# Kyykka.com

Repository for kyykka.com 2.0

## Setting up a local development environment

### Prerequisites

- Python 3.10 or newer
- MySQL
- Node.js (for frontend development)

### Backend Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/Polytekninen-Willimiesklubi/kyykkacom.git
   cd kyykkacom
   ```

2. System dependencies:

- PyMySQL (default): The project uses `PyMySQL` (a pure-Python MySQL driver) by default, so you do not need to install native MySQL client headers or build tools for most development workflows.

- Optional — native MySQL driver (`mysqlclient`): If you prefer the native driver (for example for slightly better performance or binary compatibility), install the system build dependencies on Ubuntu/Debian and then install the `mysql` optional extra described below.

  ```bash
  sudo apt update
  sudo apt install -y python3-dev default-libmysqlclient-dev pkg-config build-essential memcached
  ```

  After installing the system packages, add the native driver into your venv with:

  ```bash
  pip install -e ".[mysql]"
  ```

  Or install it together with dev extras:

  ```bash
  pip install -e ".[dev,mysql]"
  ```

3. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

4. Install Python dependencies:
   ```bash
   # Install core dependencies
   pip install -e .
   
   # For development, install additional tools
   pip install -e ".[dev]"

   # If using `mysqlclient`, install that package with dev
   pip install -e ".[dev, mysqlclient]"
   ```

5. Database setup:

- Create a MySQL database (example name `nkl` or the one you prefer).

- Create a local settings file at `nkl/settings_local.py` (this file is excluded from version control). Example `settings_local.py`:

   ```python
   SECRET_KEY = "replace-with-secure-key"
   DEBUG = True
   DATABASES = {
         "default": {
               "ENGINE": "django.db.backends.mysql",
               "NAME": "nkl",
               "USER": "example",
               "PASSWORD": "example",
               "HOST": "127.0.0.1",
               "PORT": "3306",
         }
   }
   ```

- Note: the project ships with `nkl/__init__.py` that calls `pymysql.install_as_MySQLdb()` so `PyMySQL` works as a drop-in replacement for `mysqlclient`.

- Run migrations:
   ```bash
   python manage.py migrate
   ```

- Populate initial data (optional):
   ```bash
   python manage.py shell
   >>> from utils.dummyGen import *; initGen()
   ```

6. Start the development server:
   ```bash
   python manage.py runserver localhost:8000
   ```

### Frontend Setup

1. Install Node.js from [the official website](https://nodejs.org/) if you haven't already

2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173` by default.

## Development

For the best development experience, you can start both frontend and backend servers using the provided VS Code tasks:

```bash
# Start both backend and frontend servers
npm run dev
```

## Project Structure

- `/api/` - Django API application
- `/kyykka/` - Main Django application
- `/frontend/` - Vue.js frontend application
- `/nkl/` - Django project settings
- `/utils/` - Utility scripts and helpers
