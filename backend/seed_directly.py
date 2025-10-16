import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from products.models import Product
from django.utils import timezone

# Delete all existing products
Product.objects.all().delete()
print('Deleted all existing products')

# Sample products data
products = [
    {
        'name': 'Wireless Bluetooth Headphones',
        'description': 'High-quality wireless headphones with noise cancellation and long battery life.',
        'price': 79.99,
        'category': 'electronics',
        'manufacturer': 'SoundTech',
        'stock': 50,
        'rating': 4.5,
    },
    {
        'name': 'Smart Fitness Tracker',
        'description': 'Track your steps, heart rate, sleep, and more with this waterproof fitness band.',
        'price': 49.99,
        'category': 'electronics',
        'manufacturer': 'FitLife',
        'stock': 75,
        'rating': 4.3,
    },
    {
        'name': 'Cotton T-Shirt Pack',
        'description': 'Set of 3 comfortable cotton t-shirts in various colors.',
        'price': 24.99,
        'category': 'clothing',
        'manufacturer': 'ComfortWear',
        'stock': 100,
        'rating': 4.0,
    },
    {
        'name': 'Stainless Steel Water Bottle',
        'description': 'Eco-friendly, double-walled insulated water bottle that keeps drinks cold for 24 hours or hot for 12 hours.',
        'price': 19.99,
        'category': 'home',
        'manufacturer': 'EcoLife',
        'stock': 120,
        'rating': 4.7,
    },
    {
        'name': 'Bestselling Novel',
        'description': 'The latest bestselling fiction novel that everyone is talking about.',
        'price': 14.99,
        'category': 'books',
        'manufacturer': 'PageTurner Publishing',
        'stock': 200,
        'rating': 4.8,
    },
    {
        'name': 'Organic Face Moisturizer',
        'description': 'Natural, organic face cream with anti-aging properties.',
        'price': 29.99,
        'category': 'beauty',
        'manufacturer': 'NaturalGlow',
        'stock': 60,
        'rating': 4.6,
    },
    {
        'name': 'Yoga Mat',
        'description': 'Non-slip, eco-friendly yoga mat with carrying strap.',
        'price': 34.99,
        'category': 'sports',
        'manufacturer': 'ZenFitness',
        'stock': 40,
        'rating': 4.4,
    },
    {
        'name': 'Building Blocks Set',
        'description': 'Creative building blocks set for children ages 3+, develops motor skills and imagination.',
        'price': 27.99,
        'category': 'toys',
        'manufacturer': 'KidCreations',
        'stock': 55,
        'rating': 4.9,
    },
]

# Create products
for product_data in products:
    product = Product.objects.create(
        name=product_data['name'],
        description=product_data['description'],
        price=product_data['price'],
        category=product_data['category'],
        manufacturer=product_data['manufacturer'],
        stock=product_data['stock'],
        rating=product_data['rating'],
        is_active=True,
    )
    print(f'Created product: {product.name}')

print('Successfully seeded products') 