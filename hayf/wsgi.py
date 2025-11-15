# hayf/wsgi.py
"""
WSGI config for hayf project.
Compatible with Vercel serverless deployment with auto-migration.
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Set default settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hayf.settings')

# Get WSGI application FIRST before any other operations
application = get_wsgi_application()

# Auto-setup on Vercel startup
if os.environ.get('VERCEL'):
    print("🚀 Vercel environment detected. Running setup...")
    try:
        from django.core.management import call_command
        
        # CRITICAL: Collect static files FIRST
        print("📦 Collecting static files...")
        try:
            call_command('collectstatic', '--noinput', '--clear', verbosity=1)
            print("✅ Static files collected successfully!")
        except Exception as static_error:
            print(f"⚠️  Collectstatic error: {static_error}")
        
        # Always run migrations on Vercel
        print("🔄 Running migrations...")
        try:
            call_command('migrate', '--noinput', verbosity=1)
            print("✅ Migrations completed successfully!")
        except Exception as migrate_error:
            print(f"⚠️  Migration error: {migrate_error}")
        
        # Create default superuser if doesn't exist
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin123'
                )
                print("✅ Default superuser created: admin/admin123")
            else:
                print("ℹ️  Superuser already exists")
                
        except Exception as user_error:
            print(f"⚠️  Superuser creation skipped: {user_error}")
        
        # Create sample data if needed (optional)
        try:
            from dashboard.models import Category, Product
            
            if Category.objects.count() == 0:
                # Create default category
                category = Category.objects.create(
                    name='Kopi',
                    slug='kopi',
                    description='Kategori Kopi',
                    is_active=True
                )
                print("✅ Default category created")
                
                # Create sample product
                Product.objects.create(
                    name='Kopi Arabica',
                    slug='kopi-arabica',
                    description='Kopi Arabica Premium',
                    price=50000,
                    category=category,
                    stock=100,
                    status='active',
                    is_featured=True
                )
                print("✅ Sample product created")
        except Exception as sample_error:
            print(f"ℹ️  Sample data creation skipped: {sample_error}")
            
    except Exception as e:
        print(f"❌ Setup error: {e}")
        import traceback
        print(traceback.format_exc())

# Wrap with WhiteNoise for static files
from whitenoise import WhiteNoise
application = WhiteNoise(application, root=os.path.join(os.path.dirname(__file__), '..', 'staticfiles'))
application.add_files(os.path.join(os.path.dirname(__file__), '..', 'media'), prefix='media/')

# Vercel requires 'app' variable for serverless functions
app = application