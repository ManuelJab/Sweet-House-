#!/bin/bash
# ============================================
# Stiman Dessert - Entrypoint Script
# ============================================
set -e

echo "🍰 Stiman Dessert - Starting..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
python << END
import os, time, sys
import psycopg2

db_host = os.environ.get('DB_HOST', 'localhost')
db_port = os.environ.get('DB_PORT', '5432')
db_name = os.environ.get('DB_NAME', 'sweet_house')
db_user = os.environ.get('DB_USER', 'postgres')
db_pass = os.environ.get('DB_PASSWORD', '')

retries = 30
while retries > 0:
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_pass,
            sslmode='require'
        )
        conn.close()
        print("✅ Database is ready!")
        break
    except psycopg2.OperationalError as e:
        retries -= 1
        if retries == 0:
            print(f"❌ Could not connect to database: {e}")
            print("⚠️  Proceeding anyway (Supabase might need SSL or different config)...")
            break
        print(f"⏳ Database not ready, retrying... ({retries} attempts left)")
        time.sleep(2)
END

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting Gunicorn server..."
exec gunicorn stimandessert.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --worker-class gthread \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
