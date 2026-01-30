from user_repository import UserRepository

class AuthService:
    def __init__(self, connection):
        self.user_repo = UserRepository(connection)
        self.current_user = None

    def register(self, username, password):
        if self.user_repo.get_user_by_username(username):
            return False, "Username already exists"
        
        try:
            self.user_repo.create_user(username, password)
            return True, "Registration successful"
        except Exception as e:
            return False, f"Registration failed: {str(e)}"

    def login(self, username, password):
        user = self.user_repo.get_user_by_username(username)
        if not user:
            return False, "Invalid username or password"
        
        user_id, db_username, db_hash = user
        if self.user_repo.verify_password(db_hash, password):
            self.current_user = {"id": user_id, "username": db_username}
            return True, "Login successful"
        
        return False, "Invalid username or password"

    def logout(self):
        self.current_user = None

    def is_authenticated(self):
        return self.current_user is not None

    def get_current_user_id(self):
        return self.current_user["id"] if self.current_user else None
