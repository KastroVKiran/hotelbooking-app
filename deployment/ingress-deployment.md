# Ingress Controller Deployment Guide

## Overview
This guide covers deploying an Ingress Controller to provide external access to your Hotel Booking System running on Kubernetes. We'll use NGINX Ingress Controller which is widely supported and feature-rich.

## Prerequisites

1. **Kubernetes Cluster**: EKS cluster should be running
2. **kubectl**: Configured to access your cluster
3. **Application Deployed**: All microservices should be deployed and running

## Part 1: Deploy NGINX Ingress Controller

### Step 1: Deploy Ingress Controller
```bash
# Apply the ingress controller configuration
kubectl apply -f k8s/ingress-controller.yaml

# Verify the ingress controller namespace
kubectl get namespace ingress-nginx

# Check if ingress controller pods are running
kubectl get pods -n ingress-nginx
```

### Step 2: Wait for Ingress Controller to be Ready
```bash
# Wait for the ingress controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/name=ingress-nginx \
  --timeout=300s

# Check the ingress controller service
kubectl get service ingress-nginx-controller -n ingress-nginx
```

### Step 3: Get External IP/Hostname
```bash
# Get the external IP or hostname
kubectl get service ingress-nginx-controller -n ingress-nginx

# For AWS EKS, you'll get a LoadBalancer hostname like:
# a1234567890abcdef-1234567890.us-east-1.elb.amazonaws.com

# Save this for later use
export INGRESS_HOST=$(kubectl get service ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "Ingress Host: $INGRESS_HOST"
```

## Part 2: Deploy Application Ingress Rules

### Step 1: Deploy Ingress Configuration
```bash
# Apply the ingress rules for your application
kubectl apply -f k8s/ingress.yaml

# Verify ingress is created
kubectl get ingress -n hotel-booking

# Check ingress details
kubectl describe ingress hotel-booking-ingress -n hotel-booking
```

### Step 2: Configure DNS (Optional)
For production, you would configure your domain DNS to point to the LoadBalancer hostname. For testing, you can use the LoadBalancer hostname directly or add an entry to your local hosts file.

#### Option A: Use LoadBalancer Hostname Directly
```bash
# Access your application using the LoadBalancer hostname
echo "Application URL: http://$INGRESS_HOST"
echo "Admin Dashboard: http://$INGRESS_HOST/admin"
echo "API Base URL: http://$INGRESS_HOST/api"
```

#### Option B: Local Hosts File (for testing)
```bash
# Add entry to /etc/hosts (Linux/Mac) or C:\Windows\System32\drivers\etc\hosts (Windows)
echo "$INGRESS_HOST hotel-booking.local" | sudo tee -a /etc/hosts

# Then access via:
# http://hotel-booking.local
# http://hotel-booking.local/admin
```

## Part 3: Verify Ingress Deployment

### Step 1: Check Ingress Status
```bash
# Check if ingress has an IP/hostname assigned
kubectl get ingress hotel-booking-ingress -n hotel-booking

# The output should show something like:
# NAME                    CLASS   HOSTS                 ADDRESS                                    PORTS   AGE
# hotel-booking-ingress   nginx   hotel-booking.local   a123...elb.amazonaws.com                   80      5m
```

### Step 2: Test Ingress Endpoints
```bash
# Test main application
curl -H "Host: hotel-booking.local" http://$INGRESS_HOST/

# Test admin dashboard
curl -H "Host: hotel-booking.local" http://$INGRESS_HOST/admin

# Test API endpoints
curl -H "Host: hotel-booking.local" http://$INGRESS_HOST/api/hotels/health
curl -H "Host: hotel-booking.local" http://$INGRESS_HOST/api/bookings/health
curl -H "Host: hotel-booking.local" http://$INGRESS_HOST/api/auth/health
curl -H "Host: hotel-booking.local" http://$INGRESS_HOST/api/reviews/health
curl -H "Host: hotel-booking.local" http://$INGRESS_HOST/api/payments/health
```

### Step 3: Test from Browser
1. Open browser and navigate to `http://$INGRESS_HOST` (replace with actual hostname)
2. You should see the Hotel Booking Admin Dashboard
3. Test different routes:
   - `/admin` - Admin Dashboard
   - `/api/hotels` - Hotel Service API
   - `/api/bookings` - Booking Service API

## Part 4: Advanced Ingress Configuration

### SSL/TLS Configuration (Production)
For production, you should enable HTTPS. Here's how to configure SSL:

```yaml
# Add to your ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: hotel-booking-ingress-ssl
  namespace: hotel-booking
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - yourdomain.com
    secretName: hotel-booking-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      # ... your paths here
```

### Rate Limiting
The current ingress configuration includes rate limiting:
```yaml
annotations:
  nginx.ingress.kubernetes.io/rate-limit: "100"
  nginx.ingress.kubernetes.io/rate-limit-window: "1m"
```

### CORS Configuration
CORS is already configured in the ingress:
```yaml
annotations:
  nginx.ingress.kubernetes.io/cors-allow-origin: "*"
  nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, DELETE, OPTIONS"
  nginx.ingress.kubernetes.io/enable-cors: "true"
```

## Part 5: Monitoring and Troubleshooting

### Check Ingress Controller Logs
```bash
# Get ingress controller pod name
kubectl get pods -n ingress-nginx

# View logs
kubectl logs -f <ingress-controller-pod-name> -n ingress-nginx

# Or use label selector
kubectl logs -f -l app.kubernetes.io/name=ingress-nginx -n ingress-nginx
```

### Debug Ingress Issues
```bash
# Check ingress controller service
kubectl describe service ingress-nginx-controller -n ingress-nginx

# Check ingress rules
kubectl describe ingress hotel-booking-ingress -n hotel-booking

# Check backend services
kubectl get endpoints -n hotel-booking

# Test service connectivity from ingress controller
kubectl exec -it deployment/ingress-nginx-controller -n ingress-nginx -- curl http://hotel-service.hotel-booking.svc.cluster.local:81/health
```

### Common Issues and Solutions

#### 1. Ingress Controller Not Getting External IP
```bash
# Check if LoadBalancer service is pending
kubectl get service ingress-nginx-controller -n ingress-nginx

# For AWS EKS, ensure your nodes have proper IAM roles
# Check AWS Load Balancer Controller is installed if using ALB
```

#### 2. 404 Not Found Errors
```bash
# Check if backend services are running
kubectl get pods -n hotel-booking

# Check service endpoints
kubectl get endpoints -n hotel-booking

# Verify ingress path configuration
kubectl describe ingress hotel-booking-ingress -n hotel-booking
```

#### 3. Backend Service Unreachable
```bash
# Test service connectivity
kubectl exec -it deployment/hotel-service -n hotel-booking -- curl http://mysql-db:3306

# Check service DNS resolution
kubectl exec -it deployment/hotel-service -n hotel-booking -- nslookup hotel-service.hotel-booking.svc.cluster.local
```

## Part 6: Access Your Application

### Public Access URLs
Once ingress is deployed and working, your application will be accessible at:

- **Main Application**: `http://<INGRESS_HOST>/`
- **Admin Dashboard**: `http://<INGRESS_HOST>/admin`
- **Hotel API**: `http://<INGRESS_HOST>/api/hotels`
- **Booking API**: `http://<INGRESS_HOST>/api/bookings`
- **User API**: `http://<INGRESS_HOST>/api/auth`
- **Review API**: `http://<INGRESS_HOST>/api/reviews`
- **Payment API**: `http://<INGRESS_HOST>/api/payments`

### Default Login Credentials
- **Admin**: admin@luxestay.com / admin123
- **Guest**: guest@example.com / guest123

## Part 7: Cleanup

### Remove Ingress Rules
```bash
kubectl delete -f k8s/ingress.yaml
```

### Remove Ingress Controller
```bash
kubectl delete -f k8s/ingress-controller.yaml
kubectl delete namespace ingress-nginx
```

## Part 8: Production Considerations

1. **SSL/TLS**: Configure HTTPS with valid certificates
2. **Domain Name**: Use a proper domain name instead of IP
3. **Rate Limiting**: Adjust rate limits based on your needs
4. **Monitoring**: Set up monitoring for ingress controller
5. **Backup**: Regular backup of ingress configurations
6. **Security**: Implement proper security headers and policies

This completes the Ingress Controller deployment. Your Hotel Booking System should now be accessible via the internet through the LoadBalancer hostname/IP provided by the ingress controller.