# Code Refactoring Challenge

## Overview
You've inherited a legacy user management API that works but has significant issues. Your task is to refactor and improve this codebase while maintaining its functionality.

## Getting Started

### Prerequisites
- Python 3.8+ installed
- 3 hours of uninterrupted time

### Setup (Should take < 5 minutes)
```bash
# Clone/download this repository
# Navigate to the assignment directory
cd messy-migration

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python init_db.py

# Start the application
python app.py

# The API will be available at http://localhost:5000
```

### Testing the Application
The application provides these endpoints:
- `GET /` - Health check
- `GET /users` - Get all users
- `GET /user/<id>` - Get specific user
- `POST /users` - Create new user
- `PUT /user/<id>` - Update user
- `DELETE /user/<id>` - Delete user
- `GET /search?name=<name>` - Search users by name
- `POST /login` - User login



## Questions?

If you have questions about the requirements, please email [anand@retainsure.com] within the first 30 minutes of starting.

---

Remember: We're not looking for perfection. We want to see how you approach real-world code problems, prioritize improvements, and communicate your decisions.
