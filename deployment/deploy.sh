#!/bin/bash

# Hotel Booking System Deployment Script

set -e

echo "🏨 Hotel Booking System Deployment Script"
echo "=========================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for deployment
wait_for_deployment() {
    local deployment=$1
    local namespace=${2:-default}
    echo "⏳ Waiting for deployment $deployment to be ready..."
    kubectl wait --for=condition=available deployment/$deployment -n $namespace --timeout=300s
}

# Check prerequisites
echo "🔍 Checking prerequisites..."
if ! command_exists docker; then
    echo "❌ Docker is not installed"
    exit 1
fi

if ! command_exists kubectl; then
    echo "❌ kubectl is not installed"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create namespace
echo "📁 Creating namespace..."
kubectl apply -f k8s/namespace.yaml

# Deploy MySQL database
echo "🗄️ Deploying MySQL database..."
kubectl apply -f k8s/mysql-deployment.yaml
wait_for_deployment mysql-db hotel-booking

# Deploy microservices
echo "🚀 Deploying microservices..."
kubectl apply -f k8s/hotel-service.yaml
kubectl apply -f k8s/booking-service.yaml
kubectl apply -f k8s/user-service.yaml
kubectl apply -f k8s/review-service.yaml
kubectl apply -f k8s/payment-service.yaml
kubectl apply -f k8s/admin-dashboard.yaml

# Wait for all services to be ready
echo "⏳ Waiting for all services to be ready..."
wait_for_deployment hotel-service hotel-booking
wait_for_deployment booking-service hotel-booking
wait_for_deployment user-service hotel-booking
wait_for_deployment review-service hotel-booking
wait_for_deployment payment-service hotel-booking
wait_for_deployment admin-dashboard hotel-booking

# Deploy ingress controller
echo "🌐 Deploying ingress controller..."
kubectl apply -f k8s/ingress-controller.yaml

echo "⏳ Waiting for ingress controller to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/name=ingress-nginx \
  --timeout=300s

# Deploy ingress rules
echo "📋 Deploying ingress rules..."
kubectl apply -f k8s/ingress.yaml

# Get service information
echo "📊 Getting service information..."
echo ""
echo "🏨 Hotel Booking System is now deployed!"
echo "=========================================="
echo ""
echo "📍 Services Status:"
kubectl get deployments -n hotel-booking
echo ""
echo "🌐 Access URLs:"
EXTERNAL_IP=$(kubectl get service ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
if [ "$EXTERNAL_IP" != "pending" ] && [ "$EXTERNAL_IP" != "" ]; then
    echo "   Frontend: http://$EXTERNAL_IP"
    echo "   Admin Dashboard: http://$EXTERNAL_IP/admin"
    echo "   API Gateway: http://$EXTERNAL_IP/api"
else
    echo "   External IP is pending. Use port-forward for testing:"
    echo "   kubectl port-forward service/admin-dashboard 8999:8999 -n hotel-booking"
fi
echo ""
echo "🗄️ Database Access:"
echo "   kubectl port-forward service/mysql-db 3306:3306 -n hotel-booking"
echo "   mysql -h localhost -P 3306 -u hotel_user -p"
echo ""
echo "📋 Useful Commands:"
echo "   kubectl get all -n hotel-booking"
echo "   kubectl logs -f deployment/<service-name> -n hotel-booking"
echo "   kubectl describe ingress hotel-booking-ingress -n hotel-booking"
echo ""
echo "✅ Deployment completed successfully!"