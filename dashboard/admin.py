from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from .models import Category, Product, Customer, Order, OrderItem, Review, Coupon


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 1
    fields = ('product', 'quantity', 'price', 'total')
    readonly_fields = ('total',)


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'product_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        count = obj.products.count()
        return format_html(f'<span style="background:#4CAF50;color:white;padding:3px 8px;border-radius:3px;">{count}</span>')
    product_count.short_description = 'Produk'


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ('name', 'category', 'price_display', 'stock_status', 'rating_display', 'is_featured', 'status')
    list_filter = ('category', 'status', 'is_featured')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'rating', 'total_reviews')
    prepopulated_fields = {'slug': ('name',)}
    
    def price_display(self, obj):
        return format_html(f'<strong>Rp {obj.price:,.0f}</strong>')
    price_display.short_description = 'Harga'
    
    def stock_status(self, obj):
        if obj.stock > 20:
            color, status = '#4CAF50', 'Stok Aman'
        elif obj.stock > 0:
            color, status = '#FF9800', 'Stok Rendah'
        else:
            color, status = '#F44336', 'Habis'
        return format_html(f'<span style="background:{color};color:white;padding:3px 8px;border-radius:3px;">{status} ({obj.stock})</span>')
    stock_status.short_description = 'Stok'
    
    def rating_display(self, obj):
        stars = '★' * int(obj.rating) + '☆' * (5 - int(obj.rating))
        return format_html(f'{stars} ({obj.rating})')
    rating_display.short_description = 'Rating'


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ('get_full_name', 'get_email', 'phone', 'total_orders', 'total_spent_display', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'total_orders', 'total_spent')
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Nama'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    
    def total_spent_display(self, obj):
        return format_html(f'<strong>Rp {obj.total_spent:,.0f}</strong>')
    total_spent_display.short_description = 'Total Belanja'


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ('order_number', 'customer_name', 'status_badge', 'payment_status_badge', 'total_display', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'customer__user__first_name')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    def customer_name(self, obj):
        return obj.customer.user.get_full_name() or obj.customer.user.username
    customer_name.short_description = 'Pelanggan'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#FF9800', 'processing': '#2196F3', 'shipped': '#9C27B0',
            'delivered': '#4CAF50', 'cancelled': '#F44336', 'refunded': '#607D8B',
        }
        color = colors.get(obj.status, '#999')
        return format_html(f'<span style="background:{color};color:white;padding:3px 8px;border-radius:3px;">{obj.get_status_display()}</span>')
    status_badge.short_description = 'Status'
    
    def payment_status_badge(self, obj):
        colors = {'pending': '#FF9800', 'completed': '#4CAF50', 'failed': '#F44336', 'refunded': '#607D8B'}
        color = colors.get(obj.payment_status, '#999')
        return format_html(f'<span style="background:{color};color:white;padding:3px 8px;border-radius:3px;">{obj.get_payment_status_display()}</span>')
    payment_status_badge.short_description = 'Pembayaran'
    
    def total_display(self, obj):
        return format_html(f'<strong>Rp {obj.total:,.0f}</strong>')
    total_display.short_description = 'Total'


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ('product', 'customer_name', 'rating_stars', 'is_verified_purchase', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'created_at')
    search_fields = ('product__name', 'customer__user__first_name', 'title')
    readonly_fields = ('created_at', 'updated_at')
    
    def customer_name(self, obj):
        return obj.customer.user.get_full_name() or obj.customer.user.username
    customer_name.short_description = 'Pelanggan'
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(f'{stars}')
    rating_stars.short_description = 'Rating'


@admin.register(Coupon)
class CouponAdmin(ModelAdmin):
    list_display = ('code', 'discount_display', 'is_active', 'usage_display', 'valid_until')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code', 'description')
    readonly_fields = ('created_at', 'current_uses')
    
    def discount_display(self, obj):
        if obj.discount_type == 'percentage':
            return format_html(f'<strong>{obj.discount_value}%</strong>')
        return format_html(f'<strong>Rp {obj.discount_value:,.0f}</strong>')
    discount_display.short_description = 'Diskon'
    
    def usage_display(self, obj):
        if obj.max_uses:
            return format_html(f'{obj.current_uses}/{obj.max_uses}')
        return format_html(f'{obj.current_uses}/Unlimited')
    usage_display.short_description = 'Penggunaan'