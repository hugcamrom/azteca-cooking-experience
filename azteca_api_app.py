from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pymysql
from pymysql.err import MySQLError as Error
import os
from dotenv import load_dotenv

from db import db
from models import Item, Category, Shop

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS

# SQLAlchemy setup for Shopping Tracker
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ------------------ AZTECA BOOKINGS ROUTE ------------------ #
@app.route("/bookings", methods=["POST"])
def create_booking():
    data = request.get_json()
    required_fields = ['name', 'email', 'class_type', 'preferred_date', 'language']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Missing or empty field: {field}"}), 400

    db_config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DB")
    }

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

# ------------------ SHOPPING TRACKER ROUTES ------------------ #

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/items')
def items_page():
    return render_template('items.html')

@app.route('/api/items', methods=['POST'])
def add_item():
    data = request.get_json()
    new_item = Item(
        name=data.get('name'),
        quantity=data.get('quantity', 1),
        needed=data.get('needed', True),
        category_id=data.get('category_id'),
        shop_id=data.get('shop_id')
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': 'Item added successfully'}), 201

@app.route('/api/items', methods=['GET'])
def get_items():
    items = Item.query.all()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'quantity': item.quantity,
        'needed': item.needed,
        'category': item.category.name if item.category else None,
        'shop': item.shop.name if item.shop else None,
        'last_updated': item.last_updated.isoformat() if item.last_updated else None
    } for item in items])

@app.route('/api/setup', methods=['POST'])
def setup_defaults():
    for name in ['Food', 'Cleaning', 'Toiletries', 'Snacks']:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
    for name, location in [('Tesco', 'Dublin 8'), ('Lidl', 'Dublin 6'), ('SuperValu', 'Online')]:
        if not Shop.query.filter_by(name=name).first():
            db.session.add(Shop(name=name, location=location))
    db.session.commit()
    return jsonify({'message': 'Defaults added'})

@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.get_json()
    item.name = data.get('name', item.name)
    item.quantity = data.get('quantity', item.quantity)
    item.needed = data.get('needed', item.needed)
    item.category_id = data.get('category_id', item.category_id)
    item.shop_id = data.get('shop_id', item.shop_id)
    db.session.commit()
    return jsonify({'message': 'Item updated successfully'})

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted successfully'})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify([{'id': c.id, 'name': c.name} for c in Category.query.all()])

@app.route('/api/categories', methods=['POST'])
def add_category():
    data = request.get_json()
    name = data.get('name')
    if name:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
            db.session.commit()
            return jsonify({'message': 'Category added'}), 201
        return jsonify({'message': 'Category already exists'}), 200
    return jsonify({'error': 'Missing name'}), 400

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted'})

@app.route('/api/shops', methods=['GET'])
def get_shops():
    return jsonify([{'id': s.id, 'name': s.name} for s in Shop.query.all()])

@app.route('/api/shops', methods=['POST'])
def add_shop():
    data = request.get_json()
    name = data.get('name')
    location = data.get('location', 'Unknown')
    if name:
        if not Shop.query.filter_by(name=name).first():
            db.session.add(Shop(name=name, location=location))
            db.session.commit()
            return jsonify({'message': 'Shop added'}), 201
        return jsonify({'message': 'Shop already exists'}), 200
    return jsonify({'error': 'Missing name'}), 400

@app.route('/api/shops/<int:shop_id>', methods=['DELETE'])
def delete_shop(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    db.session.delete(shop)
    db.session.commit()
    return jsonify({'message': 'Shop deleted'})

if __name__ == '__main__':
    app.run(debug=True)
