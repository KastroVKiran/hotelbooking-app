# Docker Compose Deployment Guide

## Prerequisites

### 1. EC2 Instance Setup
```bash
# Update system
sudo yum update -y  # For Amazon Linux
# OR
sudo apt update && sudo apt upgrade -y  # For Ubuntu

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 2. Security Group Configuration
Configure your EC2 security group to allow the following ports:
- **Port 80**: HTTP traffic (for main application)
- **Port 8999**: Admin Dashboard (optional, for direct access)
- **Port 22**: SSH access
- **Ports 81-85**: Individual microservices (optional, for debugging)

### 3. Clone Repository
```bash
# Clone your repository
git clone <your-repo-url>
cd hotel-booking-system

# Make scripts executable
chmod +x deployment/*.sh
```

## Deployment Steps

### Step 1: Deploy with Docker Compose
```bash
# Use the public IP compatible docker-compose file
docker-compose -f docker-compose-public.yml up --build -d

# Check if all services are running
docker-compose -f docker-compose-public.yml ps

# View logs
docker-compose -f docker-compose-public.yml logs -f
```

### Step 2: Verify Deployment
```bash
# Check container status
docker ps

# Test health endpoints
curl http://localhost/health
curl http://localhost:81/health
curl http://localhost:82/health
curl http://localhost:83/health
curl http://localhost:84/health
curl http://localhost:85/health
curl http://localhost:8999/health

# Check nginx proxy
curl http://localhost/api/hotels/health
```

### Step 3: Access Application
- **Main Application**: `http://YOUR_EC2_PUBLIC_IP`
- **Admin Dashboard**: `http://YOUR_EC2_PUBLIC_IP/admin`
- **Direct Admin Access**: `http://YOUR_EC2_PUBLIC_IP:8999`

## Database Access

### Method 1: Direct Container Access
```bash
# Access MySQL container
docker exec -it hotel-booking-db mysql -u hotel_user -p
# Password: hotel_pass

# Use the database
USE hotel_booking;
SHOW TABLES;
SELECT * FROM hotels;
```

### Method 2: Port Forwarding (if needed)
```bash
# Forward MySQL port to local machine
ssh -L 3306:localhost:3306 ec2-user@YOUR_EC2_PUBLIC_IP

# Then connect from your local machine
mysql -h localhost -P 3306 -u hotel_user -p
```

### Method 3: MySQL Workbench
- **Host**: YOUR_EC2_PUBLIC_IP
- **Port**: 3306
- **Username**: hotel_user
- **Password**: hotel_pass
- **Database**: hotel_booking

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
sudo netstat -tulpn | grep :80
sudo lsof -i :80

# Kill process if needed
sudo kill -9 <PID>
```

#### 2. Permission Denied
```bash
# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker

# Fix file permissions
sudo chown -R $USER:$USER .
```

#### 3. Service Not Starting
```bash
# Check logs for specific service
docker-compose -f docker-compose-public.yml logs hotel-service

# Restart specific service
docker-compose -f docker-compose-public.yml restart hotel-service

# Rebuild service
docker-compose -f docker-compose-public.yml build hotel-service
docker-compose -f docker-compose-public.yml up -d hotel-service
```

#### 4. Database Connection Issues
```bash
# Check MySQL container
docker-compose -f docker-compose-public.yml logs mysql-db

# Restart MySQL
docker-compose -f docker-compose-public.yml restart mysql-db

# Check database initialization
docker exec -it hotel-booking-db mysql -u root -p
# Password: rootpassword
SHOW DATABASES;
USE hotel_booking;
SHOW TABLES;
```

### Monitoring Commands
```bash
# Monitor all containers
docker stats

# Check container health
docker-compose -f docker-compose-public.yml ps

# View real-time logs
docker-compose -f docker-compose-public.yml logs -f --tail=100

# Check disk usage
docker system df

# Check network
docker network ls
docker network inspect hotel-booking-system_hotel-network
```

## Maintenance

### Backup Database
```bash
# Create backup
docker exec hotel-booking-db mysqldump -u hotel_user -p hotel_booking > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker exec -i hotel-booking-db mysql -u hotel_user -p hotel_booking < backup_file.sql
```

### Update Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose-public.yml down
docker-compose -f docker-compose-public.yml up --build -d

# Or update specific service
docker-compose -f docker-compose-public.yml build hotel-service
docker-compose -f docker-compose-public.yml up -d hotel-service
```

### Cleanup
```bash
# Stop all services
docker-compose -f docker-compose-public.yml down

# Remove volumes (WARNING: This deletes all data)
docker-compose -f docker-compose-public.yml down -v

# Clean up Docker system
docker system prune -a
```

## Performance Optimization

### 1. Resource Limits
Add resource limits to docker-compose-public.yml:
```yaml
services:
  hotel-service:
    # ... other config
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
```

### 2. Nginx Optimization
The nginx configuration includes:
- Gzip compression
- Rate limiting
- Caching for static files
- Security headers

### 3. Database Optimization
```sql
-- Connect to MySQL and run these optimizations
USE hotel_booking;

-- Add indexes for better performance
CREATE INDEX idx_hotels_location ON hotels(location);
CREATE INDEX idx_hotels_price ON hotels(price);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_reviews_rating ON reviews(rating);

-- Optimize tables
OPTIMIZE TABLE hotels, bookings, users, reviews, payments;
```

## Security Considerations

1. **Change Default Passwords**: Update MySQL passwords in production
2. **Use HTTPS**: Configure SSL certificates for production
3. **Firewall Rules**: Restrict access to necessary ports only
4. **Regular Updates**: Keep Docker images and system packages updated
5. **Backup Strategy**: Implement regular database backups

## Default Login Credentials

- **Admin**: admin@luxestay.com / admin123
- **Guest**: guest@example.com / guest123
- **Demo User**: john@example.com / password123

## API Endpoints

All API endpoints are accessible via the nginx proxy:
- `http://YOUR_EC2_PUBLIC_IP/api/hotels` - Hotel listings
- `http://YOUR_EC2_PUBLIC_IP/api/bookings` - Booking management
- `http://YOUR_EC2_PUBLIC_IP/api/auth` - Authentication
- `http://YOUR_EC2_PUBLIC_IP/api/reviews` - Reviews
- `http://YOUR_EC2_PUBLIC_IP/api/payments` - Payments