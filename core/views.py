from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from .forms import CheckOutForm, CouponForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Item, Order, OrderItem, Billing, Payment, Coupon
from django.contrib import messages
import stripe
stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"


"""
class HomeListView(ListView):
    model = Item
    context_object_name = 'items'
    paginate_by = 4
    template_name = 'home.html'

"""

def HomeListView(request):
    items = Item.objects.all()
    recent = None
    try:
       slug = request.COOKIES.get('pro').split(" ")
       recent = Item.objects.filter(slug__in= slug)
    except: 
        pass   
        
    
    
    
    return render(request, 'home.html', {'items': items, 'recent':recent})


class CartView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(request, "you dont have any active oreders")
            return redirect("core:home")


class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        forms = CheckOutForm()
        couponform = CouponForm()
        context = {
            'forms': forms,
            'couponform': couponform,
            'order': order
        }
        return render(request, "checkout.html", context)

    def post(self, request, *args, **kwargs):
        form = CheckOutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get("street_address")
                appartment_address = form.cleaned_data.get(
                    "appartment_address")
                country = form.cleaned_data.get("country")
                zip = form.cleaned_data.get("zip")
                payment_option = form.cleaned_data.get("payment_option")
                # same_billing_address = form.cleaned_data.get(
                #     "same_billing_address")
                # save_info = form.cleaned_data.get("save_info")
                billing = Billing(
                    user=self.request.user,
                    street_address=street_address,
                    appartment_address=appartment_address,
                    country=country,
                    zip=zip
                )
                billing.save()
                order.billing_address = billing
                order.save()

                if payment_option == 's':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'r':
                    return redirect('core:payment', payment_option='rocket')
                elif payment_option == 'b':
                    return redirect('core:payment', payment_option='bikash')

        except ObjectDoesNotExist:
            messages.error(request, "You dont have any active oreders")
            return redirect('core:cart')


class PaymentView(View):
    def get(self, request, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        couponform = CouponForm()
        context = {
            'order': order,
            'couponform': couponform
        }
        return render(self.request, "payment.html", context)

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(user=request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.final_price())
        try:
            charge = stripe.Charge.create(
                amount=amount * 100,
                currency="usd",
                source=token,
            )

            # creating patment
            payment = Payment()
            payment.stripe_charge_id = charge.id
            payment.user = self.request.user
            payment.amount = amount
            payment.save()

            # assigning the payment to order
            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, "Successfully Created Order")
            return redirect("/")
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            messages.error(self.request, f"{e.error.message}")
            return redirect("/")
        except stripe.error.RateLimitError as e:
            messages.error(self.request, f"{e.error.message}")
            return redirect("/")
        except stripe.error.InvalidRequestError as e:
            messages.error(self.request, f"{e.error.message}")
            return redirect("/")
        except stripe.error.AuthenticationError as e:
            messages.error(self.request, f"{e.error.message}")
            return redirect("/")
        except stripe.error.APIConnectionError as e:
            messages.error(self.request, f"{e.error.message}")
            return redirect("/")
        except stripe.error.StripeError as e:
            messages.error(self.request, f"{e.error.message}")
            return redirect("/")
        except Exception as e:
            messages.error(self.request, f"{e.error.message}")
            return redirect("/")

def ProouctDetailView(request, slug):
    item = Item.objects.get(slug=slug)
    response = render(request, 'product.html', {'item' : item } )
    temp = request.COOKIES.get('pro', None)

    response.set_cookie('pro','{0} {1}'.format(temp, slug))
    print(type(request.COOKIES.get('pro')))
    return response

"""
class ProouctDetailView(DetailView):
    model = Item
    context_object_name = 'item'
    template_name = 'product.html'
    
"""

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    print(order_item)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Item was updated in your cart")
            return redirect("core:cart")
        else:
            order.items.add(order_item)
            messages.info(request, "Newly item was added in your cart")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item was added in your cart")
    return redirect("core:product", slug=slug)


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.warning(request, "Item was removed from your cart")
            return redirect("core:cart")
        else:
            # message you dont have that item in your cart
            messages.warning(request, "You dont have that item in your cart")
            return redirect("core:product", slug=slug)
    else:
        # you dont have any order
        messages.warning(request, "You dont have any order")
        return redirect("core:product", slug=slug)


def remove_single_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, "Item was updated in your cart")
                return redirect("core:cart")
            else:
                order.items.remove(order_item)
                messages.warning(request, "Item was removed from your cart")
                return redirect("core:cart")
        else:
            # message you dont have that item in your cart
            messages.warning(request, "You dont have that item in your cart")
            return redirect("core:product", slug=slug)
    else:
        # you dont have any order
        messages.warning(request, "You dont have any order")
        return redirect("core:product", slug=slug)


def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST or None)
        if form.is_valid():
            code = form.cleaned_data.get('coupon')
            print(code)
            order = Order.objects.get(
                user=request.user, ordered=False)
            coupon = Coupon.objects.get(name=code)
            try:

                order.coupon = coupon
                order.save()
                messages.error(request, "Your Coupon has been added")
                return redirect('core:checkout')

            except ObjectDoesNotExist:
                messages.error(request, "You dont have any active oreders")
                return redirect('core:cart')
