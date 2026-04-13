from django.contrib import admin
from .models import Payment, Order, OrderedFood

class OrderedFoodInline(admin.TabularInline):
    model = OrderedFood
    readonly_fields = ('fooditem', 'quantity', 'price', 'amount', 'payment')
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['order_number', 'first_name', 'last_name', 'email','total', 'payment_method', 'status', 'is_ordered', 'created_at']
    list_filter   = ['status', 'is_ordered', 'payment_method']
    search_fields = ['order_number', 'email', 'phone']
    inlines       = [OrderedFoodInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'payment_method', 'amount', 'status', 'created_at']


@admin.register(OrderedFood)
class OrderedFoodAdmin(admin.ModelAdmin):
    list_display = ['order', 'fooditem', 'quantity', 'price', 'amount']