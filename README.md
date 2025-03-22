# Xero Accounting API Integration with Django

## Overview
This project implements an integration with the Xero Accounting API using OAuth 2.0 for authentication and authorization in a Django application. It retrieves the Chart of Accounts from Xero and saves the data into a database:
- **SQLite** when using a virtual environment.
- **PostgreSQL** when running the project inside Docker.

The implementation includes a user-friendly interface with filtering capabilities and error handling for token expiration and API failures.

## Instructions to Run the Project

### Step 1: Clone the Project
Start by cloning the project repository to your local machine:
```bash
git clone <repository_url>
cd <project_directory>
```

### Step 2: Rename the Environment Sample File
Rename the `env_sample` file to `.env`. This file contains environment variables and settings necessary for your project.

### Step 3: Choose Your Setup Option
You can set up the project using either:
1. **SQLite in a Virtual Environment**
2. **PostgreSQL with Docker**

Follow the corresponding steps for your chosen option.

## Option 1: Using SQLite and Virtual Environment

### 1. Check `settings.py` for SQLite Configuration
Ensure that the `DATABASES` configuration in `settings.py` is set to use SQLite.

### 2. Set Up a Virtual Environment
Run the following command to create a virtual environment:
```bash
python -m venv venv  # or
python3 -m venv venv
```

### 3. Activate the Virtual Environment
```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
.\venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Make and Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Run the Django Development Server
```bash
python manage.py runserver
```

---

## Option 2: Using PostgreSQL with Docker

### 1. Check `settings.py` for PostgreSQL Configuration
Ensure that the `DATABASES` configuration in `settings.py` is set to use PostgreSQL.

### 2. Check for Docker Configuration Files
Ensure that the following files exist in the project root directory:
- `docker-compose.yml`
- `Dockerfile`
- `entrypoint.sh`
- `.env`

### 3. Build and Run the Docker Containers
Run the following command to build and start the containers:
```bash
docker-compose --build
```

Docker will automatically build the images and start the containers. This process may take a few minutes.

---

## Usage Instructions (For Both Setup Options)

### Step 1: Visit the Home Page
- Open your preferred web browser and navigate to:
  ```
  http://localhost:8000/
  ```
- You will see a simple interface with a **"Login with Xero"** button.

### Step 2: Login with Xero
- Click the **"Login with Xero"** button.
- You will be redirected to Xero’s login page.
- Sign in and authorize the application.
- After authorization, you will be redirected back to the application.
- The home page will confirm authentication and show a **"Get Xero Data"** button.

### Step 3: Fetch Xero Data
- Click the **"Get Xero Data"** button.
- The application will fetch the Chart of Accounts from Xero and store it in the database.
- After retrieving the data, you will be redirected to:
  ```
  http://localhost:8000/account/
  ```
- The account page will display the Chart of Accounts data, allowing filtering and viewing of account details.

---

## Notes
- The application automatically refreshes expired tokens.
- Logs provide debugging information for API interactions.
- For troubleshooting, check the `logs/` directory or use:
  ```bash
  docker logs <container_name>
  ```

