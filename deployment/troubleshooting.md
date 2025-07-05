# Troubleshooting Guide

## Common Issues and Solutions

### 1. Database Connection Issues
```bash
# Check MySQL pod status
kubectl get pods -n hotel-booking | grep mysql

# Check MySQL logs
kubectl logs -f deployment/mysql-db -n hotel-booking

# Access MySQL pod directly
kubectl exec -it deployment/mysql-db -n hotel-booking -- mysql -u hotel_user -p

# Reset MySQL pod
kubectl delete pod -l app=mysql-db -n hotel-booking
```

### 2. Service Communication Issues
```bash
# Check service endpoints
kubectl get endpoints -n hotel-booking

# Test service connectivity
kubectl exec -it deployment/hotel-service -n hotel-booking -- curl http://mysql-db:3306

# Check service DNS resolution
kubectl exec -it deployment/hotel-service -n hotel-booking -- nslookup mysql-db
```

### 3. Ingress Issues
```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress configuration
kubectl describe ingress hotel-booking-ingress -n hotel-booking

# Check ingress controller logs
kubectl logs -f deployment/ingress-nginx-controller -n ingress-nginx
```

### 4. Image Pull Issues
```bash
# Check image pull secrets
kubectl get secrets -n hotel-booking

# Update deployment with latest image
kubectl set image deployment/hotel-service hotel-service=hotel-booking/hotel-service:latest -n hotel-booking

# Force pod restart
kubectl rollout restart deployment/hotel-service -n hotel-booking
```

### 5. Resource Issues
```bash
# Check resource usage
kubectl top nodes
kubectl top pods -n hotel-booking

# Check resource limits
kubectl describe pod <pod-name> -n hotel-booking

# Scale deployment
kubectl scale deployment hotel-service --replicas=3 -n hotel-booking
```

## Monitoring Commands

```bash
# Watch pod status
kubectl get pods -n hotel-booking -w

# Monitor logs in real-time
kubectl logs -f deployment/hotel-service -n hotel-booking --tail=100

# Check events
kubectl get events -n hotel-booking --sort-by='.lastTimestamp'

# Health check endpoints
curl http://<ingress-ip>/api/hotels/health
curl http://<ingress-ip>/api/bookings/health
curl http://<ingress-ip>/api/auth/health
curl http://<ingress-ip>/api/reviews/health
curl http://<ingress-ip>/api/payments/health
```