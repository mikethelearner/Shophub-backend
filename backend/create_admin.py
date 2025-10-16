import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from users.models import User

def create_admin_user():
    """Create an admin user with email admin@gmail.com and password e1234"""
    try:
        # Check if the admin user already exists
        if User.objects.filter(email='admin@gmail.com').exists():
            admin_user = User.objects.get(email='admin@gmail.com')
            admin_user.set_password('e1234')
            admin_user.role = 'admin'
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            print("Admin user updated with password 'e1234'")
        else:
            # Create a new admin user
            User.objects.create_superuser(
                email='admin@gmail.com',
                name='Admin User',
                password='e1234',
                phone='1234567890'
            )
            print("Admin user created with email 'admin@gmail.com' and password 'e1234'")
        
        return True
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return False

if __name__ == '__main__':
    create_admin_user() 