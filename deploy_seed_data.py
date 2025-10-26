import pymysql
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
import re

load_dotenv()

def deploy_seed_data():
    """Deploy seed data with properly hashed passwords"""
    try:
        # Connect to database
        connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            port=int(os.getenv('DB_PORT', 3306))
        )

        cursor = connection.cursor()

        # Generate password hash for 'password123'
        password_hash = generate_password_hash('password123')
        print(f"[INFO] Generated password hash for 'password123'")

        # Insert employees with real password hashes
        print("\n[INFO] Inserting employees...")
        cursor.execute("""
            INSERT INTO employee (username, password_hash, first_name, last_name, email, phone, position, hire_date, is_active) VALUES
            (%s, %s, 'John', 'Admin', 'admin@rentalshop.com', '555-0100', 'Manager', '2023-01-15', TRUE),
            (%s, %s, 'Jane', 'Smith', 'jsmith@rentalshop.com', '555-0101', 'Rental Agent', '2023-03-20', TRUE),
            (%s, %s, 'Mike', 'Jones', 'mjones@rentalshop.com', '555-0102', 'Rental Agent', '2023-06-10', TRUE)
        """, ('admin', password_hash, 'jsmith', password_hash, 'mjones', password_hash))
        print("[OK] Employees inserted")

        # Read seed data file
        with open('database/seed_data.sql', 'r', encoding='utf-8') as f:
            seed_sql = f.read()

        # Remove employee insert statements (we already did those)
        seed_sql = re.sub(r'INSERT INTO employee.*?;', '', seed_sql, flags=re.DOTALL)

        # Remove comments
        seed_sql = re.sub(r'--.*$', '', seed_sql, flags=re.MULTILINE)

        # Split by semicolon but keep multi-line statements together
        statements = []
        current_statement = []

        for line in seed_sql.split('\n'):
            line = line.strip()
            if line:
                current_statement.append(line)
                if line.endswith(';'):
                    statements.append(' '.join(current_statement))
                    current_statement = []

        # Execute each statement
        for statement in statements:
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                    # Determine what was inserted
                    if 'INTO customer' in statement:
                        print("[OK] Customers inserted")
                    elif 'INTO equipment' in statement:
                        print("[OK] Equipment inserted")
                    elif 'INTO rental' in statement:
                        print("[OK] Rentals inserted")
                    elif 'INTO rental_detail' in statement:
                        print("[OK] Rental details inserted")
                except Exception as e:
                    print(f"[ERROR] {e}")
                    print(f"Statement: {statement[:100]}...")

        connection.commit()
        print("\n[SUCCESS] Seed data deployed successfully!")
        print("\n[INFO] You can now log in with:")
        print("  Username: admin")
        print("  Password: password123")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"[ERROR] Error deploying seed data: {e}")
        return False

    return True

if __name__ == '__main__':
    deploy_seed_data()
