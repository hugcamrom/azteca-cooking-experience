import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import pymysql
from pymysql.err import MySQLError as Error

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

def check_auth(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def login_required():
    return Response(
        "Login required",
        401,
        {"WWW-Authenticate": 'Basic realm="Azteca Admin"'}
    )


app = Flask(__name__, template_folder="templates")
CORS(app, resources={r"/bookings": {"origins": "*"}})


def get_db_config():
    return {
        "host": os.getenv("MYSQL_HOST"),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DB"),
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/booking_form")
def serve_booking_form():
    return render_template("booking_form.html")


@app.route("/thank-you.html")
def thank_you():
    return render_template("thank-you.html")


@app.route("/bookings", methods=["POST", "GET"])
def handle_bookings():
    db_config = get_db_config()
    connection = None

    if request.method == "POST":
        try:
            data = request.get_json()
            required_fields = ["name", "email", "class_type", "preferred_date", "language"]

            for field in required_fields:
                if not data.get(field):
                    return jsonify({"error": f"Missing or empty field: {field}"}), 400

            connection = pymysql.connect(**db_config)
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO bookings (name, email, class_type, preferred_date, language, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                data["name"],
                data["email"],
                data["class_type"],
                data["preferred_date"],
                data["language"],
                data.get("notes", "")
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

    if request.method == "GET":
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


@app.route("/admin")
def view_bookings():
    auth = request.authorization

    if not auth or not check_auth(auth.username, auth.password):
        return login_required()

    db_config = get_db_config()
    connection = None

    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute("SELECT * FROM bookings ORDER BY id DESC")
        bookings = cursor.fetchall()

        return render_template("admin.html", bookings=bookings)

    except Error as e:
        print("❌ ADMIN ERROR:", e)
        return f"Database error: {e}", 500

    finally:
        if connection:
            cursor.close()
            connection.close()


if __name__ == "__main__":
    app.run(debug=True)