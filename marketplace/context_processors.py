# context processors is used when we want global context for html pages for ex - if navbar is present in all pages and somehow we have cart which should be there in all pages then context_processors is needed
from .models import Cart
from menu.models import FoodItem

def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user = request.user)
            if cart_items:
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
            else:
                cart_count = 0
        except:
            cart_count = 0
    return dict(cart_count = cart_count)
