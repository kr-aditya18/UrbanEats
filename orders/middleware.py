from orders.models import OrderedFood
from django.db.models import Sum


def get_vendor_ids_from_order(order):
    return order.vendors.values_list('id', flat=True)


class VendorOrderMiddleware:
    """
    Lesson 209/210: Custom middleware that attaches
    a helper method to the request for getting
    vendor-specific totals from an order.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Attach helper function to request
        request.get_vendor_subtotal = self._get_vendor_subtotal
        response = self.get_response(request)
        return response

    @staticmethod
    def _get_vendor_subtotal(order, vendor):
        """
        Lesson 210: Returns the subtotal for a specific vendor
        within a given order.
        """
        result = OrderedFood.objects.filter(
            order=order,
            fooditem__vendor=vendor,
        ).aggregate(total=Sum('amount'))['total']
        return result or 0