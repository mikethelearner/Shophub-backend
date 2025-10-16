# E-Commerce Platform with Django and MongoDB

This is an e-commerce platform built with Django backend and MongoDB database, with a React frontend.

## Features

- User authentication and authorization
- Product browsing and searching
- Shopping cart functionality
- Order management
- Admin dashboard for product and order management

## Tech Stack

- **Backend**: Django with Django REST Framework
- **Database**: MongoDB (using Djongo)
- **Frontend**: React with TypeScript
- **Styling**: Tailwind CSS

## Setup Instructions

### Prerequisites

- Python 3.8+
- MongoDB
- Node.js and npm

### Backend Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   MONGODB_URI=mongodb://localhost:27017/ecommerce
   ```

4. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

### Frontend Setup

The frontend is located in the `Frontend` directory and can be set up as follows:

1. Install dependencies:
   ```
   cd Frontend
   npm install
   ```

2. Start the development server:
   ```
   npm run dev
   ```

## API Endpoints

- `/api/users/` - User registration and authentication
- `/api/products/` - Product listing and details
- `/api/orders/` - Order creation and management
- `/api/cart/` - Shopping cart operations

## License

This project is licensed under the MIT License. 