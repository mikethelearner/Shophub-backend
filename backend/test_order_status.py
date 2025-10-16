#!/usr/bin/env python
"""
Simple test script to verify order status update functionality from the backend.
This script uses Django's test client to directly test the view without making HTTP requests.
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

# Now we can import Django models
from django.test import Client
from django.contrib.auth import get_user_model
from orders.models import Order
from rest_framework.authtoken.models import Token

User = get_user_model()

def test_order_status_update():
    """Test the order status update functionality"""
    # Configuration
    order_id = 18  # Replace with a valid order ID
    new_status = 'processing'  # One of: pending, processing, shipped, delivered, cancelled, etc.
    
    # Get an admin user
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        print("No admin user found. Please create an admin user first.")
        return
    
    # Get or create token for the admin user
    token, _ = Token.objects.get_or_create(user=admin_user)
    
    # Get the order
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        print(f"Order with ID {order_id} does not exist.")
        return
    
    print(f"Testing order status update for order {order_id}")
    print(f"Current status: {order.status}")
    print(f"Current total amount: {order.total_amount}")
    
    # Create a test client
    client = Client()
    
    # Make the request
    response = client.put(
        f'/api/orders/{order_id}/status/',
        data={'status': new_status},
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Token {token.key}'
    )
    
    # Print the response
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content.decode()}")
    
    # Refresh the order from the database
    order.refresh_from_db()
    print(f"Updated status: {order.status}")
    print(f"Total amount after update: {order.total_amount}")

if __name__ == '__main__':
    test_order_status_update() 