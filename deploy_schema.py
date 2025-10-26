import pymysql
import os
from dotenv import load_dotenv
import re

load_dotenv()

def deploy_schema():
    """Deploy the database schema"""
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

        # Read and execute schema file
        with open('database/schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Remove comments
        schema_sql = re.sub(r'--.*$', '', schema_sql, flags=re.MULTILINE)

        # Split by semicolon but keep multi-line statements together
        statements = []
        current_statement = []

        for line in schema_sql.split('\n'):
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
                    # Print only the first word (CREATE, DROP, etc.)
                    action = statement.split()[0] if statement else ""
                    print(f"[OK] {action} statement executed")
                except Exception as e:
                    print(f"[ERROR] {e}")
                    print(f"Statement: {statement[:100]}...")

        connection.commit()
        print("\n[SUCCESS] Schema deployed successfully!")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"[ERROR] Error deploying schema: {e}")
        return False

    return True

if __name__ == '__main__':
    deploy_schema()
