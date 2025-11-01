# Bannerlord Troop & Item Database

This project is a Flask web application that provides a searchable and filterable database of troops, items, and equipment from the game *Mount & Blade II: Bannerlord*.

## Setup Instructions

Follow these steps in order to get the application running locally.

### 1. MySQL Setup

1.  **Install MySQL Server:** Download and install the MySQL Community Server from the [official website](https://dev.mysql.com/downloads/mysql/).

2.  **Add to PATH:** Add the `bin` folder of your MySQL Server installation (e.g., `C:\Program Files\MySQL\MySQL Server 8.0\bin`) to your system's `PATH` environment variable.

3.  **Start the MySQL Server:** Ensure the MySQL service is running.

4.  **Create Database and User:** Open a terminal and log in to MySQL as the root user (you will be prompted for the password you set during installation).

    ```sh
    mysql -u root -p
    ```

    Once logged in, run the following SQL commands. **Choose a secure password** for your new database user.

    ```sql
    -- 1. Create the database
    CREATE DATABASE bannerlord_db;
    
    -- 2. Create a new, dedicated user for your application
    CREATE USER 'bannerlord_user'@'localhost' IDENTIFIED BY 'your_new_secure_password';
    
    -- 3. Grant all permissions on your new database to your new user
    GRANT ALL PRIVILEGES ON bannerlord_db.* TO 'bannerlord_user'@'localhost';
    
    -- 4. Apply the changes
    FLUSH PRIVILEGES;
    
    -- 5. Exit MySQL
    EXIT;
    ```

### 2. Project Setup

1.  **Clone the Repository:**
    ```sh
    git clone [https://github.com/f-uncuoglu/bannerlord_project.git](https://github.com/f-uncuoglu/bannerlord_project.git)
    cd bannerlord_project
    ```

2.  **Create `.env` File:**
    Create a file named `.env` in the root of the project directory and add the following content. **Use the new user and password** you just created in the step above.

    ```env
    SECRET_KEY=your-secret-key-here-change-this
    MYSQL_HOST=localhost
    MYSQL_USER=bannerlord_user
    MYSQL_PASSWORD=your_new_secure_password
    MYSQL_DB=bannerlord_db
    MYSQL_PORT=3306
    ```

3.  **Create and Activate Virtual Environment:**
    It is highly recommended to use a Python virtual environment.

    ```sh
    # Create the venv
    python -m venv venv
    
    # Activate the venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

4.  **Install Dependencies:**
    Install all required Python packages from `requirements.txt`.
    ```sh
    pip install -r requirements.txt
    ```

### 3. Database Initialization

Run the `init_db.py` script. This will create all the tables (from `schema.sql`) and insert all the data you just generated.

```sh
python database/init_db.py