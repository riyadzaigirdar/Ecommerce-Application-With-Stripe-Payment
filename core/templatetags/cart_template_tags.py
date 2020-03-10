from django import template
from core.models import Order
register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        order = Order.objects.filter(user=user, ordered=False)
        if order:
            order = order[0]
            return order.items.count()
    else:
        return 0
