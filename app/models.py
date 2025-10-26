from flask_login import UserMixin
from werkzeug.security import check_password_hash
from app.db_connect import get_db

class Employee(UserMixin):
    def __init__(self, employee_id, username, password_hash, first_name, last_name, email, phone, position, hire_date, is_active):
        self.id = employee_id  # Flask-Login requires this to be 'id'
        self.employee_id = employee_id
        self.username = username
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.position = position
        self.hire_date = hire_date
        self._is_active = is_active  # Store as private variable

    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """Return the employee ID as a string (required by Flask-Login)"""
        return str(self.employee_id)

    @property
    def is_active(self):
        """Return True if the employee is active (required by Flask-Login)"""
        return self._is_active

    def get_full_name(self):
        """Return full name of employee"""
        return f"{self.first_name} {self.last_name}"

    @staticmethod
    def get_by_id(employee_id):
        """Get employee by ID"""
        db = get_db()
        if db is None:
            return None

        cursor = db.cursor()
        cursor.execute("""
            SELECT employee_id, username, password_hash, first_name, last_name,
                   email, phone, position, hire_date, is_active
            FROM employee
            WHERE employee_id = %s AND is_active = TRUE
        """, (employee_id,))

        row = cursor.fetchone()
        cursor.close()

        if row:
            return Employee(
                employee_id=row['employee_id'],
                username=row['username'],
                password_hash=row['password_hash'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                email=row['email'],
                phone=row['phone'],
                position=row['position'],
                hire_date=row['hire_date'],
                is_active=row['is_active']
            )
        return None

    @staticmethod
    def get_by_username(username):
        """Get employee by username"""
        db = get_db()
        if db is None:
            return None

        cursor = db.cursor()
        cursor.execute("""
            SELECT employee_id, username, password_hash, first_name, last_name,
                   email, phone, position, hire_date, is_active
            FROM employee
            WHERE username = %s AND is_active = TRUE
        """, (username,))

        row = cursor.fetchone()
        cursor.close()

        if row:
            return Employee(
                employee_id=row['employee_id'],
                username=row['username'],
                password_hash=row['password_hash'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                email=row['email'],
                phone=row['phone'],
                position=row['position'],
                hire_date=row['hire_date'],
                is_active=row['is_active']
            )
        return None

    @staticmethod
    def authenticate(username, password):
        """Authenticate user with username and password"""
        employee = Employee.get_by_username(username)
        if employee and employee.check_password(password):
            return employee
        return None
