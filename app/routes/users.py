from flask import request, jsonify
from marshmallow import ValidationError
from datetime import datetime

from app.models.user import UserService
from app.utils.validation import (
    UserCreateSchema, UserUpdateSchema, UserLoginSchema, 
    SearchSchema, validate_user_id
)
from app.utils.middleware import rate_limit, validate_json_request
from app.utils.logging import log_api_request
from app.utils.monitoring import health_checker, metrics_collector

user_create_schema = UserCreateSchema()
user_update_schema = UserUpdateSchema()
user_login_schema = UserLoginSchema()
search_schema = SearchSchema()

def error_response(message, status_code=400):
    return jsonify({
        'success': False,
        'error': message,
        'timestamp': datetime.utcnow().isoformat()
    }), status_code

def success_response(data=None, message="Success", status_code=200):
    response = {
        'success': True,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code

def register_user_routes(app):
    
    @app.route('/', methods=['GET'])
    @rate_limit(max_requests=200, window_seconds=60)
    def health_check():
        log_api_request('/', 'GET', success=True)
        return success_response(
            data={'status': 'healthy', 'service': 'User Management API'},
            message="Service is running"
        )
    
    @app.route('/health', methods=['GET'])
    @rate_limit(max_requests=100, window_seconds=60)
    def detailed_health_check():
        """Detailed health check with system monitoring."""
        try:
            health_data = health_checker.run_health_checks()
            metrics_data = metrics_collector.get_metrics_summary()
            
            response_data = {
                'health': health_data,
                'metrics': {
                    'total_requests': metrics_data['total_requests'],
                    'active_connections': metrics_data['active_connections']
                }
            }
            
            status_code = 200 if health_data['status'] == 'healthy' else 503
            log_api_request('/health', 'GET', success=(status_code == 200))
            
            return success_response(
                data=response_data,
                message=f"System is {health_data['status']}",
                status_code=status_code
            )
            
        except Exception as e:
            log_api_request('/health', 'GET', success=False, error=str(e))
            return error_response("Health check failed", 500)

    @app.route('/users', methods=['GET'])
    @rate_limit(max_requests=50, window_seconds=60)
    def get_all_users():
        try:
            users = UserService.get_all_users()
            log_api_request('/users', 'GET', success=True)
            return success_response(
                data={'users': users, 'count': len(users)},
                message=f"Retrieved {len(users)} users"
            )
        except Exception as e:
            log_api_request('/users', 'GET', success=False, error=str(e))
            return error_response("Failed to retrieve users", 500)

    @app.route('/user/<user_id>', methods=['GET'])
    @rate_limit(max_requests=100, window_seconds=60)
    def get_user(user_id):
        try:
            user_id_int = validate_user_id(user_id)
            user = UserService.get_user_by_id(user_id_int)
            
            if not user:
                log_api_request(f'/user/{user_id}', 'GET', success=False, error='User not found')
                return error_response("User not found", 404)
            
            log_api_request(f'/user/{user_id}', 'GET', user_id=user_id_int, success=True)
            return success_response(data={'user': user}, message="User retrieved successfully")
        except ValidationError as e:
            log_api_request(f'/user/{user_id}', 'GET', success=False, error=str(e))
            return error_response(f"Invalid user ID: {str(e)}", 400)
        except Exception as e:
            log_api_request(f'/user/{user_id}', 'GET', success=False, error=str(e))
            return error_response("Failed to retrieve user", 500)

    @app.route('/users', methods=['POST'])
    @rate_limit(max_requests=10, window_seconds=60)
    def create_user():
        try:
            json_error = validate_json_request()
            if json_error:
                return json_error
            
            data = user_create_schema.load(request.get_json())
            user = UserService.create_user(
                name=data['name'],
                email=data['email'],
                password=data['password']
            )
            
            log_api_request('/users', 'POST', user_id=user['id'], success=True)
            return success_response(
                data={'user': user},
                message="User created successfully",
                status_code=201
            )
        except ValidationError as e:
            log_api_request('/users', 'POST', success=False, error=f"Validation: {e.messages}")
            return error_response(f"Validation error: {e.messages}", 400)
        except ValueError as e:
            log_api_request('/users', 'POST', success=False, error=str(e))
            return error_response(str(e), 409)
        except Exception as e:
            log_api_request('/users', 'POST', success=False, error=str(e))
            return error_response("Failed to create user", 500)

    @app.route('/user/<user_id>', methods=['PUT'])
    @rate_limit(max_requests=20, window_seconds=60)
    def update_user(user_id):
        try:
            user_id_int = validate_user_id(user_id)
            
            json_error = validate_json_request()
            if json_error:
                return json_error
            
            data = user_update_schema.load(request.get_json())
            
            if not data:
                return error_response("No valid fields to update", 400)
            
            user = UserService.update_user(
                user_id=user_id_int,
                name=data.get('name'),
                email=data.get('email')
            )
            
            if not user:
                log_api_request(f'/user/{user_id}', 'PUT', success=False, error='User not found')
                return error_response("User not found", 404)
            
            log_api_request(f'/user/{user_id}', 'PUT', user_id=user_id_int, success=True)
            return success_response(data={'user': user}, message="User updated successfully")
        except ValidationError as e:
            log_api_request(f'/user/{user_id}', 'PUT', success=False, error=f"Validation: {e.messages}")
            return error_response(f"Validation error: {e.messages}", 400)
        except ValueError as e:
            log_api_request(f'/user/{user_id}', 'PUT', success=False, error=str(e))
            return error_response(str(e), 409)
        except Exception as e:
            log_api_request(f'/user/{user_id}', 'PUT', success=False, error=str(e))
            return error_response("Failed to update user", 500)

    @app.route('/user/<user_id>', methods=['DELETE'])
    @rate_limit(max_requests=10, window_seconds=60)
    def delete_user(user_id):
        try:
            user_id_int = validate_user_id(user_id)
            success = UserService.delete_user(user_id_int)
            
            if not success:
                log_api_request(f'/user/{user_id}', 'DELETE', success=False, error='User not found')
                return error_response("User not found", 404)
            
            log_api_request(f'/user/{user_id}', 'DELETE', user_id=user_id_int, success=True)
            return success_response(message="User deleted successfully")
        except ValidationError as e:
            log_api_request(f'/user/{user_id}', 'DELETE', success=False, error=str(e))
            return error_response(f"Invalid user ID: {str(e)}", 400)
        except Exception as e:
            log_api_request(f'/user/{user_id}', 'DELETE', success=False, error=str(e))
            return error_response("Failed to delete user", 500)

    @app.route('/search', methods=['GET'])
    @rate_limit(max_requests=30, window_seconds=60)
    def search_users():
        try:
            name = request.args.get('name')
            if not name:
                return error_response("Query parameter 'name' is required", 400)
            
            search_data = search_schema.load({'name': name})
            users = UserService.search_users_by_name(search_data['name'])
            
            log_api_request('/search', 'GET', success=True)
            return success_response(
                data={'users': users, 'count': len(users)},
                message=f"Found {len(users)} users matching '{search_data['name']}'"
            )
        except ValidationError as e:
            log_api_request('/search', 'GET', success=False, error=f"Validation: {e.messages}")
            return error_response(f"Validation error: {e.messages}", 400)
        except Exception as e:
            log_api_request('/search', 'GET', success=False, error=str(e))
            return error_response("Failed to search users", 500)

    @app.route('/login', methods=['POST'])
    @rate_limit(max_requests=5, window_seconds=60)  
    def login():
        try:
            json_error = validate_json_request()
            if json_error:
                return json_error
            
            data = user_login_schema.load(request.get_json())
            auth_result = UserService.authenticate_user(
                email=data['email'],
                password=data['password']
            )
            
            if not auth_result:
                log_api_request('/login', 'POST', success=False, error='Invalid credentials')
                return error_response("Invalid email or password", 401)
            
            log_api_request('/login', 'POST', user_id=auth_result['id'], success=True)
            return success_response(
                data={
                    'user': {
                        'id': auth_result['id'],
                        'name': auth_result['name'],
                        'email': auth_result['email']
                    },
                    'token': auth_result['token']
                },
                message="Login successful"
            )
        except ValidationError as e:
            log_api_request('/login', 'POST', success=False, error=f"Validation: {e.messages}")
            return error_response(f"Validation error: {e.messages}", 400)
        except Exception as e:
            log_api_request('/login', 'POST', success=False, error=str(e))
            return error_response("Login failed", 500)
