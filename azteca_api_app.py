from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

db_config = {
    "host": "localhost",
    "user": "your_mysql_user",
    "password": "your_mysql_password",
    "database": "azteca"
}
# This code defines a simple Flask API for booking classes at Azteca.

app = Flask(__name__)

# Replace with your actual MySQL credentials
db_config = {
    "host": "localhost",
    "user": "your_mysql_user",
    "password": "your_mysql_password",
    "database": "azteca"
}

@app.route("/")
def home():
    return "Azteca API is live!"

@app.route("/book", methods=["POST"])
def book_class():
    data = request.json
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        sql = """INSERT INTO bookings (name, email, class_type, preferred_date, language, notes)
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        values = (
            data.get("name"),
            data.get("email"),
            data.get("class_type"),
            data.get("preferred_date"),
            data.get("language"),
            data.get("notes"),
        )
        cursor.execute(sql, values)
        connection.commit()
        return jsonify({"message": "Booking successful!"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    app.run(debug=True)
    
# This code defines a simple Flask API for booking classes at Azteca.