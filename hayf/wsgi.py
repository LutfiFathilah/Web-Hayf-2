# hayf/wsgi.py
"""
WSGI config for hayf project.
Compatible with Vercel serverless deployment.
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Set default settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hayf.settings')

# Get WSGI application
application = get_wsgi_application()

# Auto-migrate on Vercel startup (for SQLite only)
if os.environ.get('VERCEL'):
    try:
        from django.core.management import call_command
        from django.db import connection
        
        # Check if tables exist
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
            if len(tables) < 5:  # If tables don't exist, run migrate
                print("⚠️  Database tables not found. Running migrations...")
                call_command('migrate', '--noinput', verbosity=0)
                print("✅ Migrations completed!")
                
                # Create superuser if needed
                from django.contrib.auth import get_user_model
                User = get_user_model()
                if not User.objects.filter(username='admin').exists():
                    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
                    print("✅ Superuser created: admin/admin123")
        except Exception as e:
            print(f"⚠️  Migration check error: {e}")
            # Try to migrate anyway
            call_command('migrate', '--noinput', verbosity=0)
            
    except Exception as e:
        print(f"❌ Migration error: {e}")

# Vercel requires 'app' variable for serverless functions
app = application