# Jenkins CI/CD Setup for Hotel Booking System

## Prerequisites

### 1. AWS EKS Cluster Setup
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Create EKS cluster
eksctl create cluster \
  --name hotel-booking-cluster \
  --version 1.27 \
  --region us-east-1 \
  --nodegroup-name hotel-booking-nodes \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 4 \
  --managed

# Update kubeconfig
aws eks update-kubeconfig --region us-east-1 --name hotel-booking-cluster
```

### 2. Jenkins Configuration

#### Install Required Plugins
- Docker Pipeline
- Kubernetes CLI
- AWS Steps
- Pipeline: Stage View
- Blue Ocean (optional)

#### Configure Credentials
1. **dockerhub-creds**: Username/Password for DockerHub
2. **aws-creds**: AWS Access Key ID and Secret Access Key

### 3. Jenkins Pipeline Jobs

Create the following Jenkins jobs:

#### Master Pipeline Job
- **Job Name**: `hotel-booking-master-pipeline`
- **Type**: Pipeline
- **Pipeline Script**: From SCM
- **Repository URL**: Your Git repository
- **Script Path**: `jenkins/master-pipeline.groovy`

#### Individual Service Jobs
1. `hotel-service-pipeline` - Script Path: `backend/hotel-service/Jenkinsfile`
2. `booking-service-pipeline` - Script Path: `backend/booking-service/Jenkinsfile`
3. `user-service-pipeline` - Script Path: `backend/user-service/Jenkinsfile`
4. `review-service-pipeline` - Script Path: `backend/review-service/Jenkinsfile`
5. `payment-service-pipeline` - Script Path: `backend/payment-service/Jenkinsfile`
6. `admin-dashboard-pipeline` - Script Path: `backend/admin-dashboard/Jenkinsfile`

## Deployment Steps

### 1. Build All Services
```bash
# Trigger master pipeline with parameters:
# - DEPLOY_ENV: dev/staging/prod
# - ACTION: build-all
# - DEPLOY_INGRESS: false
```

### 2. Deploy to Kubernetes
```bash
# Trigger master pipeline with parameters:
# - DEPLOY_ENV: dev/staging/prod
# - ACTION: build-deploy-all
# - DEPLOY_INGRESS: true (for first time)
```

### 3. Individual Service Deployment
```bash
# For individual service updates:
# Trigger specific service pipeline with:
# - DEPLOY_ENV: dev/staging/prod
# - ACTION: build-deploy
```

## Verification Commands

```bash
# Check cluster status
kubectl get nodes
kubectl get namespaces

# Check hotel-booking namespace
kubectl get all -n hotel-booking

# Check ingress
kubectl get ingress -n hotel-booking

# Port forward for testing
kubectl port-forward service/admin-dashboard 8999:8999 -n hotel-booking
kubectl port-forward service/mysql-db 3306:3306 -n hotel-booking

# View logs
kubectl logs -f deployment/hotel-service -n hotel-booking
kubectl logs -f deployment/admin-dashboard -n hotel-booking
```