import os
import pymongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB URI from environment
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/ecommerce')

# Connect to MongoDB
client = pymongo.MongoClient(MONGODB_URI)
db_name = MONGODB_URI.split('/')[-1]
db = client[db_name]

# Check if the index exists and drop it
collection = db['knox_authtoken']
indexes = collection.index_information()

print("Current indexes:", indexes)

# Look for the salt_1 index directly
if 'salt_1' in indexes:
    print("Found salt_1 index. Dropping...")
    collection.drop_index('salt_1')
    print("Index dropped successfully.")
else:
    print("No salt_1 index found.")

# Verify indexes after dropping
print("Indexes after update:", collection.index_information()) 