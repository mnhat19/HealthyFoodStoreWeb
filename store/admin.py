from django.contrib import admin
from .models import Product, HomePage, Customer, Payment, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('category',)
    search_fields = ('name', 'description', 'ingredients')
    list_editable = ('price', 'stock')

@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    filter_horizontal = ('bestsellers', 'new_products')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'total_paid')
    search_fields = ('user__username', 'phone_number')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_number')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('id', 'customer', 'status', 'total_amount', 'created_at')
#     list_filter = ('status', 'created_at')
#     inlines = [OrderItemInline]
#     search_fields = ('customer__user__username',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__user__username',)

    actions = ['confirm_orders']

    def confirm_orders(self, request, queryset):
        for order in queryset.filter(status='unpaid'):
            order.status = 'confirmed'
            order.save()
            # Trừ hàng tồn kho
            for item in order.orderitem_set.all():
                item.product.stock -= item.quantity
                item.product.save()
            # Cộng tiền đã thanh toán cho khách hàng
            order.customer.total_paid += order.total_amount
            order.customer.save()
            # Gửi thông báo cho khách hàng (có thể thêm email nếu cần)
        self.message_user(request, "Selected orders have been confirmed.")
    confirm_orders.short_description = "Confirm selected orders"
