from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import mysql.connector
import os
import requests
from datetime import datetime, timedelta

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

# Service URLs
SERVICE_URLS = {
    'hotel': 'http://hotel-service:81',
    'booking': 'http://booking-service:82',
    'user': 'http://user-service:83',
    'review': 'http://review-service:84',
    'payment': 'http://payment-service:85'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "admin-dashboard"})

@app.route('/', methods=['GET'])
def admin_dashboard():
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hotel Booking - Admin Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen">
            <!-- Header -->
            <header class="bg-white shadow-sm border-b">
                <div class="max-w-7xl mx-auto px-4 py-4">
                    <h1 class="text-2xl font-bold text-gray-900">Hotel Booking Admin Dashboard</h1>
                </div>
            </header>
            
            <!-- Dashboard Content -->
            <main class="max-w-7xl mx-auto px-4 py-8">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <!-- Stats Cards -->
                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-600">Total Hotels</p>
                                <p class="text-2xl font-bold text-blue-600" id="totalHotels">-</p>
                            </div>
                            <div class="bg-blue-100 p-3 rounded-full">
                                <i data-lucide="building" class="h-6 w-6 text-blue-600"></i>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-600">Total Bookings</p>
                                <p class="text-2xl font-bold text-green-600" id="totalBookings">-</p>
                            </div>
                            <div class="bg-green-100 p-3 rounded-full">
                                <i data-lucide="calendar" class="h-6 w-6 text-green-600"></i>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-600">Total Users</p>
                                <p class="text-2xl font-bold text-purple-600" id="totalUsers">-</p>
                            </div>
                            <div class="bg-purple-100 p-3 rounded-full">
                                <i data-lucide="users" class="h-6 w-6 text-purple-600"></i>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-600">Revenue</p>
                                <p class="text-2xl font-bold text-orange-600" id="totalRevenue">-</p>
                            </div>
                            <div class="bg-orange-100 p-3 rounded-full">
                                <i data-lucide="dollar-sign" class="h-6 w-6 text-orange-600"></i>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Service Status -->
                <div class="bg-white rounded-lg shadow mb-8">
                    <div class="px-6 py-4 border-b">
                        <h2 class="text-lg font-semibold">Service Status</h2>
                    </div>
                    <div class="p-6">
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" id="serviceStatus">
                            <!-- Service status will be populated by JavaScript -->
                        </div>
                    </div>
                </div>
                
                <!-- Recent Activity -->
                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b">
                        <h2 class="text-lg font-semibold">Recent Activity</h2>
                    </div>
                    <div class="p-6">
                        <div class="space-y-4" id="recentActivity">
                            <!-- Recent activity will be populated by JavaScript -->
                        </div>
                    </div>
                </div>
            </main>
        </div>
        
        <script>
            // Initialize Lucide icons
            lucide.createIcons();
            
            // Load dashboard data
            async function loadDashboardData() {
                try {
                    // Load stats
                    const statsResponse = await fetch('/api/admin/stats');
                    const stats = await statsResponse.json();
                    
                    document.getElementById('totalHotels').textContent = stats.hotels || '0';
                    document.getElementById('totalBookings').textContent = stats.bookings || '0';
                    document.getElementById('totalUsers').textContent = stats.users || '0';
                    document.getElementById('totalRevenue').textContent = '$' + (stats.revenue || '0');
                    
                    // Load service status
                    const serviceResponse = await fetch('/api/admin/services');
                    const services = await serviceResponse.json();
                    
                    const serviceStatusContainer = document.getElementById('serviceStatus');
                    serviceStatusContainer.innerHTML = '';
                    
                    services.forEach(service => {
                        const statusColor = service.status === 'healthy' ? 'green' : 'red';
                        const statusDiv = document.createElement('div');
                        statusDiv.className = 'flex items-center justify-between p-3 border rounded-lg';
                        statusDiv.innerHTML = `
                            <span class="font-medium">${service.name}</span>
                            <span class="px-2 py-1 text-xs rounded-full bg-${statusColor}-100 text-${statusColor}-800">
                                ${service.status}
                            </span>
                        `;
                        serviceStatusContainer.appendChild(statusDiv);
                    });
                    
                } catch (error) {
                    console.error('Error loading dashboard data:', error);
                }
            }
            
            // Load data on page load
            loadDashboardData();
            
            // Refresh data every 30 seconds
            setInterval(loadDashboardData, 30000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get counts from different tables
        stats = {}
        
        # Hotels count
        cursor.execute("SELECT COUNT(*) as count FROM hotels")
        stats['hotels'] = cursor.fetchone()['count']
        
        # Bookings count
        cursor.execute("SELECT COUNT(*) as count FROM bookings")
        stats['bookings'] = cursor.fetchone()['count']
        
        # Users count
        cursor.execute("SELECT COUNT(*) as count FROM users")
        stats['users'] = cursor.fetchone()['count']
        
        # Revenue
        cursor.execute("SELECT SUM(amount) as total FROM payments WHERE amount > 0")
        result = cursor.fetchone()
        stats['revenue'] = result['total'] if result['total'] else 0
        
        cursor.close()
        conn.close()
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/services', methods=['GET'])
def get_service_status():
    services = []
    
    for service_name, service_url in SERVICE_URLS.items():
        try:
            response = requests.get(f"{service_url}/health", timeout=5)
            if response.status_code == 200:
                status = "healthy"
            else:
                status = "unhealthy"
        except:
            status = "unreachable"
        
        services.append({
            "name": service_name.title() + " Service",
            "status": status,
            "url": service_url
        })
    
    return jsonify(services)

@app.route('/api/admin/bookings', methods=['GET'])
def get_admin_bookings():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT b.*, h.name as hotel_name, u.username
        FROM bookings b
        JOIN hotels h ON b.hotel_id = h.id
        JOIN users u ON b.user_id = u.id
        ORDER BY b.created_at DESC
        LIMIT 50
        """
        cursor.execute(query)
        bookings = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(bookings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/users', methods=['GET'])
def get_admin_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT id, username, email, phone, role, created_at
        FROM users
        ORDER BY created_at DESC
        """
        cursor.execute(query)
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/revenue', methods=['GET'])
def get_revenue_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get daily revenue for the last 30 days
        query = """
        SELECT DATE(created_at) as date, SUM(amount) as revenue
        FROM payments
        WHERE amount > 0 AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        GROUP BY DATE(created_at)
        ORDER BY date DESC
        """
        cursor.execute(query)
        revenue_data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(revenue_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8999, debug=True)