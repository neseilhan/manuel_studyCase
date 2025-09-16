# User Management API

## Overview
A FastAPI-based User Management system with RESTful endpoints for user operations.

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd qa-assignment
Install dependencies

bash
Kodu kopyala
pip install -r requirements.txt
Start the API server

bash
Kodu kopyala
uvicorn main:app --reload --host 0.0.0.0 --port 8000
Seed sample data (optional)

bash
Kodu kopyala
python seed_data.py
Documentation
Assignment Instructions: See QA_ASSIGNMENT.md

API Documentation: http://localhost:8000/docs

Alternative Docs: http://localhost:8000/redoc

API Endpoints
Public Endpoints
GET / - API information

POST /users - Create new user

GET /users - List users

GET /users/{id} - Get user by ID

POST /login - User authentication

Protected Endpoints
PUT /users/{id} - Update user

DELETE /users/{id} - Delete user

Additional Endpoints
GET /users/search - Search users

GET /stats - System statistics

GET /health - Health check

Project Structure
bash
Kodu kopyala
qa-assignment/
├── main.py              # FastAPI application
├── seed_data.py         # Sample data generator
├── requirements.txt     # Python dependencies
├── QA_ASSIGNMENT.md     # Assignment details
└── README.md            # This file
For QA Engineers
Your task is to:
 
Test all API endpoints thoroughly

Identify and document bugs

Write automated tests

Create comprehensive test reports

See QA_ASSIGNMENT.md for detailed instructions.

Sample Credentials
After running seed_data.py:

Username: john_doe, Password: password123

Username: jane_smith, Password: securepass456

