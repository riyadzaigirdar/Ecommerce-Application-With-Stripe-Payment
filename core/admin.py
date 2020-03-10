from django.contrib import admin
from .models import Item, Order, OrderItem, Billing, Payment, Coupon


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'start_date', 'ordered_date',
                    'ordered', 'billing_address')
    list_display_links = ('id', 'user')
    list_filter = ('ordered',)
    list_per_page = 25


admin.site.register(Item)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Billing)
admin.site.register(Payment)
admin.site.register(Coupon)
