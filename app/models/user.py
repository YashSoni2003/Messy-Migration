from app.utils.database import db_manager
from app.utils.security import password_manager

class UserService:
    @staticmethod
    def get_all_users():
        return db_manager.execute_query(
            "SELECT id, name, email, created_at FROM users WHERE is_active = 1"
        )

    @staticmethod
    def get_user_by_id(user_id):
        return db_manager.execute_single_query(
            "SELECT id, name, email, created_at FROM users WHERE id = ? AND is_active = 1",
            (user_id,)
        )

    @staticmethod
    def create_user(name, email, password):
        existing_user = db_manager.execute_single_query(
            "SELECT id FROM users WHERE email = ?", (email,)
        )
        if existing_user:
            raise ValueError("Email already exists")
        
        password_hash = password_manager.hash_password(password)
        
        with db_manager.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash)
            )
            user_id = cursor.lastrowid
        
        return UserService.get_user_by_id(user_id)

    @staticmethod
    def update_user(user_id, name=None, email=None):
        existing_user = UserService.get_user_by_id(user_id)
        if not existing_user:
            return None
        
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        
        if email is not None:
            email_check = db_manager.execute_single_query(
                "SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id)
            )
            if email_check:
                raise ValueError("Email already exists")
            
            updates.append("email = ?")
            params.append(email)
        
        if not updates:
            return existing_user
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(user_id)
        
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        db_manager.execute_update(query, tuple(params))
        
        return UserService.get_user_by_id(user_id)

    @staticmethod
    def delete_user(user_id):
        rows_affected = db_manager.execute_update(
            "UPDATE users SET is_active = 0 WHERE id = ? AND is_active = 1",
            (user_id,)
        )
        return rows_affected > 0

    @staticmethod
    def search_users_by_name(name):
        return db_manager.execute_query(
            "SELECT id, name, email, created_at FROM users WHERE name LIKE ? AND is_active = 1",
            (f"%{name}%",)
        )

    @staticmethod
    def authenticate_user(email, password):
        user = db_manager.execute_single_query(
            "SELECT id, name, email, password_hash FROM users WHERE email = ? AND is_active = 1",
            (email,)
        )
        
        if not user or not password_manager.verify_password(password, user['password_hash']):
            return None
        
   
        import secrets
        token = secrets.token_urlsafe(32)
        
        return {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'token': token 
        }
