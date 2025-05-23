from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
from pymysql.err import MySQLError as Error

app = Flask(__name__)
CORS(app, resources={r"/bookings": {"origins": "http://localhost:8000"}})

# MySQL config
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}


@app.route("/")
def home():
    return "Azteca API is live!"

@app.route("/bookings", methods=["GET", "POST"])
def bookings():
    if request.method == "POST":
        data = request.get_json()
        required_fields = ['name', 'email', 'class_type', 'preferred_date', 'language']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing or empty field: {field}"}), 400

        connection = None
        try:
            connection = pymysql.connect(**db_config)
            cursor = connection.cursor()
            query = """
                INSERT INTO bookings (name, email, class_type, preferred_date, language, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                data['name'],
                data['email'],
                data['class_type'],
                data['preferred_date'],
                data['language'],
                data.get('notes', '')
            )
            cursor.execute(query, values)
            connection.commit()
            print(f"✅ Booking saved: {data['name']} ({data['email']})")
            return jsonify({"message": "Booking saved successfully!"}), 201
        except Error as e:
            print("❌ POST ERROR:", e)
            return jsonify({"error": str(e)}), 500
        finally:
            if connection:
                cursor.close()
                connection.close()

    elif request.method == "GET":
        connection = None
        try:
            connection = pymysql.connect(**db_config)
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM bookings ORDER BY id DESC")
            results = cursor.fetchall()
            return jsonify(results), 200
        except Error as e:
            print("❌ GET ERROR:", e)
            return jsonify({"error": str(e)}), 500
        finally:
            if connection:
                cursor.close()
                connection.close()

if __name__ == "__main__":
    app.run(debug=True)
