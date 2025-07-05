from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
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

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "review-service"})

@app.route('/api/reviews', methods=['POST'])
def create_review():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO reviews (hotel_id, user_id, rating, comment, booking_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            data['hotel_id'],
            data.get('user_id', 1),  # Default user for demo
            data['rating'],
            data['comment'],
            data.get('booking_id')
        )
        
        cursor.execute(query, params)
        conn.commit()
        review_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "review_id": review_id,
            "message": "Review created successfully"
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reviews/hotel/<int:hotel_id>', methods=['GET'])
def get_hotel_reviews(hotel_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT r.*, u.username, h.name as hotel_name
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        JOIN hotels h ON r.hotel_id = h.id
        WHERE r.hotel_id = %s
        ORDER BY r.created_at DESC
        """
        cursor.execute(query, (hotel_id,))
        reviews = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(reviews)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reviews', methods=['GET'])
def get_all_reviews():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT r.*, u.username, h.name as hotel_name
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        JOIN hotels h ON r.hotel_id = h.id
        ORDER BY r.created_at DESC
        """
        cursor.execute(query)
        reviews = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(reviews)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE reviews 
        SET rating = %s, comment = %s
        WHERE id = %s
        """
        params = (
            data['rating'],
            data['comment'],
            review_id
        )
        
        cursor.execute(query, params)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Review updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Review deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reviews/<int:review_id>/like', methods=['POST'])
def like_review(review_id):
    try:
        data = request.json
        user_id = data.get('user_id', 1)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user already liked this review
        cursor.execute("SELECT id FROM review_likes WHERE review_id = %s AND user_id = %s", (review_id, user_id))
        if cursor.fetchone():
            return jsonify({"error": "Already liked"}), 400
        
        # Add like
        cursor.execute("INSERT INTO review_likes (review_id, user_id) VALUES (%s, %s)", (review_id, user_id))
        conn.commit()
        
        # Get total likes count
        cursor.execute("SELECT COUNT(*) as likes FROM review_likes WHERE review_id = %s", (review_id,))
        likes_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Review liked successfully",
            "likes_count": likes_count
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reviews/user/<int:user_id>', methods=['GET'])
def get_user_reviews(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT r.*, h.name as hotel_name, h.location as hotel_location
        FROM reviews r
        JOIN hotels h ON r.hotel_id = h.id
        WHERE r.user_id = %s
        ORDER BY r.created_at DESC
        """
        cursor.execute(query, (user_id,))
        reviews = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(reviews)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reviews/stats/<int:hotel_id>', methods=['GET'])
def get_review_stats(hotel_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT 
            COUNT(*) as total_reviews,
            AVG(rating) as average_rating,
            SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END) as five_star,
            SUM(CASE WHEN rating = 4 THEN 1 ELSE 0 END) as four_star,
            SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) as three_star,
            SUM(CASE WHEN rating = 2 THEN 1 ELSE 0 END) as two_star,
            SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as one_star
        FROM reviews 
        WHERE hotel_id = %s
        """
        cursor.execute(query, (hotel_id,))
        stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=84, debug=True)