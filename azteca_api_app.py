import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pymysql
from pymysql.err import MySQLError as Error

# Initialize Flask app
app = Flask(__name__, template_folder='templates')
CORS(app, resources={r"/bookings": {"origins": "*"}})


# ------------------ Serve Booking Form ------------------ #
@app.route("/booking_form")
def serve_booking_form():
    return render_template("booking_form.html")


# ------------------ Handle Bookings ------------------ #
@app.route("/bookings", methods=["POST", "GET"])
def handle_bookings():
    db_config = {
        "host": os.getenv("MYSQL_HOST"),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DB")
    }

    connection = None

    if request.method == "POST":
        try:
            data = request.get_json()
            required_fields = ['name', 'email', 'class_type', 'preferred_date', 'language']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"error": f"Missing or empty field: {field}"}), 400

            #print("🔍 DB config:", db_config)
            connection = pymysql.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO bookings (name, email, class_type, preferred_date, language, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                data['name'],
                data['email'],
                data['class_type'],
                data['preferred_date'],
                data['language'],
                data.get('notes', '')
            ))
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

    return jsonify({"error": "Unhandled request"}), 400


# ------------------ Serve Thank You Page ------------------ #
@app.route("/thank-you.html")
def thank_you():
    return render_template("thank-you.html")


# ------------------ Entry Point ------------------ #
if __name__ == "__main__":
    app.run(debug=True)
