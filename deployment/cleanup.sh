#!/bin/bash

# Hotel Booking System Cleanup Script

set -e

echo "🧹 Hotel Booking System Cleanup Script"
echo "======================================"

# Function to check if namespace exists
namespace_exists() {
    kubectl get namespace "$1" >/dev/null 2>&1
}

# Delete ingress
echo "🌐 Removing ingress..."
kubectl delete -f k8s/ingress.yaml --ignore-not-found=true

# Delete services
echo "🚀 Removing microservices..."
kubectl delete -f k8s/admin-dashboard.yaml --ignore-not-found=true
kubectl delete -f k8s/payment-service.yaml --ignore-not-found=true
kubectl delete -f k8s/review-service.yaml --ignore-not-found=true
kubectl delete -f k8s/user-service.yaml --ignore-not-found=true
kubectl delete -f k8s/booking-service.yaml --ignore-not-found=true
kubectl delete -f k8s/hotel-service.yaml --ignore-not-found=true

# Delete database
echo "🗄️ Removing MySQL database..."
kubectl delete -f k8s/mysql-deployment.yaml --ignore-not-found=true

# Delete namespace
echo "📁 Removing namespace..."
if namespace_exists hotel-booking; then
    kubectl delete namespace hotel-booking
fi

# Delete ingress controller (optional)
read -p "Do you want to remove the ingress controller? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌐 Removing ingress controller..."
    kubectl delete -f k8s/ingress-controller.yaml --ignore-not-found=true
    kubectl delete namespace ingress-nginx --ignore-not-found=true
fi

echo ""
echo "✅ Cleanup completed successfully!"
echo "   All hotel booking system resources have been removed."