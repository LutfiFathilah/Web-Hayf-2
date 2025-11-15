from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models import Avg, Sum
from decimal import Decimal
import uuid


class TimeStampedModel(models.Model):
    """Abstract base model with timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class Category(TimeStampedModel):
    """Product category model"""
    name = models.CharField(max_length=200, unique=True, verbose_name='Nama Kategori')
    slug = models.SlugField(unique=True, max_length=220)
    description = models.TextField(blank=True, verbose_name='Deskripsi')
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='Gambar')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    display_order = models.IntegerField(default=0, verbose_name='Urutan Tampil')

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_product_count(self):
        """Get active product count"""
        return self.products.filter(status='active').count()
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('dashboard:products') + f'?category={self.slug}'


class Product(TimeStampedModel):
    """Product model"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('discontinued', 'Discontinued'),
        ('out_of_stock', 'Out of Stock'),
    ]

    name = models.CharField(max_length=255, verbose_name='Nama Produk')
    slug = models.SlugField(unique=True, max_length=280)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Kategori')
    description = models.TextField(verbose_name='Deskripsi')
    short_description = models.CharField(max_length=200, blank=True, verbose_name='Deskripsi Singkat')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Harga Jual')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0, verbose_name='Harga Modal')
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True, verbose_name='Harga Coret')
    
    # Inventory
    stock = models.IntegerField(validators=[MinValueValidator(0)], default=0, verbose_name='Stok')
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name='SKU')
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Berat (gram)')
    
    # Media
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Gambar Utama')
    
    # Status & Features
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Status')
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name='Rating')
    total_reviews = models.IntegerField(default=0, verbose_name='Total Review')
    is_featured = models.BooleanField(default=False, verbose_name='Produk Unggulan')
    is_new = models.BooleanField(default=False, verbose_name='Produk Baru')
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, verbose_name='Meta Title')
    meta_description = models.TextField(blank=True, verbose_name='Meta Description')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_featured']),
        ]
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name

    def clean(self):
        """Validate model data"""
        if self.price and self.cost_price and self.price < self.cost_price:
            raise ValidationError('Harga jual tidak boleh lebih rendah dari harga modal')
        
        if self.compare_price and self.compare_price < self.price:
            raise ValidationError('Harga coret harus lebih tinggi dari harga jual')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Auto-generate SKU if not provided
        if not self.sku:
            self.sku = f'PRD-{uuid.uuid4().hex[:8].upper()}'
        
        # Update status based on stock
        if self.stock == 0 and self.status == 'active':
            self.status = 'out_of_stock'
        elif self.stock > 0 and self.status == 'out_of_stock':
            self.status = 'active'
        
        self.clean()
        super().save(*args, **kwargs)

    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock > 0 and self.status == 'active'

    def get_discount_percentage(self):
        """Calculate discount percentage"""
        if self.compare_price and self.compare_price > self.price:
            discount = ((self.compare_price - self.price) / self.compare_price) * 100
            return round(discount)
        return 0
    
    def get_profit_margin(self):
        """Calculate profit margin"""
        if self.cost_price > 0:
            margin = ((self.price - self.cost_price) / self.price) * 100
            return round(margin, 2)
        return 0
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('dashboard:product-detail', kwargs={'slug': self.slug})
    
    def update_rating(self):
        """Update product rating from reviews"""
        reviews = self.reviews.all()
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            self.rating = round(avg_rating, 1)
            self.total_reviews = reviews.count()
        else:
            self.rating = 0
            self.total_reviews = 0
        self.save(update_fields=['rating', 'total_reviews'])


class Customer(TimeStampedModel):
    """Customer profile model"""
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Format: '+999999999'. Minimal 9 digit, maksimal 15 digit."
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, verbose_name='Telepon')
    
    # Address
    address = models.TextField(blank=True, verbose_name='Alamat')
    city = models.CharField(max_length=100, blank=True, verbose_name='Kota')
    state = models.CharField(max_length=100, blank=True, verbose_name='Provinsi')
    postal_code = models.CharField(max_length=20, blank=True, verbose_name='Kode Pos')
    country = models.CharField(max_length=100, blank=True, default='Indonesia', verbose_name='Negara')
    
    # Profile
    profile_image = models.ImageField(upload_to='customers/', blank=True, null=True, verbose_name='Foto Profil')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='Tanggal Lahir')
    gender = models.CharField(max_length=10, choices=[('pria', 'Pria'), ('wanita', 'Wanita')], blank=True, verbose_name='Jenis Kelamin')
    
    # Stats
    total_orders = models.IntegerField(default=0, verbose_name='Total Pesanan')
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Total Belanja')
    is_verified = models.BooleanField(default=False, verbose_name='Terverifikasi')
    
    # Newsletter
    newsletter_subscribed = models.BooleanField(default=False, verbose_name='Berlangganan Newsletter')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"
    
    def get_full_address(self):
        """Get formatted full address"""
        parts = [self.address, self.city, self.state, self.postal_code, self.country]
        return ', '.join(filter(None, parts))
    
    def update_stats(self):
        """Update customer statistics"""
        completed_orders = self.orders.filter(payment_status='completed')
        self.total_orders = completed_orders.count()
        self.total_spent = completed_orders.aggregate(total=Sum('total'))['total'] or Decimal('0')
        self.save(update_fields=['total_orders', 'total_spent'])


class Order(TimeStampedModel):
    """Order model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    order_number = models.CharField(max_length=50, unique=True, editable=False, verbose_name='Nomor Order')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders', verbose_name='Pelanggan')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Status Pesanan')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name='Status Pembayaran')
    payment_method = models.CharField(max_length=50, blank=True, verbose_name='Metode Pembayaran')
    
    # Shipping Address
    shipping_address = models.TextField(verbose_name='Alamat Pengiriman')
    shipping_city = models.CharField(max_length=100, verbose_name='Kota')
    shipping_state = models.CharField(max_length=100, verbose_name='Provinsi')
    shipping_postal_code = models.CharField(max_length=20, verbose_name='Kode Pos')
    shipping_country = models.CharField(max_length=100, default='Indonesia', verbose_name='Negara')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Subtotal')
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Pajak')
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Ongkos Kirim')
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Diskon')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Total')
    
    # Additional Info
    notes = models.TextField(blank=True, verbose_name='Catatan')
    tracking_number = models.CharField(max_length=100, blank=True, verbose_name='Nomor Resi')
    courier = models.CharField(max_length=50, blank=True, verbose_name='Kurir')
    
    # Timestamps
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='Tanggal Dikirim')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='Tanggal Diterima')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['customer']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
        ]
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            random_part = uuid.uuid4().hex[:6].upper()
            self.order_number = f"ORD-{timestamp}-{random_part}"
        super().save(*args, **kwargs)
    
    def get_total_items(self):
        """Get total number of items in order"""
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0
    
    def can_cancel(self):
        """Check if order can be cancelled"""
        return self.status in ['pending', 'processing']
    
    def get_status_display_color(self):
        """Get color for status badge"""
        colors = {
            'pending': 'warning',
            'processing': 'info',
            'shipped': 'primary',
            'delivered': 'success',
            'cancelled': 'danger',
            'refunded': 'secondary',
        }
        return colors.get(self.status, 'secondary')


class OrderItem(models.Model):
    """Order item model"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Order')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name='Produk')
    product_name = models.CharField(max_length=255, default='', blank=True, verbose_name='Nama Produk')  # Store name in case product is deleted
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Jumlah')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Harga')
    total = models.DecimalField(max_digits=12, decimal_places=2, editable=False, verbose_name='Total')

    class Meta:
        unique_together = ('order', 'product')
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    def save(self, *args, **kwargs):
        # Store product name
        if self.product and not self.product_name:
            self.product_name = self.product.name
        
        # Calculate total
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)


class Review(TimeStampedModel):
    """Product review model"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='Produk')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reviews', verbose_name='Pelanggan')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='Rating')
    title = models.CharField(max_length=200, verbose_name='Judul')
    comment = models.TextField(verbose_name='Komentar')
    is_verified_purchase = models.BooleanField(default=False, verbose_name='Pembelian Terverifikasi')
    helpful_count = models.IntegerField(default=0, verbose_name='Helpful Count')
    is_approved = models.BooleanField(default=True, verbose_name='Disetujui')

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'customer')
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.rating} stars by {self.customer}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update product rating
        self.product.update_rating()


class Coupon(TimeStampedModel):
    """Coupon/discount code model"""
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ]
    
    code = models.CharField(max_length=50, unique=True, verbose_name='Kode Kupon')
    description = models.TextField(blank=True, verbose_name='Deskripsi')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, verbose_name='Tipe Diskon')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Nilai Diskon')
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Minimal Pembelian')
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Maksimal Diskon')
    max_uses = models.IntegerField(null=True, blank=True, verbose_name='Maksimal Penggunaan')
    current_uses = models.IntegerField(default=0, verbose_name='Penggunaan Saat Ini')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    valid_from = models.DateTimeField(verbose_name='Berlaku Dari')
    valid_until = models.DateTimeField(verbose_name='Berlaku Sampai')

    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def is_valid(self):
        """Check if coupon is valid"""
        now = timezone.now()
        is_time_valid = self.valid_from <= now <= self.valid_until
        is_usage_valid = self.max_uses is None or self.current_uses < self.max_uses
        return self.is_active and is_time_valid and is_usage_valid
    
    def calculate_discount(self, subtotal):
        """Calculate discount amount"""
        if not self.is_valid():
            return Decimal('0')
        
        if subtotal < self.min_purchase:
            return Decimal('0')
        
        if self.discount_type == 'percentage':
            discount = (subtotal * self.discount_value) / 100
            if self.max_discount and discount > self.max_discount:
                discount = self.max_discount
        else:
            discount = self.discount_value
        
        return min(discount, subtotal)
    
    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        super().save(*args, **kwargs)