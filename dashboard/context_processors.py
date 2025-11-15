"""
Context Processors untuk Dashboard App
Menambahkan variables yang dibutuhkan ke semua templates
"""

from django.conf import settings


def site_settings(request):
    """
    Context processor untuk menambahkan settings dan cart info ke template
    """
    # Get cart count from session
    cart_count = 0
    if hasattr(request, 'session'):
        cart = request.session.get('cart', {})
        if cart:
            cart_count = sum(item['quantity'] for item in cart.values())
    
    return {
        'MIDTRANS_CLIENT_KEY': getattr(settings, 'MIDTRANS_CLIENT_KEY', ''),
        'MIDTRANS_IS_PRODUCTION': getattr(settings, 'MIDTRANS_IS_PRODUCTION', False),
        'cart_count': cart_count,
    }