import pymongo

# Connect to MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['ecommerce']

# Get collections
collections = db.list_collection_names()
print("Collections in ecommerce database:", collections)

# Check products
products = list(db.products_product.find().limit(5))
print("\nProducts:")
for p in products:
    print(f"ID: {p.get('_id')} | Name: {p.get('name')} | Category: {p.get('category')} | Price: {p.get('price')}")

# Check users
users = list(db.users_user.find().limit(3))
print("\nUsers:")
for u in users:
    print(f"ID: {u.get('_id')} | Email: {u.get('email')} | Name: {u.get('name')}")

# Check orders
orders = list(db.orders_order.find().limit(3))
print("\nOrders:")
for o in orders:
    print(f"ID: {o.get('_id')} | User ID: {o.get('user_id')} | Status: {o.get('status')} | Total: {o.get('total_amount')}")

# Check product reviews
reviews = list(db.products_productreview.find().limit(3))
print("\nProduct Reviews:")
for r in reviews:
    print(f"ID: {r.get('_id')} | Product ID: {r.get('product_id')} | User ID: {r.get('user_id')} | Rating: {r.get('rating')}") 