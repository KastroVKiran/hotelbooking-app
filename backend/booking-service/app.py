from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
from datetime import datetime, timedelta
import random

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
    return jsonify({"status": "healthy", "service": "booking-service"})

@app.route('/api/availability', methods=['POST'])
def check_availability():
    try:
        data = request.json
        hotel_id = data.get('hotel_id')
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get hotel room count
        cursor.execute("SELECT rooms FROM hotels WHERE id = %s", (hotel_id,))
        hotel = cursor.fetchone()
        
        if not hotel:
            return jsonify({"error": "Hotel not found"}), 404
        
        # Count booked rooms for the period
        query = """
        SELECT COUNT(*) as booked_rooms FROM bookings 
        WHERE hotel_id = %s AND status = 'confirmed'
        AND ((check_in <= %s AND check_out > %s) OR (check_in < %s AND check_out >= %s))
        """
        cursor.execute(query, (hotel_id, check_in, check_in, check_out, check_out))
        booked = cursor.fetchone()
        
        available_rooms = hotel['rooms'] - booked['booked_rooms']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "hotel_id": hotel_id,
            "available_rooms": max(0, available_rooms),
            "total_rooms": hotel['rooms']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate booking reference
        booking_ref = f"BK{random.randint(100000, 999999)}"
        
        query = """
        INSERT INTO bookings (booking_ref, hotel_id, user_id, check_in, check_out, 
                             guests, room_type, special_requests, total_amount, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            booking_ref,
            data['hotel_id'],
            data.get('user_id', 1),  # Default user for demo
            data['check_in'],
            data['check_out'],
            data['guests'],
            data['room_type'],
            data.get('special_requests', ''),
            data['total_amount'],
            'confirmed'
        )
        
        cursor.execute(query, params)
        conn.commit()
        booking_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "booking_id": booking_id,
            "booking_ref": booking_ref,
            "message": "Booking created successfully"
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/bookings/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT b.*, h.name as hotel_name, h.location as hotel_location
        FROM bookings b
        JOIN hotels h ON b.hotel_id = h.id
        WHERE b.id = %s
        """
        cursor.execute(query, (booking_id,))
        booking = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if booking:
            return jsonify(booking)
        else:
            return jsonify({"error": "Booking not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/bookings/user/<int:user_id>', methods=['GET'])
def get_user_bookings(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT b.*, h.name as hotel_name, h.location as hotel_location
        FROM bookings b
        JOIN hotels h ON b.hotel_id = h.id
        WHERE b.user_id = %s
        ORDER BY b.created_at DESC
        """
        cursor.execute(query, (user_id,))
        bookings = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(bookings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/bookings/<int:booking_id>', methods=['PUT'])
def update_booking(booking_id):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE bookings 
        SET check_in = %s, check_out = %s, guests = %s, 
            room_type = %s, special_requests = %s, total_amount = %s
        WHERE id = %s
        """
        params = (
            data['check_in'],
            data['check_out'],
            data['guests'],
            data['room_type'],
            data.get('special_requests', ''),
            data['total_amount'],
            booking_id
        )
        
        cursor.execute(query, params)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Booking updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE bookings SET status = 'cancelled' WHERE id = %s", (booking_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Booking cancelled successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=82, debug=True)