import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
import requests
from datetime import datetime

# Constants
DATABASE_PARAMS = {
    "dbname": "taskly_db",
    "user": "postgres",
    "password": "password",
    "host": "localhost"
}
MAILGUN_PARAMS = {
    "api_key": "f5bc4441a7dcf79999c0eae3c9873450-f68a26c9-ee97c458",
    "domain": "sandbox95cd123de98742a9b22670e67402c67e.mailgun.org"
}
EMAIL_RECIPIENT = "janpreetswatch@gmail.com"

# Observer Pattern - Notification Manager and Notifiers
class NotificationManager:
    def __init__(self):
        self.observers = []

    def register_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, message):
        for observer in self.observers:
            observer.notify(message)

class EmailNotifier:
    def __init__(self, api_key, domain):
        self.api_key = api_key
        self.domain = domain

    def notify(self, message):
        response = requests.post(
            f"https://api.mailgun.net/v3/{self.domain}/messages",
            auth=("api", self.api_key),
            data={"from": f"Taskly <mailgun@{self.domain}>",
                  "to": [EMAIL_RECIPIENT],
                  "subject": "Taskly Notification",
                  "text": message})
        print(f"Email notification sent: {response.status_code}")

# Stratergy pattern - Task and Sorting Strategies
class Task:
    def __init__(self, name, priority, deadline):
        self.name = name
        self.priority = priority
        self.deadline = deadline

class SortStrategy:
    def sort(self, tasks, ascending=True):
        pass

class SortByPriority(SortStrategy):
    def sort(self, tasks, ascending=True):
        return sorted(tasks, key=lambda task: task.priority, reverse=not ascending)

class SortByDeadline(SortStrategy):
    def sort(self, tasks, ascending=True):
        return sorted(tasks, key=lambda task: task.deadline, reverse=not ascending)

# Database Operations
class Database:
    def __init__(self, dbname, user, password, host):
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
        self.conn.autocommit = True
        self.create_table()

    def create_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id SERIAL PRIMARY KEY,
                    task_name VARCHAR(255) UNIQUE,
                    priority INTEGER,
                    deadline DATE
                )
            """)

    def add_task(self, task):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (task_name, priority, deadline) VALUES (%s, %s, %s) ON CONFLICT (task_name) DO NOTHING",
                (task.name, task.priority, task.deadline))

    def get_tasks(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT task_name, priority, deadline FROM tasks ORDER BY task_name ASC")
            return [Task(*row) for row in cur.fetchall()]

    def delete_task(self, task_name):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE task_name = %s", (task_name,))

    def update_task(self, old_task_name, new_task_name, new_priority, new_deadline):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET task_name = %s, priority = %s, deadline = %s WHERE task_name = %s",
                (new_task_name, new_priority, new_deadline, old_task_name))

# Main Taskly Application
class Taskly:
    def __init__(self):
        self.db = Database(**DATABASE_PARAMS)
        self.notification_manager = NotificationManager()

    def add_task(self, name, priority, deadline):
        task = Task(name, priority, deadline)
        self.db.add_task(task)
        due_date = deadline.strftime('%Y-%m-%d')
        notification_message = f"New task added: {name} with priority {priority} due on {due_date}"
        self.notification_manager.notify_observers(notification_message)

    def display_tasks(self, sort_strategy, ascending=True):
        sorted_tasks = sort_strategy.sort(self.db.get_tasks(), ascending)
        return "\n".join(f"{task.name} - Priority: {task.priority}, Deadline: {task.deadline.strftime('%Y-%m-%d')}" for task in sorted_tasks)

    def delete_task(self, task_name):
        self.db.delete_task(task_name)
        notification_message = f"Task deleted: {task_name}"
        self.notification_manager.notify_observers(notification_message)

    def update_task(self, old_task_name, new_task_name, new_priority, new_deadline):
        self.db.update_task(old_task_name, new_task_name, new_priority, new_deadline)
        due_date = new_deadline.strftime('%Y-%m-%d')
        notification_message = f"Task updated: {old_task_name} to name {new_task_name}, priority {new_priority}, and deadline {due_date}"
        self.notification_manager.notify_observers(notification_message)

# GUI Integration with Task Name Update and Sort Order Options
class TasklyGUI(tk.Tk):
    def __init__(self, taskly):
        super().__init__()
        self.taskly = taskly
        self.title("Taskly Task Manager")
        self.geometry("700x800")

        # Input Section for Adding Tasks
        self.setup_task_adding_section()
        # Setup Task Management (Update & Delete) Section
        self.setup_task_management_section()
        # Setup Task Display Section
        self.setup_task_display_section()

        self.refresh_tasks_combobox()

    def setup_task_adding_section(self):
        tk.Label(self, text="Task Name:").pack()
        self.task_name_var = tk.StringVar()
        tk.Entry(self, textvariable=self.task_name_var).pack()

        tk.Label(self, text="Priority:").pack()
        self.priority_var = tk.IntVar()
        tk.Entry(self, textvariable=self.priority_var).pack()

        tk.Label(self, text="Deadline (YYYY-MM-DD):").pack()
        self.deadline_var = tk.StringVar()
        tk.Entry(self, textvariable=self.deadline_var).pack()

        tk.Button(self, text="Add Task", command=self.add_task).pack()

    def setup_task_management_section(self):
        manage_tasks_frame = tk.Frame(self)
        manage_tasks_frame.pack(pady=20)

        tk.Label(manage_tasks_frame, text="Select Task to Update/Delete:").grid(row=0, column=0, columnspan=2)
        self.task_combobox_var = tk.StringVar()
        self.task_combobox = ttk.Combobox(manage_tasks_frame, textvariable=self.task_combobox_var, state="readonly")
        self.task_combobox.grid(row=1, column=0, columnspan=2, pady=5)

        tk.Label(manage_tasks_frame, text="New Task Name:").grid(row=2, column=0)
        self.new_task_name_var = tk.StringVar()
        tk.Entry(manage_tasks_frame, textvariable=self.new_task_name_var).grid(row=2, column=1)

        tk.Label(manage_tasks_frame, text="New Priority:").grid(row=3, column=0)
        self.new_priority_var = tk.IntVar()
        tk.Entry(manage_tasks_frame, textvariable=self.new_priority_var).grid(row=3, column=1)

        tk.Label(manage_tasks_frame, text="New Deadline (YYYY-MM-DD):").grid(row=4, column=0)
        self.new_deadline_var = tk.StringVar()
        tk.Entry(manage_tasks_frame, textvariable=self.new_deadline_var).grid(row=4, column=1)

        tk.Button(manage_tasks_frame, text="Update Task", command=self.update_task).grid(row=5, column=0, pady=5)
        tk.Button(manage_tasks_frame, text="Delete Task", command=self.delete_task).grid(row=5, column=1, pady=5)

    def setup_task_display_section(self):
        tk.Button(self, text="Display Tasks by Priority (Asc)", command=lambda: self.display_tasks(SortByPriority(), True)).pack(pady=2)
        tk.Button(self, text="Display Tasks by Priority (Desc)", command=lambda: self.display_tasks(SortByPriority(), False)).pack(pady=2)
        tk.Button(self, text="Display Tasks by Deadline (Asc)", command=lambda: self.display_tasks(SortByDeadline(), True)).pack(pady=2)
        tk.Button(self, text="Display Tasks by Deadline (Desc)", command=lambda: self.display_tasks(SortByDeadline(), False)).pack(pady=2)

        self.tasks_display = tk.Text(self, state='disabled', height=15)
        self.tasks_display.pack(pady=10)

    def add_task(self):
        name = self.task_name_var.get()
        priority = self.priority_var.get()
        deadline_str = self.deadline_var.get()
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
            self.taskly.add_task(name, priority, deadline)
            messagebox.showinfo("Success", "Task added successfully.")
            self.refresh_tasks_combobox()
        except ValueError:
            messagebox.showerror("Error", "Invalid input for date. Use YYYY-MM-DD format.")
        finally:
            self.task_name_var.set("")
            self.priority_var.set("")
            self.deadline_var.set("")

    def update_task(self):
        old_task_name = self.task_combobox_var.get()
        new_task_name = self.new_task_name_var.get()
        new_priority = self.new_priority_var.get()
        new_deadline_str = self.new_deadline_var.get()
        try:
            new_deadline = datetime.strptime(new_deadline_str, '%Y-%m-%d')
            self.taskly.update_task(old_task_name, new_task_name, new_priority, new_deadline)
            messagebox.showinfo("Success", "Task updated successfully.")
            self.refresh_tasks_combobox()
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")

    def delete_task(self):
        task_name = self.task_combobox_var.get()
        self.taskly.delete_task(task_name)
        messagebox.showinfo("Success", "Task deleted successfully.")
        self.refresh_tasks_combobox()

    def display_tasks(self, sort_strategy, ascending):
        tasks_text = self.taskly.display_tasks(sort_strategy, ascending)
        self.tasks_display.config(state='normal')
        self.tasks_display.delete(1.0, tk.END)
        self.tasks_display.insert(tk.END, tasks_text)
        self.tasks_display.config(state='disabled')

    def refresh_tasks_combobox(self):
        tasks = self.taskly.db.get_tasks()
        task_names = [task.name for task in tasks]
        self.task_combobox['values'] = task_names
        if task_names:
            self.task_combobox.current(0)
        else:
            self.task_combobox_var.set("")

if __name__ == "__main__":
    taskly = Taskly()
    email_notifier = EmailNotifier(**MAILGUN_PARAMS)
    taskly.notification_manager.register_observer(email_notifier)

    gui = TasklyGUI(taskly)
    gui.mainloop()
