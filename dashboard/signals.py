from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import Review, Order, Customer


@receiver([post_save, post_delete], sender=Review)
def update_product_rating(sender, instance, **kwargs):
    """Auto update product rating when review added/updated/deleted"""
    product = instance.product
    reviews = product.reviews.all()
    
    if reviews.exists():
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        product.rating = round(avg_rating, 1)
        product.total_reviews = reviews.count()
    else:
        product.rating = 0
        product.total_reviews = 0
    
    product.save(update_fields=['rating', 'total_reviews'])


@receiver(post_save, sender=Order)
def update_customer_stats(sender, instance, created, **kwargs):
    """Auto update customer stats when order created/updated"""
    customer = instance.customer
    completed_orders = customer.orders.filter(payment_status='completed')
    
    customer.total_orders = completed_orders.count()
    customer.total_spent = sum(order.total for order in completed_orders)
    customer.save(update_fields=['total_orders', 'total_spent'])