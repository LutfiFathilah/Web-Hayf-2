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

# Get WSGI application
application = get_wsgi_application()

# Auto-migrate on Vercel startup
if os.environ.get('VERCEL'):
    print("🚀 Vercel environment detected. Running migrations...")
    try:
        from django.core.management import call_command
        from django.db import connection
        from django.db.utils import OperationalError
        
        # Always run migrations on Vercel (SQLite resets on each cold start)
        print("📦 Running migrations...")
        call_command('migrate', '--noinput', verbosity=1)
        print("✅ Migrations completed successfully!")
        
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
        print(f"❌ Migration error: {e}")
        import traceback
        print(traceback.format_exc())

# Vercel requires 'app' variable for serverless functions
app = application