# E-commerce Application with Django and React

This is an e-commerce application built with Django (backend) and React (frontend). The application is containerized using Docker for easy deployment on any platform, including Windows.

## Features

- User authentication and authorization
- Product browsing and searching
- Shopping cart functionality
- Order management
- Product reviews
- Admin dashboard for product management
- MongoDB database integration

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your machine
  - For Windows: Make sure WSL 2 is enabled
  - For Mac: Both Intel and Apple Silicon are supported

## Running the Application with Docker

### Quick Start

For Linux/Mac users:
```bash
./start-app.sh
```

For Windows users, double-click the `start-app.bat` file or run it from the command prompt.

### Production Mode

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Start the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```
   
   The `-d` flag runs the containers in detached mode (in the background).

3. Access the application:
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000/api
   - Admin interface: http://localhost:8000/admin

4. Default admin credentials:
   - Email: admin@gmail.com
   - Password: admin123

### Development Mode

For development with hot-reloading:

1. Start the application in development mode:
   ```bash
   docker-compose -f docker-compose.dev.yml up
   ```

2. Access the application:
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000/api

## Windows-Specific Instructions

If you're using Windows, follow these additional steps:

1. Make sure Docker Desktop is installed with WSL 2 backend enabled
2. In Docker Desktop settings, ensure that the "Use the WSL 2 based engine" option is checked
3. If you encounter file permission issues, try running Docker Desktop as administrator

## Development

If you want to make changes to the application:

1. Make your changes to the code
2. Rebuild the Docker images:
   ```bash
   docker-compose build
   ```
   
   Or for development mode:
   ```bash
   docker-compose -f docker-compose.dev.yml build
   ```
   
3. Restart the containers:
   ```bash
   docker-compose up -d
   ```
   
   Or for development mode:
   ```bash
   docker-compose -f docker-compose.dev.yml up
   ```

## Stopping the Application

To stop the application:
```bash
docker-compose down
```

Or for development mode:
```bash
docker-compose -f docker-compose.dev.yml down
```

To remove all data volumes (this will delete all data):
```bash
docker-compose down -v
```

## Troubleshooting

If you encounter any issues:

1. Check the logs:
   ```bash
   docker-compose logs
   ```

2. Check specific service logs:
   ```bash
   docker-compose logs backend
   docker-compose logs frontend
   docker-compose logs mongodb
   ```

3. Restart the services:
   ```bash
   docker-compose restart
   ```

4. Common issues and solutions:
   - **MongoDB connection issues**: Make sure MongoDB is running and healthy
   - **Frontend can't connect to backend**: Check that the VITE_API_URL environment variable is set correctly
   - **Windows path issues**: Make sure you're using the correct path format for Windows

## License

This project is licensed under the MIT License - see the LICENSE file for details. 