from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__)
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql-db'),
    'user': os.getenv('DB_USER', 'hotel_user'),
    'password': os.getenv('DB_PASSWORD', 'hotel_pass'),
    'database': os.getenv('DB_NAME', 'hotel_booking'),
    'port': int(os.getenv('DB_PORT', 3306))
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "hotel-service"})

@app.route('/api/hotels', methods=['GET'])
def get_hotels():
    try:
        location = request.args.get('location', '')
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM hotels WHERE status = 'active'"
        params = []
        
        if location:
            query += " AND location LIKE %s"
            params.append(f"%{location}%")
        
        cursor.execute(query, params)
        hotels = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(hotels)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/hotels/<int:hotel_id>', methods=['GET'])
def get_hotel(hotel_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM hotels WHERE id = %s", (hotel_id,))
        hotel = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if hotel:
            return jsonify(hotel)
        else:
            return jsonify({"error": "Hotel not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/hotels', methods=['POST'])
def create_hotel():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO hotels (name, location, rooms, price, amenities, description, image, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['name'],
            data['location'],
            data['rooms'],
            data['price'],
            ','.join(data['amenities']) if isinstance(data['amenities'], list) else data['amenities'],
            data['description'],
            data['image'],
            data.get('status', 'active')
        )
        
        cursor.execute(query, params)
        conn.commit()
        hotel_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return jsonify({"id": hotel_id, "message": "Hotel created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/hotels/<int:hotel_id>', methods=['PUT'])
def update_hotel(hotel_id):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE hotels 
        SET name = %s, location = %s, rooms = %s, price = %s, 
            amenities = %s, description = %s, image = %s, status = %s
        WHERE id = %s
        """
        params = (
            data['name'],
            data['location'],
            data['rooms'],
            data['price'],
            ','.join(data['amenities']) if isinstance(data['amenities'], list) else data['amenities'],
            data['description'],
            data['image'],
            data.get('status', 'active'),
            hotel_id
        )
        
        cursor.execute(query, params)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Hotel updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/hotels/<int:hotel_id>', methods=['DELETE'])
def delete_hotel(hotel_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM hotels WHERE id = %s", (hotel_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Hotel deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)