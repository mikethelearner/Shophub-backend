import os
import django
import sys
import requests
import json

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from users.models import User

def test_admin_login():
    """Test admin login with email admin@gmail.com and password e1234"""
    try:
        # Check if the admin user exists
        if User.objects.filter(email='admin@gmail.com').exists():
            admin_user = User.objects.get(email='admin@gmail.com')
            print(f"Admin user exists: {admin_user.email}, role: {admin_user.role}, is_staff: {admin_user.is_staff}")
            
            # Test login via API
            url = 'http://localhost:8000/api/users/login/'
            data = {
                'email': 'admin@gmail.com',
                'password': 'e1234'
            }
            headers = {
                'Content-Type': 'application/json'
            }
            
            print(f"Sending login request to {url} with data: {data}")
            response = requests.post(url, data=json.dumps(data), headers=headers)
            
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
            
            try:
                print(f"Response body: {response.json()}")
            except:
                print(f"Response body (text): {response.text}")
            
            return response.status_code == 200
        else:
            print("Admin user does not exist")
            return False
    except Exception as e:
        print(f"Error testing admin login: {e}")
        return False

if __name__ == '__main__':
    test_admin_login() 