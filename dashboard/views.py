from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
import logging
import json
from django.db.models import Q, Avg, Count
from django.core.mail import send_mail, BadHeaderError

from .models import Product, Category, Order, OrderItem, Customer, Review, Coupon
from .forms import RegisterForm, LoginForm, CustomerProfileForm, ReviewForm, ContactForm

from django.http import HttpResponse
import sys

def health_check(request):
    """Simple health check endpoint"""
    return HttpResponse(f"""
        <h1>✅ Django is Working!</h1>
        <ul>
            <li>Python version: {sys.version}</li>
            <li>Django settings module: {request.META.get('DJANGO_SETTINGS_MODULE')}</li>
            <li>Debug mode: {settings.DEBUG}</li>
            <li>User authenticated: {request.user.is_authenticated}</li>
        </ul>
    """)

# Setup logger
logger = logging.getLogger(__name__)

# ============================================
# MIDTRANS INTEGRATION
# ============================================
try:
    import midtransclient
    MIDTRANS_AVAILABLE = True
except ImportError:
    MIDTRANS_AVAILABLE = False
    logger.warning("midtransclient not installed. Payment gateway will not work.")


def get_midtrans_client():
    """Get Midtrans Snap client instance"""
    if not MIDTRANS_AVAILABLE:
        logger.error("Midtrans client not available")
        return None
    
    try:
        snap = midtransclient.Snap(
            is_production=getattr(settings, 'MIDTRANS_IS_PRODUCTION', False),
            server_key=getattr(settings, 'MIDTRANS_SERVER_KEY', ''),
            client_key=getattr(settings, 'MIDTRANS_CLIENT_KEY', '')
        )
        logger.info("Midtrans client initialized successfully")
        return snap
    except Exception as e:
        logger.error(f"Error initializing Midtrans client: {str(e)}")
        return None


def create_midtrans_transaction(order):
    """Create Midtrans transaction and get Snap token"""
    snap = get_midtrans_client()
    if not snap:
        logger.error("Failed to get Midtrans client")
        return {'success': False, 'error': 'Midtrans not configured'}
    
    try:
        # Build transaction details
        transaction_details = {
            'order_id': str(order.order_number),
            'gross_amount': int(order.total),
        }
        
        logger.info(f"Creating transaction for order: {order.order_number}, amount: {order.total}")
        
        # Build item details
        item_details = []
        for item in order.items.all():
            item_details.append({
                'id': str(item.product.id if item.product else 0),
                'price': int(item.price),
                'quantity': item.quantity,
                'name': item.product_name[:50],
            })
        
        # Add shipping & tax
        if order.shipping_cost > 0:
            item_details.append({
                'id': 'SHIPPING',
                'price': int(order.shipping_cost),
                'quantity': 1,
                'name': 'Ongkos Kirim',
            })
        
        if order.tax > 0:
            item_details.append({
                'id': 'TAX',
                'price': int(order.tax),
                'quantity': 1,
                'name': 'Pajak (10%)',
            })
        
        if order.discount > 0:
            item_details.append({
                'id': 'DISCOUNT',
                'price': -int(order.discount),
                'quantity': 1,
                'name': 'Diskon',
            })
        
        # Customer details
        customer_details = {
            'first_name': order.customer.user.first_name or 'Customer',
            'last_name': order.customer.user.last_name or '',
            'email': order.customer.user.email,
            'phone': order.customer.phone or '081234567890',
            'billing_address': {
                'first_name': order.customer.user.first_name or 'Customer',
                'last_name': order.customer.user.last_name or '',
                'email': order.customer.user.email,
                'phone': order.customer.phone or '081234567890',
                'address': order.shipping_address[:200],
                'city': order.shipping_city,
                'postal_code': order.shipping_postal_code,
                'country_code': 'IDN'
            },
            'shipping_address': {
                'first_name': order.customer.user.first_name or 'Customer',
                'last_name': order.customer.user.last_name or '',
                'email': order.customer.user.email,
                'phone': order.customer.phone or '081234567890',
                'address': order.shipping_address[:200],
                'city': order.shipping_city,
                'postal_code': order.shipping_postal_code,
                'country_code': 'IDN'
            }
        }
        
        # Transaction parameters
        param = {
            'transaction_details': transaction_details,
            'item_details': item_details,
            'customer_details': customer_details,
            'enabled_payments': [
                'credit_card', 'bca_va', 'bni_va', 'bri_va', 'permata_va',
                'other_va', 'gopay', 'shopeepay', 'qris', 'cimb_clicks',
                'bca_klikbca', 'bca_klikpay', 'bri_epay', 'echannel',
                'mandiri_clickpay', 'indomaret', 'alfamart', 'akulaku', 'kredivo'
            ],
            'credit_card': {
                'secure': True,
                'bank': 'bca',
                'installment': {
                    'required': False,
                    'terms': {
                        'bni': [3, 6, 12],
                        'mandiri': [3, 6, 12],
                        'cimb': [3],
                        'bca': [3, 6, 12],
                        'mega': [3, 6, 12]
                    }
                }
            },
            'callbacks': {
                'finish': getattr(settings, 'MIDTRANS_FINISH_URL', 'http://localhost:8000/payment/finish/'),
            }
        }
        
        # Create transaction
        transaction = snap.create_transaction(param)
        
        logger.info(f"Midtrans transaction created successfully for order {order.order_number}")
        
        return {
            'success': True,
            'snap_token': transaction['token'],
            'redirect_url': transaction['redirect_url'],
        }
        
    except Exception as e:
        logger.error(f"Error creating Midtrans transaction: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'error': str(e)
        }


def process_midtrans_notification(notification_data):
    """Process Midtrans notification and update order"""
    try:
        order_id = notification_data.get('order_id')
        transaction_status = notification_data.get('transaction_status')
        fraud_status = notification_data.get('fraud_status', 'accept')
        payment_type = notification_data.get('payment_type')
        
        logger.info(f"Processing notification for order {order_id}: {transaction_status}")
        
        try:
            order = Order.objects.get(order_number=order_id)
        except Order.DoesNotExist:
            logger.error(f"Order not found: {order_id}")
            return False
        
        # Update order status based on transaction status
        if transaction_status == 'capture':
            if fraud_status == 'accept':
                order.payment_status = 'completed'
                order.status = 'processing'
                order.payment_method = payment_type
            else:
                order.payment_status = 'failed'
                order.status = 'cancelled'
                
        elif transaction_status == 'settlement':
            order.payment_status = 'completed'
            order.status = 'processing'
            order.payment_method = payment_type
            
        elif transaction_status == 'pending':
            order.payment_status = 'pending'
            order.status = 'pending'
            order.payment_method = payment_type
            
        elif transaction_status in ['deny', 'expire', 'cancel']:
            order.payment_status = 'failed'
            order.status = 'cancelled'
            
        elif transaction_status == 'refund':
            order.payment_status = 'refunded'
            order.status = 'refunded'
        
        order.save()
        logger.info(f"Order {order_id} updated: {order.payment_status}/{order.status}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing notification: {str(e)}")
        return False


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_cart_count(request):
    """Helper untuk get cart count"""
    try:
        cart = request.session.get('cart', {})
        return len(cart)
    except Exception as e:
        logger.error(f"Error getting cart count: {str(e)}")
        return 0


def get_cart_data(request):
    """Helper untuk get cart data lengkap"""
    try:
        cart = request.session.get('cart', {})
        cart_items = []
        subtotal = Decimal('0')
        
        for product_id, item in list(cart.items()):
            try:
                product = Product.objects.get(id=product_id, status='active')
                quantity = item['quantity']
                price = Decimal(item['price'])
                item_total = price * quantity
                subtotal += item_total
                
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'price': price,
                    'total': item_total
                })
            except Product.DoesNotExist:
                del cart[product_id]
                request.session.modified = True
            except Exception as e:
                logger.error(f"Error processing cart item {product_id}: {str(e)}")
        
        return {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'count': len(cart_items)
        }
    except Exception as e:
        logger.error(f"Error getting cart data: {str(e)}")
        return {
            'cart_items': [],
            'subtotal': Decimal('0'),
            'count': 0
        }


# ============================================
# PUBLIC VIEWS
# ============================================

def index(request):
    """Landing page"""
    try:
        featured_products = Product.objects.filter(
            status='active', 
            is_featured=True
        ).select_related('category')[:6]
        
        categories = Category.objects.filter(is_active=True)[:4]
        
        context = {
            'featured_products': featured_products,
            'categories': categories,
            'cart_count': get_cart_count(request),
        }
        return render(request, 'dashboard/LandingPage.html', context)
    except Exception as e:
        logger.error(f"Error in index view: {str(e)}")
        messages.error(request, 'Terjadi kesalahan. Silakan coba lagi.')
        return render(request, 'dashboard/LandingPage.html', {'cart_count': 0})


def products(request):
    """Katalog produk dengan pagination"""
    try:
        products_list = Product.objects.filter(status='active').select_related('category')
        
        # Search
        search_query = request.GET.get('search', '').strip()
        if search_query:
            products_list = products_list.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        
        # Filter by category
        category_slug = request.GET.get('category', '')
        if category_slug:
            products_list = products_list.filter(category__slug=category_slug)
        
        # Sort
        sort_by = request.GET.get('sort', '-created_at')
        valid_sorts = ['name', '-name', 'price', '-price', '-created_at', '-rating', 'stock']
        if sort_by in valid_sorts:
            products_list = products_list.order_by(sort_by)
        
        # Pagination
        paginator = Paginator(products_list, 12)
        page = request.GET.get('page', 1)
        
        try:
            products_page = paginator.page(page)
        except PageNotAnInteger:
            products_page = paginator.page(1)
        except EmptyPage:
            products_page = paginator.page(paginator.num_pages)
        
        categories = Category.objects.filter(is_active=True)
        
        context = {
            'products': products_page,
            'categories': categories,
            'search_query': search_query,
            'selected_category': category_slug,
            'selected_sort': sort_by,
            'cart_count': get_cart_count(request),
            'total_products': products_list.count(),
        }
        return render(request, 'dashboard/katalog.html', context)
    except Exception as e:
        logger.error(f"Error in products view: {str(e)}")
        messages.error(request, 'Terjadi kesalahan saat memuat produk.')
        return redirect('dashboard:index')


def product_detail(request, slug):
    """Detail produk"""
    try:
        product = get_object_or_404(Product, slug=slug, status='active')
        reviews = product.reviews.select_related('customer__user').order_by('-created_at')[:10]
        related_products = Product.objects.filter(
            category=product.category, 
            status='active'
        ).exclude(id=product.id)[:4]
        
        has_purchased = False
        user_review = None
        if request.user.is_authenticated:
            try:
                customer = Customer.objects.get(user=request.user)
                has_purchased = OrderItem.objects.filter(
                    order__customer=customer,
                    product=product,
                    order__payment_status='completed'
                ).exists()
                user_review = Review.objects.filter(product=product, customer=customer).first()
            except Customer.DoesNotExist:
                pass
        
        review_stats = reviews.aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id'),
            five_star=Count('id', filter=Q(rating=5)),
            four_star=Count('id', filter=Q(rating=4)),
            three_star=Count('id', filter=Q(rating=3)),
            two_star=Count('id', filter=Q(rating=2)),
            one_star=Count('id', filter=Q(rating=1)),
        )
        
        context = {
            'product': product,
            'reviews': reviews,
            'related_products': related_products,
            'has_purchased': has_purchased,
            'user_review': user_review,
            'review_stats': review_stats,
            'cart_count': get_cart_count(request),
        }
        return render(request, 'dashboard/product_detail.html', context)
    except Exception as e:
        logger.error(f"Error in product_detail view for slug {slug}: {str(e)}")
        messages.error(request, 'Produk tidak ditemukan.')
        return redirect('dashboard:products')


def about(request):
    """Tentang kami"""
    context = {'cart_count': get_cart_count(request)}
    return render(request, 'dashboard/about.html', context)


def kontak(request):
    """Halaman kontak dengan fungsi kirim email"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Ambil data dari form
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Buat email body yang rapi
            email_subject = f'[Kopi Hayf Contact] {subject}'
            email_body = f"""
Pesan Baru dari Website Kopi Hayf
{'='*50}

Dari: {name}
Email: {email}
Subjek: {subject}

Pesan:
{message}

{'='*50}
Email ini dikirim otomatis dari form kontak website Kopi Hayf.
Balas langsung ke email: {email}
            """
            
            try:
                # Kirim email
                send_mail(
                    subject=email_subject,
                    message=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                
                logger.info(f"Contact email sent from {email}")
                
                messages.success(
                    request, 
                    'Pesan Anda telah terkirim! Kami akan segera menghubungi Anda dalam 1x24 jam.'
                )
                
                return redirect('dashboard:kontak')
                
            except Exception as e:
                logger.error(f"Error sending contact email: {str(e)}")
                messages.error(
                    request, 
                    'Gagal mengirim pesan. Silakan coba lagi atau hubungi kami melalui WhatsApp.'
                )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'cart_count': get_cart_count(request),
    }
    return render(request, 'dashboard/kontak.html', context)


# ============================================
# AUTHENTICATION
# ============================================

def masuk(request):
    """Login page"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Selamat datang, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'dashboard:index')
                return redirect(next_url)
    else:
        form = LoginForm()
    
    context = {
        'form': form,
        'cart_count': get_cart_count(request),
    }
    return render(request, 'dashboard/masuk.html', context)


def registrasi(request):
    """Registration page"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registrasi berhasil! Selamat datang di Kopi Hayf.')
            return redirect('dashboard:index')
    else:
        form = RegisterForm()
    
    context = {
        'form': form,
        'cart_count': get_cart_count(request),
    }
    return render(request, 'dashboard/registrasi.html', context)


def logout_view(request):
    """Logout"""
    logout(request)
    messages.success(request, 'Anda telah berhasil logout.')
    return redirect('dashboard:index')


# ============================================
# CART MANAGEMENT
# ============================================

def view_cart(request):
    """View shopping cart"""
    try:
        cart_data = get_cart_data(request)
        subtotal = cart_data['subtotal']
        tax = Decimal('0')  # Pajak dihapus
        shipping_cost = Decimal('1000')  # Ongkir Rp 1.000
        
        coupon_code = request.session.get('coupon_code')
        discount = Decimal('0')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code.upper())
                if coupon.is_valid():
                    discount = coupon.calculate_discount(subtotal)
            except:
                pass
        
        total = subtotal + tax + shipping_cost - discount
        
        context = {
            'cart_items': cart_data['cart_items'],
            'subtotal': subtotal,
            'tax': tax,
            'shipping_cost': shipping_cost,
            'discount': discount,
            'total': total,
            'cart_count': cart_data['count'],
        }
        return render(request, 'dashboard/cart.html', context)
    except Exception as e:
        logger.error(f"Error in view_cart: {str(e)}")
        messages.error(request, 'Terjadi kesalahan')
        return redirect('dashboard:index')


@require_POST
def add_to_cart(request, product_id):
    """Add product to cart via AJAX - Returns JSON response"""
    try:
        product = get_object_or_404(Product, id=product_id, status='active')
        quantity = int(request.POST.get('quantity', 1))
        
        # Validation
        if quantity < 1:
            return JsonResponse({
                'success': False,
                'error': 'Jumlah produk tidak valid'
            }, status=400)
        
        if quantity > product.stock:
            return JsonResponse({
                'success': False,
                'error': f'Stok tidak mencukupi. Stok tersedia: {product.stock}'
            }, status=400)
        
        # Get or create cart in session
        cart = request.session.get('cart', {})
        
        # Add or update product in cart
        if str(product_id) in cart:
            old_quantity = cart[str(product_id)]['quantity']
            new_quantity = old_quantity + quantity
            
            # Check if new quantity exceeds stock
            if new_quantity > product.stock:
                return JsonResponse({
                    'success': False,
                    'error': f'Stok tidak mencukupi. Anda sudah memiliki {old_quantity} di keranjang. Stok tersedia: {product.stock}'
                }, status=400)
            
            cart[str(product_id)]['quantity'] = new_quantity
        else:
            cart[str(product_id)] = {
                'quantity': quantity,
                'price': str(product.price),
                'name': product.name,
                'image': product.image.url if product.image else ''
            }
        
        # Save cart to session
        request.session['cart'] = cart
        request.session.modified = True
        
        # Calculate cart count
        cart_count = sum(item['quantity'] for item in cart.values())
        
        # Return success JSON response
        return JsonResponse({
            'success': True,
            'message': f'{product.name} berhasil ditambahkan ke keranjang!',
            'cart_count': cart_count,
            'product': {
                'id': product.id,
                'name': product.name,
                'quantity': quantity
            }
        })
        
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Produk tidak ditemukan'
        }, status=404)
    except ValueError:
        return JsonResponse({
            'success': False,
            'error': 'Format quantity tidak valid'
        }, status=400)
    except Exception as e:
        logger.error(f"Error adding to cart: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Terjadi kesalahan. Silakan coba lagi.'
        }, status=500)


@require_POST
def update_cart(request, product_id):
    """Update cart quantity"""
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        
        cart = request.session.get('cart', {})
        
        if str(product_id) in cart:
            if quantity > 0:
                cart[str(product_id)]['quantity'] = quantity
            else:
                del cart[str(product_id)]
            
            request.session['cart'] = cart
            request.session.modified = True
            
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False, 'error': 'Product not in cart'})
    except Exception as e:
        logger.error(f"Error updating cart: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


def remove_from_cart(request, product_id):
    """Remove product from cart"""
    try:
        cart = request.session.get('cart', {})
        
        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session['cart'] = cart
            request.session.modified = True
            messages.success(request, 'Produk berhasil dihapus dari keranjang')
        
        return redirect('dashboard:view-cart')
    except Exception as e:
        logger.error(f"Error removing from cart: {str(e)}")
        messages.error(request, 'Terjadi kesalahan')
        return redirect('dashboard:view-cart')


def clear_cart(request):
    """Clear cart completely"""
    try:
        request.session['cart'] = {}
        request.session.modified = True
        messages.success(request, 'Keranjang berhasil dikosongkan')
    except Exception as e:
        logger.error(f"Error clearing cart: {str(e)}")
        messages.error(request, 'Terjadi kesalahan')
    return redirect('dashboard:view-cart')


def apply_coupon(request):
    """Apply coupon code"""
    if request.method == 'POST':
        try:
            code = request.POST.get('coupon_code', '').strip().upper()
            
            if not code:
                messages.error(request, 'Masukkan kode kupon')
                return redirect('dashboard:view-cart')
            
            try:
                coupon = Coupon.objects.get(code=code)
                
                if not coupon.is_valid():
                    messages.error(request, 'Kupon tidak valid atau sudah kadaluarsa')
                    return redirect('dashboard:view-cart')
                
                request.session['coupon_code'] = code
                request.session.modified = True
                
                messages.success(request, f'Kupon "{code}" berhasil diterapkan!')
                
            except Coupon.DoesNotExist:
                messages.error(request, 'Kode kupon tidak ditemukan')
                
        except Exception as e:
            logger.error(f"Error applying coupon: {str(e)}")
            messages.error(request, 'Terjadi kesalahan')
    
    return redirect('dashboard:view-cart')


# ============================================
# CHECKOUT & PAYMENT
# ============================================

@login_required
def checkout(request):
    """Checkout page with Midtrans integration"""
    try:
        customer = get_object_or_404(Customer, user=request.user)
        cart_data = get_cart_data(request)
        
        if not cart_data['cart_items']:
            messages.warning(request, 'Keranjang belanja Anda kosong')
            return redirect('dashboard:products')
        
        # Calculate totals
        subtotal = cart_data['subtotal']
        tax = Decimal('0')  # Pajak dihapus
        shipping_cost = Decimal('1000')  # Ongkir Rp 1.000
        
        # Apply coupon
        coupon_code = request.session.get('coupon_code')
        discount = Decimal('0')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code.upper())
                if coupon.is_valid():
                    discount = coupon.calculate_discount(subtotal)
            except:
                pass
        
        total = subtotal + tax + shipping_cost - discount
        
        context = {
            'customer': customer,
            'cart_items': cart_data['cart_items'],
            'subtotal': subtotal,
            'tax': tax,
            'shipping_cost': shipping_cost,
            'discount': discount,
            'total': total,
            'cart_count': cart_data['count'],
            'MIDTRANS_CLIENT_KEY': getattr(settings, 'MIDTRANS_CLIENT_KEY', ''),
        }
        return render(request, 'dashboard/checkout.html', context)
    except Exception as e:
        logger.error(f"Error in checkout: {str(e)}")
        messages.error(request, 'Terjadi kesalahan')
        return redirect('dashboard:view-cart')


@login_required
@require_POST
def create_payment(request):
    """Create Midtrans payment - AJAX endpoint - FIXED VERSION"""
    import traceback
    
    try:
        logger.info(f"=== Payment Create Request Started ===")
        logger.info(f"User: {request.user.username}")
        logger.info(f"Method: {request.method}")
        logger.info(f"Content-Type: {request.META.get('CONTENT_TYPE')}")
        
        # Get customer
        try:
            customer = Customer.objects.get(user=request.user)
            logger.info(f"Customer found: {customer}")
        except Customer.DoesNotExist:
            logger.error(f"Customer not found for user: {request.user.username}")
            return JsonResponse({
                'success': False,
                'error': 'Profil pelanggan tidak ditemukan. Silakan lengkapi profil Anda terlebih dahulu.'
            }, status=404)
        
        # Get cart from session
        cart = request.session.get('cart', {})
        logger.info(f"Cart items: {len(cart)}")
        
        if not cart:
            logger.warning("Cart is empty")
            return JsonResponse({
                'success': False,
                'error': 'Keranjang belanja kosong'
            }, status=400)
        
        # Get shipping info from POST data
        shipping_address = request.POST.get('shipping_address', '').strip()
        shipping_city = request.POST.get('shipping_city', '').strip()
        shipping_state = request.POST.get('shipping_state', '').strip()
        shipping_postal_code = request.POST.get('shipping_postal_code', '').strip()
        shipping_country = request.POST.get('shipping_country', 'Indonesia').strip()
        notes = request.POST.get('notes', '').strip()
        
        logger.info(f"Shipping info - City: {shipping_city}, State: {shipping_state}")
        
        # Validate required fields
        if not all([shipping_address, shipping_city, shipping_state, shipping_postal_code]):
            missing_fields = []
            if not shipping_address: missing_fields.append('Alamat')
            if not shipping_city: missing_fields.append('Kota')
            if not shipping_state: missing_fields.append('Provinsi')
            if not shipping_postal_code: missing_fields.append('Kode Pos')
            
            logger.warning(f"Missing fields: {missing_fields}")
            return JsonResponse({
                'success': False,
                'error': f'Mohon lengkapi: {", ".join(missing_fields)}'
            }, status=400)
        
        # Calculate totals and validate stock
        subtotal = Decimal('0')
        cart_items = []
        
        for product_id, item in cart.items():
            try:
                product = Product.objects.get(id=product_id, status='active')
                quantity = int(item['quantity'])
                
                # Check stock
                if product.stock < quantity:
                    logger.warning(f"Insufficient stock for {product.name}: {product.stock} < {quantity}")
                    return JsonResponse({
                        'success': False,
                        'error': f'Stok {product.name} tidak mencukupi. Tersedia: {product.stock}'
                    }, status=400)
                
                price = Decimal(str(item['price']))
                item_total = price * quantity
                subtotal += item_total
                
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'price': price,
                    'total': item_total
                })
                
                logger.info(f"Cart item: {product.name} x{quantity} = Rp {item_total}")
                
            except Product.DoesNotExist:
                logger.error(f"Product not found: {product_id}")
                return JsonResponse({
                    'success': False,
                    'error': f'Produk dengan ID {product_id} tidak ditemukan'
                }, status=400)
            except (ValueError, KeyError) as e:
                logger.error(f"Invalid cart data for product {product_id}: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': 'Data keranjang tidak valid'
                }, status=400)
        
        # Calculate additional costs
        tax = Decimal('0')  # No tax
        shipping_cost = Decimal('1000')  # Fixed shipping Rp 1.000
        
        # Apply coupon if exists
        discount = Decimal('0')
        coupon_code = request.session.get('coupon_code')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code.upper())
                if coupon.is_valid():
                    discount = coupon.calculate_discount(subtotal)
                    logger.info(f"Coupon applied: {coupon_code} - Discount: Rp {discount}")
                else:
                    logger.warning(f"Coupon invalid: {coupon_code}")
            except Coupon.DoesNotExist:
                logger.warning(f"Coupon not found: {coupon_code}")
        
        total = subtotal + tax + shipping_cost - discount
        
        logger.info(f"Order calculation - Subtotal: {subtotal}, Tax: {tax}, Shipping: {shipping_cost}, Discount: {discount}, Total: {total}")
        
        # Create Order
        try:
            order = Order.objects.create(
                customer=customer,
                shipping_address=shipping_address,
                shipping_city=shipping_city,
                shipping_state=shipping_state,
                shipping_postal_code=shipping_postal_code,
                shipping_country=shipping_country,
                subtotal=subtotal,
                tax=tax,
                shipping_cost=shipping_cost,
                discount=discount,
                total=total,
                notes=notes,
                status='pending',
                payment_status='pending'
            )
            logger.info(f"Order created: {order.order_number}")
        except Exception as e:
            logger.error(f"Failed to create order: {str(e)}")
            logger.error(traceback.format_exc())
            return JsonResponse({
                'success': False,
                'error': f'Gagal membuat pesanan: {str(e)}'
            }, status=500)
        
        # Create Order Items & reduce stock
        try:
            for cart_item in cart_items:
                product = cart_item['product']
                quantity = cart_item['quantity']
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    quantity=quantity,
                    price=cart_item['price']
                )
                
                # Reduce stock
                product.stock -= quantity
                product.save()
                
                logger.info(f"Order item created: {product.name} x{quantity}, stock reduced to {product.stock}")
        except Exception as e:
            logger.error(f"Failed to create order items: {str(e)}")
            logger.error(traceback.format_exc())
            # Rollback: delete order
            order.delete()
            return JsonResponse({
                'success': False,
                'error': f'Gagal membuat detail pesanan: {str(e)}'
            }, status=500)
        
        # Create Midtrans transaction
        logger.info("Creating Midtrans transaction...")
        payment_result = create_midtrans_transaction(order)
        
        if payment_result['success']:
            logger.info(f"Midtrans transaction created successfully. Snap token: {payment_result['snap_token'][:20]}...")
            
            # Clear cart and coupon
            request.session['cart'] = {}
            if 'coupon_code' in request.session:
                del request.session['coupon_code']
            request.session.modified = True
            
            logger.info("Cart cleared")
            logger.info("=== Payment Create Request Completed Successfully ===")
            
            return JsonResponse({
                'success': True,
                'snap_token': payment_result['snap_token'],
                'redirect_url': payment_result['redirect_url'],
                'order_number': order.order_number
            })
        else:
            logger.error(f"Midtrans transaction failed: {payment_result.get('error')}")
            
            # Rollback: restore stock and delete order
            try:
                for item in order.items.all():
                    if item.product:
                        item.product.stock += item.quantity
                        item.product.save()
                        logger.info(f"Stock restored for {item.product.name}")
                order.delete()
                logger.info("Order deleted (rollback)")
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {str(rollback_error)}")
            
            return JsonResponse({
                'success': False,
                'error': f"Gagal membuat transaksi pembayaran: {payment_result.get('error', 'Unknown error')}"
            }, status=500)
            
    except Exception as e:
        logger.error(f"Unexpected error in create_payment: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': f'Terjadi kesalahan sistem: {str(e)}'
        }, status=500)


@csrf_exempt
@require_POST
def payment_notification(request):
    """Midtrans webhook notification"""
    try:
        notification_data = json.loads(request.body.decode('utf-8'))
        logger.info(f"Midtrans notification: {notification_data}")
        
        success = process_midtrans_notification(notification_data)
        
        if success:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error'}, status=400)
            
    except Exception as e:
        logger.error(f"Error in notification: {str(e)}")
        return JsonResponse({'status': 'error'}, status=500)


@login_required
def payment_finish(request):
    """Payment finish page"""
    try:
        order_id = request.GET.get('order_id')
        transaction_status = request.GET.get('transaction_status')
        
        if order_id:
            customer = Customer.objects.get(user=request.user)
            order = Order.objects.get(order_number=order_id, customer=customer)
            
            # Get latest status from Midtrans
            snap = get_midtrans_client()
            if snap:
                try:
                    status_data = snap.transactions.status(order_id)
                    process_midtrans_notification(status_data)
                    order.refresh_from_db()
                except:
                    pass
            
            context = {
                'order': order,
                'transaction_status': transaction_status or order.payment_status,
                'cart_count': 0,
            }
            return render(request, 'dashboard/payment_finish.html', context)
        else:
            messages.warning(request, 'Informasi pesanan tidak lengkap')
            return redirect('dashboard:order-list')
            
    except Exception as e:
        logger.error(f"Error in payment_finish: {str(e)}")
        messages.error(request, 'Terjadi kesalahan')
        return redirect('dashboard:order-list')


# ============================================
# ORDER MANAGEMENT
# ============================================

@login_required
def order_list(request):
    """Order history"""
    try:
        customer = get_object_or_404(Customer, user=request.user)
        orders = Order.objects.filter(customer=customer).prefetch_related('items__product').order_by('-created_at')
        
        paginator = Paginator(orders, 10)
        page = request.GET.get('page', 1)
        
        try:
            orders_page = paginator.page(page)
        except PageNotAnInteger:
            orders_page = paginator.page(1)
        except EmptyPage:
            orders_page = paginator.page(paginator.num_pages)
        
        context = {
            'orders': orders_page,
            'cart_count': get_cart_count(request),
        }
        return render(request, 'dashboard/order_list.html', context)
    except Exception as e:
        logger.error(f"Error in order_list: {str(e)}")
        messages.error(request, 'Terjadi kesalahan')
        return redirect('dashboard:index')


@login_required
def order_detail(request, pk):
    """Order detail"""
    try:
        customer = get_object_or_404(Customer, user=request.user)
        order = get_object_or_404(Order, pk=pk, customer=customer)
        
        context = {
            'order': order,
            'cart_count': get_cart_count(request),
        }
        return render(request, 'dashboard/order_detail.html', context)
    except Exception as e:
        logger.error(f"Error in order_detail: {str(e)}")
        messages.error(request, 'Order tidak ditemukan')
        return redirect('dashboard:order-list')


# ============================================
# USER PROFILE
# ============================================

@login_required
def profile(request):
    """User profile"""
    try:
        customer, created = Customer.objects.get_or_create(user=request.user)
        recent_orders = customer.orders.all().order_by('-created_at')[:5]
        recent_reviews = customer.reviews.select_related('product').order_by('-created_at')[:5]
        
        context = {
            'customer': customer,
            'recent_orders': recent_orders,
            'recent_reviews': recent_reviews,
            'cart_count': get_cart_count(request),
            'profile_customer': customer,
        }
        return render(request, 'dashboard/profile.html', context)
    except Exception as e:
        logger.error(f"Error in profile: {str(e)}")
        messages.error(request, 'Terjadi kesalahan')
        return redirect('dashboard:index')


@login_required
def profile_edit(request):
    """Edit profile"""
    try:
        customer, created = Customer.objects.get_or_create(user=request.user)
        
        if request.method == 'POST':
            form = CustomerProfileForm(request.POST, request.FILES, instance=customer)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profil berhasil diperbarui!')
                return redirect('dashboard:profile')
            else:
                for error in form.errors.values():
                    messages.error(request, error)
        else:
            form = CustomerProfileForm(instance=customer)
        
        context = {
            'form': form,
            'cart_count': get_cart_count(request),
        }
        return render(request, 'dashboard/profile_edit.html', context)
    except Exception as e:
        logger.error(f"Error in profile_edit: {str(e)}")
        messages.error(request, 'Terjadi kesalahan')
        return redirect('dashboard:profile')


# ============================================
# REVIEWS
# ============================================

@login_required
@require_POST
def add_review(request, product_id):
    """Add or update review"""
    try:
        product = get_object_or_404(Product, id=product_id)
        customer, created = Customer.objects.get_or_create(user=request.user)
        
        rating = int(request.POST.get('rating', 0))
        title = request.POST.get('title', '').strip()
        comment = request.POST.get('comment', '').strip()
        
        if rating < 1 or rating > 5:
            messages.error(request, 'Rating harus antara 1-5 bintang')
            return redirect('dashboard:product-detail', slug=product.slug)
        
        if not comment:
            messages.error(request, 'Komentar tidak boleh kosong')
            return redirect('dashboard:product-detail', slug=product.slug)
        
        is_verified = OrderItem.objects.filter(
            order__customer=customer,
            product=product,
            order__payment_status='completed'
        ).exists()
        
        review, created_new = Review.objects.update_or_create(
            product=product,
            customer=customer,
            defaults={
                'rating': rating,
                'title': title,
                'comment': comment,
                'is_verified_purchase': is_verified
            }
        )
        
        if created_new:
            messages.success(request, 'Review berhasil ditambahkan!')
        else:
            messages.success(request, 'Review berhasil diperbarui!')
        
        return redirect('dashboard:product-detail', slug=product.slug)
    except ValueError:
        messages.error(request, 'Rating tidak valid')
        return redirect('dashboard:products')
    except Exception as e:
        logger.error(f"Error adding review: {str(e)}")
        messages.error(request, 'Terjadi kesalahan')
        return redirect('dashboard:products')