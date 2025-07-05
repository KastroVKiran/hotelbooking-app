from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
import random
import string
from datetime import datetime

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

def generate_transaction_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "payment-service"})

@app.route('/api/payments', methods=['POST'])
def process_payment():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate transaction ID
        transaction_id = generate_transaction_id()
        
        # Simulate payment processing (always successful for demo)
        payment_status = 'completed'
        
        # Store payment record
        query = """
        INSERT INTO payments (transaction_id, booking_id, amount, currency, 
                            payment_method, card_last_four, payment_status, gateway_response)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            transaction_id,
            data.get('booking_id'),
            data['amount'],
            data.get('currency', 'USD'),
            data['payment_method'],
            data.get('card_number', '')[-4:] if data.get('card_number') else '',
            payment_status,
            '{"status": "success", "gateway": "fake-gateway"}'
        )
        
        cursor.execute(query, params)
        conn.commit()
        payment_id = cursor.lastrowid
        
        # Update booking status if booking_id provided
        if data.get('booking_id'):
            cursor.execute("UPDATE bookings SET payment_status = %s WHERE id = %s", 
                          (payment_status, data['booking_id']))
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "payment_id": payment_id,
            "transaction_id": transaction_id,
            "status": payment_status,
            "amount": data['amount'],
            "currency": data.get('currency', 'USD'),
            "message": "Payment processed successfully"
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT p.*, b.booking_ref, h.name as hotel_name
        FROM payments p
        LEFT JOIN bookings b ON p.booking_id = b.id
        LEFT JOIN hotels h ON b.hotel_id = h.id
        WHERE p.id = %s
        """
        cursor.execute(query, (payment_id,))
        payment = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if payment:
            return jsonify(payment)
        else:
            return jsonify({"error": "Payment not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/payments/booking/<int:booking_id>', methods=['GET'])
def get_booking_payments(booking_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT * FROM payments 
        WHERE booking_id = %s
        ORDER BY created_at DESC
        """
        cursor.execute(query, (booking_id,))
        payments = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(payments)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/payments/<int:payment_id>/refund', methods=['POST'])
def refund_payment(payment_id):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get original payment
        cursor.execute("SELECT * FROM payments WHERE id = %s", (payment_id,))
        payment = cursor.fetchone()
        
        if not payment:
            return jsonify({"error": "Payment not found"}), 404
        
        # Create refund record
        refund_amount = data.get('amount', payment[2])  # payment[2] is amount
        transaction_id = generate_transaction_id()
        
        query = """
        INSERT INTO payments (transaction_id, booking_id, amount, currency, 
                            payment_method, payment_status, gateway_response, refund_for)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            transaction_id,
            payment[1],  # booking_id
            -refund_amount,  # negative amount for refund
            payment[3],  # currency
            payment[4],  # payment_method
            'completed',
            '{"status": "refund_success", "gateway": "fake-gateway"}',
            payment_id
        )
        
        cursor.execute(query, params)
        conn.commit()
        refund_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "refund_id": refund_id,
            "transaction_id": transaction_id,
            "amount": refund_amount,
            "status": "completed",
            "message": "Refund processed successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/invoices/<int:booking_id>', methods=['GET'])
def generate_invoice(booking_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get booking details
        query = """
        SELECT b.*, h.name as hotel_name, h.location as hotel_location,
               u.username, u.email
        FROM bookings b
        JOIN hotels h ON b.hotel_id = h.id
        JOIN users u ON b.user_id = u.id
        WHERE b.id = %s
        """
        cursor.execute(query, (booking_id,))
        booking = cursor.fetchone()
        
        if not booking:
            return jsonify({"error": "Booking not found"}), 404
        
        # Get payment details
        cursor.execute("SELECT * FROM payments WHERE booking_id = %s AND amount > 0", (booking_id,))
        payment = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        # Calculate invoice details
        nights = (datetime.strptime(booking['check_out'], '%Y-%m-%d') - 
                 datetime.strptime(booking['check_in'], '%Y-%m-%d')).days
        subtotal = booking['total_amount']
        tax_rate = 0.1  # 10% tax
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        
        invoice = {
            "invoice_id": f"INV-{booking['id']}-{datetime.now().strftime('%Y%m%d')}",
            "booking_ref": booking['booking_ref'],
            "hotel_name": booking['hotel_name'],
            "hotel_location": booking['hotel_location'],
            "guest_name": booking['username'],
            "guest_email": booking['email'],
            "check_in": booking['check_in'],
            "check_out": booking['check_out'],
            "nights": nights,
            "room_type": booking['room_type'],
            "guests": booking['guests'],
            "subtotal": subtotal,
            "tax_rate": tax_rate,
            "tax_amount": tax_amount,
            "total": total,
            "payment_status": payment['payment_status'] if payment else 'pending',
            "payment_method": payment['payment_method'] if payment else None,
            "transaction_id": payment['transaction_id'] if payment else None,
            "invoice_date": datetime.now().strftime('%Y-%m-%d'),
            "due_date": booking['check_in']
        }
        
        return jsonify(invoice)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/payments/stats', methods=['GET'])
def get_payment_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get payment statistics
        queries = {
            'total_payments': "SELECT COUNT(*) as count, SUM(amount) as total FROM payments WHERE amount > 0",
            'successful_payments': "SELECT COUNT(*) as count FROM payments WHERE payment_status = 'completed' AND amount > 0",
            'failed_payments': "SELECT COUNT(*) as count FROM payments WHERE payment_status = 'failed'",
            'refunds': "SELECT COUNT(*) as count, SUM(ABS(amount)) as total FROM payments WHERE amount < 0"
        }
        
        stats = {}
        for key, query in queries.items():
            cursor.execute(query)
            result = cursor.fetchone()
            stats[key] = result
        
        cursor.close()
        conn.close()
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=85, debug=True)