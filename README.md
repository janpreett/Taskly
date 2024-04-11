# Taskly
Taskly is a task management application designed to demonstrate the implementation of software architecture principles, including the use of design patterns and interaction with a cloud database and third-party web services. This guide will walk you through setting up and running the Taskly application on your own machine.

Prerequisites
Before running the Taskly application, ensure you have the following installed:

Python 3.8 or newer
pip (Python package installer)
PostgreSQL database
Setup
1. Clone the Repository
First, clone the Taskly application repository to your local machine. If the code is not hosted on a repository, skip this step.
2. Install Dependencies
Install the required Python libraries using pip:
3. Database Configuration
Using an Existing PostgreSQL Database
If you wish to use your own PostgreSQL database, follow these steps:

Create a new database in your PostgreSQL server.
Open the Python file containing database parameters (DATABASE_PARAMS) and update the connection details (dbname, user, password, host) to match your database configuration.
Example:
DATABASE_PARAMS = {
    "dbname": "your_database_name",
    "user": "your_database_user",
    "password": "your_database_password",
    "host": "localhost"  # or your database server address
}

Initial Database Setup
To set up the required tables in your database, simply run the Taskly application. It will automatically create a tasks table if it does not exist.

4. Third-party Web Service Configuration
The application uses Mailgun for sending email notifications. Update the MAILGUN_PARAMS in the code with your Mailgun API key and domain.

Example:
MAILGUN_PARAMS = {
    "api_key": "your_mailgun_api_key",
    "domain": "your_mailgun_domain"
}

Running the Application

To run the Taskly application, navigate to the directory containing the application code and run:

Using the Application

Add a Task: Fill in the task name, priority, and deadline, then click "Add Task".
Update/Delete a Task: Select a task from the dropdown menu, update the details as needed, and click "Update Task" or "Delete Task".
Sort and Display Tasks: Use the display buttons to sort tasks by priority or deadline, either in ascending or descending order.
Troubleshooting
Database Connection Issues: Verify that your PostgreSQL server is running and that the connection details in DATABASE_PARAMS are correct.
Dependency Installation Issues: Ensure you have the correct version of Python installed and that pip is up to date.
