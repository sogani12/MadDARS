import psycopg2

# Database connection settings
db_name = "madmajors"
db_user = "namans"
db_password = "aRAY_YAR12!"
db_host = "db"  # 'db' is the service name from docker-compose.yml

# Connect to the PostgreSQL database

try:
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port="5432"
    )
    print("Connected to the database successfully!")

    

except Exception as e:
    print("Error:", e)
finally:
    # Close the database connection
    if conn:
        conn.close()
        print("Database connection closed.")
