# Docker Compose Commands Reference

## Basic Operations

### Start Services
```bash
# Start all services in background
docker-compose up -d

# Start with build (rebuild images)
docker-compose up --build -d

# Start specific service
docker-compose up -d hotel-service

# View logs while starting
docker-compose up --build
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (delete database data)
docker-compose down -v

# Stop specific service
docker-compose stop hotel-service
```

### View Status and Logs
```bash
# Check running containers
docker-compose ps

# View all logs
docker-compose logs

# View logs for specific service
docker-compose logs hotel-service

# Follow logs in real-time
docker-compose logs -f

# Follow logs for specific service
docker-compose logs -f admin-dashboard
```

### Database Operations
```bash
# Access MySQL container
docker-compose exec mysql-db mysql -u hotel_user -p

# Backup database
docker-compose exec mysql-db mysqldump -u hotel_user -p hotel_booking > backup.sql

# Restore database
docker-compose exec -T mysql-db mysql -u hotel_user -p hotel_booking < backup.sql

# View database files
docker-compose exec mysql-db ls -la /var/lib/mysql
```

### Service Management
```bash
# Restart specific service
docker-compose restart hotel-service

# Rebuild specific service
docker-compose build hotel-service
docker-compose up -d hotel-service

# Scale service (not applicable for this setup)
docker-compose up -d --scale hotel-service=2

# Update service
docker-compose pull hotel-service
docker-compose up -d hotel-service
```

### Troubleshooting
```bash
# View container processes
docker-compose top

# Execute command in running container
docker-compose exec hotel-service /bin/bash

# Check container configuration
docker-compose config

# Remove orphaned containers
docker-compose down --remove-orphans

# View resource usage
docker stats $(docker-compose ps -q)
```

### Development Commands
```bash
# Build without cache
docker-compose build --no-cache

# Recreate containers
docker-compose up -d --force-recreate

# Pull latest images
docker-compose pull

# Check for updates
docker-compose config --services | xargs -I {} docker-compose pull {}
```

## Service-Specific Operations

### Hotel Service (Port 81)
```bash
# Test health endpoint
curl http://localhost:81/health

# View logs
docker-compose logs -f hotel-service

# Restart service
docker-compose restart hotel-service
```

### Booking Service (Port 82)
```bash
# Test health endpoint
curl http://localhost:82/health

# Access container
docker-compose exec booking-service /bin/bash
```

### User Service (Port 83)
```bash
# Test health endpoint
curl http://localhost:83/health

# Check environment variables
docker-compose exec user-service env
```

### Review Service (Port 84)
```bash
# Test health endpoint
curl http://localhost:84/health

# View real-time logs
docker-compose logs -f review-service
```

### Payment Service (Port 85)
```bash
# Test health endpoint
curl http://localhost:85/health

# Debug service
docker-compose exec payment-service python -c "import mysql.connector; print('MySQL connector working')"
```

### Admin Dashboard (Port 8999)
```bash
# Access admin dashboard
curl http://localhost:8999/health

# View logs
docker-compose logs -f admin-dashboard
```

## Maintenance Commands

### Cleanup
```bash
# Remove stopped containers
docker-compose rm

# Remove all containers, networks, and images
docker-compose down --rmi all

# Remove volumes (WARNING: This will delete all data)
docker-compose down -v --rmi all

# Clean up Docker system
docker system prune -a
```

### Monitoring
```bash
# Monitor resource usage
docker stats $(docker-compose ps -q)

# Check disk usage
docker system df

# Monitor logs
docker-compose logs -f --tail=100
```