from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
import hashlib
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

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

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "user-service"})

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (data['email'],))
        if cursor.fetchone():
            return jsonify({"error": "User already exists"}), 400
        
        # Create new user
        hashed_password = hash_password(data['password'])
        query = """
        INSERT INTO users (username, email, password_hash, phone, role)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            data['username'],
            data['email'],
            hashed_password,
            data.get('phone', ''),
            data.get('role', 'user')
        )
        
        cursor.execute(query, params)
        conn.commit()
        user_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        token = generate_token(user_id)
        
        return jsonify({
            "user_id": user_id,
            "username": data['username'],
            "email": data['email'],
            "token": token,
            "message": "User registered successfully"
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Find user by email
        cursor.execute("SELECT * FROM users WHERE email = %s", (data['email'],))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Verify password
        hashed_password = hash_password(data['password'])
        if user['password_hash'] != hashed_password:
            return jsonify({"error": "Invalid credentials"}), 401
        
        cursor.close()
        conn.close()
        
        token = generate_token(user['id'])
        
        return jsonify({
            "user_id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "role": user['role'],
            "token": token,
            "message": "Login successful"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, username, email, phone, role, created_at FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if user:
            return jsonify(user)
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE users 
        SET username = %s, phone = %s
        WHERE id = %s
        """
        params = (
            data['username'],
            data.get('phone', ''),
            user_id
        )
        
        cursor.execute(query, params)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"message": "User updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, username, email, phone, role, created_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/verify', methods=['POST'])
def verify_token():
    try:
        data = request.json
        token = data.get('token')
        
        if not token:
            return jsonify({"error": "Token required"}), 400
        
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, username, email, role FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if user:
            return jsonify({
                "valid": True,
                "user": user
            })
        else:
            return jsonify({"valid": False, "error": "User not found"}), 404
    except jwt.ExpiredSignatureError:
        return jsonify({"valid": False, "error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"valid": False, "error": "Invalid token"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=83, debug=True)