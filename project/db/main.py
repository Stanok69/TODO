import sys
from connection import DatabaseConnection
from todo_repository import TodoRepository
from auth_service import AuthService

class TodoApp:
    def __init__(self):
        self.db_connection = DatabaseConnection()
        self.conn = None
        self.auth_service = None
        self.todo_repo = None

    def start(self):
        with self.db_connection as conn:
            self.conn = conn
            self.auth_service = AuthService(conn)
            self.todo_repo = TodoRepository(conn)
            
            while True:
                if not self.auth_service.is_authenticated():
                    self._show_auth_menu()
                else:
                    self._show_main_menu()

    def _show_auth_menu(self):
        print("\n=== Welcome to Todo App ===")
        print("1. Login")
        print("2. Register")
        print("0. Exit")
        
        choice = input("Select option: ")
        
        if choice == "1":
            self._handle_login()
        elif choice == "2":
            self._handle_register()
        elif choice == "0":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid option")

    def _handle_login(self):
        username = input("Username: ")
        password = input("Password: ")
        success, message = self.auth_service.login(username, password)
        print(f"\n{message}")

    def _handle_register(self):
        username = input("Choose username: ")
        password = input("Choose password: ")
        success, message = self.auth_service.register(username, password)
        print(f"\n{message}")

    def _show_main_menu(self):
        print(f"\n=== Todo Menu ({self.auth_service.current_user['username']}) ===")
        print("1. Add task")
        print("2. Show all tasks")
        print("3. Show completed tasks")
        print("4. Toggle task status")
        print("5. Delete task")
        print("9. Logout")
        print("0. Exit")

        choice = input("Select option: ")
        user_id = self.auth_service.get_current_user_id()

        if choice == "1":
            task = input("Enter task description: ")
            if task.strip():
                self.todo_repo.add_task(user_id, task)
                print("Task added successfully")
            else:
                print("Task cannot be empty")

        elif choice == "2":
            tasks = self.todo_repo.get_all_by_user(user_id)
            self._print_tasks(tasks)

        elif choice == "3":
            tasks = self.todo_repo.get_completed_by_user(user_id)
            self._print_tasks(tasks)

        elif choice == "4":
            try:
                task_id = int(input("Enter task ID to toggle: "))
                if self.todo_repo.toggle_status(task_id, user_id):
                    print("Task status updated")
                else:
                    print("Task not found")
            except ValueError:
                print("Invalid input")

        elif choice == "5":
            try:
                task_id = int(input("Enter task ID to delete: "))
                if self.todo_repo.delete_task(task_id, user_id):
                    print("Task deleted")
                else:
                    print("Task not found")
            except ValueError:
                print("Invalid input")

        elif choice == "9":
            self.auth_service.logout()
            print("Logged out successfully")

        elif choice == "0":
            print("Goodbye!")
            sys.exit(0)

        else:
            print("Invalid option")

    def _print_tasks(self, tasks):
        if not tasks:
            print("\nNo tasks found.")
            return

        print("\nYour Tasks:")
        print("-" * 50)
        print(f"{'ID':<5} | {'Status':<10} | {'Task'}")
        print("-" * 50)
        for task_id, task_text, is_completed in tasks:
            status = "[x]" if is_completed else "[ ]"
            print(f"{task_id:<5} | {status:<10} | {task_text}")
        print("-" * 50)

if __name__ == "__main__":
    try:
        app = TodoApp()
        app.start()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
