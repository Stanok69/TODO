import sys

import bcrypt
from sqlalchemy import select

from database import init_db
from database import SessionLocal
from models import Todo, User


class TodoApp:
    def __init__(self):
        init_db()
        self.session = SessionLocal()
        self.current_user = None

    def start(self):
        while True:
            if not self.current_user:
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
            self._close()
            sys.exit(0)
        else:
            print("Invalid option")

    def _handle_login(self):
        username = input("Username: ")
        password = input("Password: ")
        user = self.session.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()
        if not user:
            print("\nInvalid username or password")
            return
        ok = bcrypt.checkpw(
            password.encode("utf-8"),
            user.password_hash.encode("utf-8"),
        )
        if not ok:
            print("\nInvalid username or password")
            return
        self.current_user = user
        print("\nLogin successful")

    def _handle_register(self):
        username = input("Choose username: ")
        password = input("Choose password: ")
        existing = self.session.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()
        if existing:
            print("\nUsername already exists")
            return
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")
        user = User(username=username, password_hash=password_hash)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        print("\nRegistration successful")

    def _show_main_menu(self):
        print(f"\n=== Todo Menu ({self.current_user.username}) ===")
        print("1. Add task")
        print("2. Show all tasks")
        print("3. Show completed tasks")
        print("4. Toggle task status")
        print("5. Delete task")
        print("9. Logout")
        print("0. Exit")

        choice = input("Select option: ")

        if choice == "1":
            task = input("Enter task description: ")
            if task.strip():
                todo = Todo(user_id=self.current_user.id, task=task, is_completed=False)
                self.session.add(todo)
                self.session.commit()
                print("Task added successfully")
            else:
                print("Task cannot be empty")

        elif choice == "2":
            tasks = self._get_tasks()
            self._print_tasks(tasks)

        elif choice == "3":
            tasks = self._get_tasks(only_completed=True)
            self._print_tasks(tasks)

        elif choice == "4":
            try:
                task_id = int(input("Enter task ID to toggle: "))
                todo = self._get_task_by_id(task_id)
                if not todo:
                    print("Task not found")
                    return
                todo.is_completed = not todo.is_completed
                self.session.commit()
                print("Task status updated")
            except ValueError:
                print("Invalid input")

        elif choice == "5":
            try:
                task_id = int(input("Enter task ID to delete: "))
                todo = self._get_task_by_id(task_id)
                if not todo:
                    print("Task not found")
                    return
                self.session.delete(todo)
                self.session.commit()
                print("Task deleted")
            except ValueError:
                print("Invalid input")

        elif choice == "9":
            self.current_user = None
            print("Logged out successfully")

        elif choice == "0":
            print("Goodbye!")
            self._close()
            sys.exit(0)

        else:
            print("Invalid option")

    def _get_tasks(self, only_completed=False):
        stmt = select(Todo).where(Todo.user_id == self.current_user.id)
        if only_completed:
            stmt = stmt.where(Todo.is_completed.is_(True))
        stmt = stmt.order_by(Todo.id)
        return list(self.session.execute(stmt).scalars().all())

    def _get_task_by_id(self, task_id):
        return self.session.execute(
            select(Todo).where(
                Todo.id == task_id,
                Todo.user_id == self.current_user.id,
            )
        ).scalar_one_or_none()

    def _print_tasks(self, tasks):
        if not tasks:
            print("\nNo tasks found.")
            return

        print("\nYour Tasks:")
        print("-" * 50)
        print(f"{'ID':<5} | {'Status':<10} | {'Task'}")
        print("-" * 50)
        for todo in tasks:
            status = "[x]" if todo.is_completed else "[ ]"
            print(f"{todo.id:<5} | {status:<10} | {todo.task}")
        print("-" * 50)

    def _close(self):
        if self.session:
            self.session.close()


if __name__ == "__main__":
    try:
        app = TodoApp()
        app.start()
    except KeyboardInterrupt:
        print("\nGoodbye!")
