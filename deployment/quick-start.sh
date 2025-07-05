#!/bin/bash

# Hotel Booking System Quick Start Script
# This script will help you deploy the application quickly

set -e

echo "🏨 Hotel Booking System Quick Start"
echo "==================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get public IP
get_public_ip() {
    curl -s http://checkip.amazonaws.com/ || curl -s http://ipinfo.io/ip || echo "Unable to detect public IP"
}

# Check prerequisites
echo "🔍 Checking prerequisites..."
if ! command_exists docker; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command_exists docker-compose; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Get deployment type
echo ""
echo "Select deployment type:"
echo "1) Docker Compose (Local/EC2)"
echo "2) Kubernetes (EKS)"
echo "3) Kubernetes with Ingress"
read -p "Enter your choice (1-3): " DEPLOY_TYPE

case $DEPLOY_TYPE in
    1)
        echo "🐳 Starting Docker Compose deployment..."
        
        # Check if we're on EC2 or local
        PUBLIC_IP=$(get_public_ip)
        echo "📍 Detected public IP: $PUBLIC_IP"
        
        # Create nginx directory if it doesn't exist
        mkdir -p nginx
        
        # Start services
        echo "🚀 Starting all services..."
        docker-compose -f docker-compose-public.yml up --build -d
        
        # Wait for services to be ready
        echo "⏳ Waiting for services to start..."
        sleep 30
        
        # Check service health
        echo "🔍 Checking service health..."
        for port in 81 82 83 84 85 8999; do
            if curl -s http://localhost:$port/health > /dev/null; then
                echo "✅ Service on port $port is healthy"
            else
                echo "⚠️  Service on port $port is not responding"
            fi
        done
        
        echo ""
        echo "🎉 Deployment completed!"
        echo "📍 Access your application at:"
        echo "   Main Application: http://$PUBLIC_IP"
        echo "   Admin Dashboard: http://$PUBLIC_IP/admin"
        echo "   Direct Admin Access: http://$PUBLIC_IP:8999"
        echo ""
        echo "🔑 Default login credentials:"
        echo "   Admin: admin@luxestay.com / admin123"
        echo "   Guest: guest@example.com / guest123"
        ;;
        
    2)
        echo "☸️  Starting Kubernetes deployment..."
        
        if ! command_exists kubectl; then
            echo "❌ kubectl is not installed. Please install kubectl first."
            exit 1
        fi
        
        # Check if cluster is accessible
        if ! kubectl cluster-info > /dev/null 2>&1; then
            echo "❌ Cannot connect to Kubernetes cluster. Please configure kubectl."
            exit 1
        fi
        
        echo "🚀 Deploying to Kubernetes..."
        ./deployment/deploy.sh
        ;;
        
    3)
        echo "🌐 Starting Kubernetes deployment with Ingress..."
        
        if ! command_exists kubectl; then
            echo "❌ kubectl is not installed. Please install kubectl first."
            exit 1
        fi
        
        # Check if cluster is accessible
        if ! kubectl cluster-info > /dev/null 2>&1; then
            echo "❌ Cannot connect to Kubernetes cluster. Please configure kubectl."
            exit 1
        fi
        
        echo "🚀 Deploying to Kubernetes with Ingress..."
        ./deployment/deploy.sh
        
        echo "🌐 Getting ingress information..."
        sleep 10
        INGRESS_HOST=$(kubectl get service ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "pending")
        
        if [ "$INGRESS_HOST" != "pending" ] && [ "$INGRESS_HOST" != "" ]; then
            echo ""
            echo "🎉 Deployment completed!"
            echo "📍 Access your application at:"
            echo "   Main Application: http://$INGRESS_HOST"
            echo "   Admin Dashboard: http://$INGRESS_HOST/admin"
            echo "   API Gateway: http://$INGRESS_HOST/api"
        else
            echo ""
            echo "⏳ Ingress external IP is still pending. Please wait a few minutes and check:"
            echo "   kubectl get service ingress-nginx-controller -n ingress-nginx"
        fi
        ;;
        
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "📚 For more information, check the deployment guides in the deployment/ directory"
echo "🔧 For troubleshooting, see deployment/troubleshooting.md"