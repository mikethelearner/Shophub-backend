import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

# Import the Command class from our management command
from products.management.commands.seed_products import Command

# Create an instance of the command and run it
cmd = Command()
cmd.handle()

print("Seeding completed successfully!") 