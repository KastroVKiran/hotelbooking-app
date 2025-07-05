-- Create database if not exists
CREATE DATABASE IF NOT EXISTS hotel_booking;
USE hotel_booking;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Hotels table
CREATE TABLE IF NOT EXISTS hotels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    description TEXT,
    rooms INT NOT NULL DEFAULT 0,
    price DECIMAL(10, 2) NOT NULL,
    amenities TEXT,
    image VARCHAR(500),
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Bookings table
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_ref VARCHAR(50) UNIQUE NOT NULL,
    hotel_id INT NOT NULL,
    user_id INT NOT NULL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    guests INT NOT NULL DEFAULT 1,
    room_type VARCHAR(100),
    special_requests TEXT,
    total_amount DECIMAL(10, 2) NOT NULL,
    status ENUM('pending', 'confirmed', 'cancelled', 'completed') DEFAULT 'pending',
    payment_status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (hotel_id) REFERENCES hotels(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_id INT NOT NULL,
    user_id INT NOT NULL,
    booking_id INT,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (hotel_id) REFERENCES hotels(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);

-- Review likes table
CREATE TABLE IF NOT EXISTS review_likes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    review_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES reviews(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY unique_review_user (review_id, user_id)
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    booking_id INT,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(50),
    card_last_four VARCHAR(4),
    payment_status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
    gateway_response TEXT,
    refund_for INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id),
    FOREIGN KEY (refund_for) REFERENCES payments(id)
);

-- Insert sample data
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@luxestay.com', SHA2('admin123', 256), 'admin'),
('john_doe', 'john@example.com', SHA2('password123', 256), 'user'),
('jane_smith', 'jane@example.com', SHA2('password123', 256), 'user'),
('guest_user', 'guest@example.com', SHA2('guest123', 256), 'user');

INSERT INTO hotels (name, location, description, rooms, price, amenities, image, status) VALUES
('Grand Palace Hotel', 'New York, NY', 'Luxury hotel in the heart of Manhattan with exceptional service and stunning city views.', 150, 299.00, 'WiFi,Parking,Restaurant,Spa,Gym,Pool', 'https://images.pexels.com/photos/258154/pexels-photo-258154.jpeg?auto=compress&cs=tinysrgb&w=400', 'active'),
('Oceanview Resort', 'Miami, FL', 'Beachfront resort with stunning ocean views and world-class amenities.', 200, 399.00, 'WiFi,Pool,Beach Access,Restaurant,Spa,Water Sports', 'https://images.pexels.com/photos/2034335/pexels-photo-2034335.jpeg?auto=compress&cs=tinysrgb&w=400', 'active'),
('Mountain Lodge', 'Denver, CO', 'Cozy mountain retreat perfect for outdoor enthusiasts and nature lovers.', 80, 249.00, 'WiFi,Fireplace,Hiking,Restaurant,Ski Access,Hot Tub', 'https://images.pexels.com/photos/1134176/pexels-photo-1134176.jpeg?auto=compress&cs=tinysrgb&w=400', 'active'),
('City Center Hotel', 'Chicago, IL', 'Modern hotel located in downtown Chicago with easy access to attractions.', 120, 199.00, 'WiFi,Parking,Restaurant,Gym,Business Center', 'https://images.pexels.com/photos/1001965/pexels-photo-1001965.jpeg?auto=compress&cs=tinysrgb&w=400', 'active'),
('Sunset Villa', 'San Diego, CA', 'Boutique hotel with panoramic views and personalized service.', 60, 449.00, 'WiFi,Pool,Ocean View,Restaurant,Spa,Concierge', 'https://images.pexels.com/photos/2373201/pexels-photo-2373201.jpeg?auto=compress&cs=tinysrgb&w=400', 'active');

INSERT INTO bookings (booking_ref, hotel_id, user_id, check_in, check_out, guests, room_type, total_amount, status, payment_status) VALUES
('BK123456', 1, 2, '2024-02-01', '2024-02-05', 2, 'deluxe', 1196.00, 'confirmed', 'completed'),
('BK123457', 2, 3, '2024-02-10', '2024-02-14', 4, 'suite', 1596.00, 'confirmed', 'completed'),
('BK123458', 3, 4, '2024-02-15', '2024-02-18', 2, 'standard', 747.00, 'confirmed', 'completed');

INSERT INTO reviews (hotel_id, user_id, booking_id, rating, comment) VALUES
(1, 2, 1, 5, 'Amazing stay! The service was exceptional and the room was beautiful. Will definitely come back.'),
(2, 3, 2, 4, 'Great location with stunning ocean views. The breakfast was fantastic, though the WiFi could be better.'),
(3, 4, 3, 5, 'Perfect for our mountain getaway. The staff was friendly and the hiking trails were amazing.');

INSERT INTO payments (transaction_id, booking_id, amount, currency, payment_method, card_last_four, payment_status, gateway_response) VALUES
('TXN001234567890', 1, 1196.00, 'USD', 'credit_card', '1234', 'completed', '{"status": "success", "gateway": "stripe"}'),
('TXN001234567891', 2, 1596.00, 'USD', 'credit_card', '5678', 'completed', '{"status": "success", "gateway": "stripe"}'),
('TXN001234567892', 3, 747.00, 'USD', 'credit_card', '9012', 'completed', '{"status": "success", "gateway": "stripe"}');

-- Create indexes for better performance
CREATE INDEX idx_bookings_hotel_id ON bookings(hotel_id);
CREATE INDEX idx_bookings_user_id ON bookings(user_id);
CREATE INDEX idx_bookings_dates ON bookings(check_in, check_out);
CREATE INDEX idx_reviews_hotel_id ON reviews(hotel_id);
CREATE INDEX idx_reviews_user_id ON reviews(user_id);
CREATE INDEX idx_payments_booking_id ON payments(booking_id);
CREATE INDEX idx_payments_transaction_id ON payments(transaction_id);