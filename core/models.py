from django.conf import settings
from django.db import models
from django.shortcuts import reverse
import time

Category_Choices = (
    ('VG', 'Vegetables'),
    ('M', 'Meat'),
    ('G', 'Grocery')
)
Label_Choices = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger'),
)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=Category_Choices, max_length=2)
    label = models.CharField(choices=Label_Choices, max_length=1)
    slug = models.SlugField()
    text = models.TextField()
    image = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("core:add_to_cart", kwargs={"slug": self.slug})

    def remove_from_cart_url(self):
        return reverse("core:remove_from_cart", kwargs={"slug": self.slug})
    
    def slow_runner(self):
        time.sleep(5)

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_discount_price(self):
        try:
            return self.quantity * self.item.discount_price
        except TypeError:
            return 0

    def get_total_price(self):
        return self.quantity * self.item.price

    def amount_saved(self):
        if self.get_total_discount_price() == 0:
            return self.get_total_discount_price()
        else:
            return self.get_total_price() - self.get_total_discount_price()

    def get_final_price(self):
        if self.get_total_discount_price() != 0:
            return self.get_total_discount_price()
        else:
            return self.get_total_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey(
        'Billing', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def final_price(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        try:
            total -= self.coupon.amount
        except:
            pass
        return total


class Billing(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    appartment_address = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    name = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.name
