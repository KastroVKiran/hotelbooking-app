# Jenkins CI/CD with Kubernetes Deployment Guide

## Prerequisites

### 1. AWS EKS Cluster Setup
```bash
# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
# Enter your AWS Access Key ID, Secret Access Key, region (us-east-1), and output format (json)

# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verify installations
aws --version
eksctl version
kubectl version --client
```

### 2. Create EKS Cluster
```bash
# Create EKS cluster (this takes 15-20 minutes)
eksctl create cluster \
  --name hotel-booking-cluster \
  --version 1.27 \
  --region us-east-1 \
  --nodegroup-name hotel-booking-nodes \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 5 \
  --managed \
  --with-oidc \
  --ssh-access \
  --ssh-public-key your-key-name

# Update kubeconfig
aws eks update-kubeconfig --region us-east-1 --name hotel-booking-cluster

# Verify cluster
kubectl get nodes
kubectl get namespaces
```

### 3. Jenkins Server Setup

#### Install Jenkins on EC2
```bash
# Install Java
sudo yum update -y
sudo yum install -y java-11-openjdk

# Install Jenkins
sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io.key
sudo yum install -y jenkins

# Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Get initial admin password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

#### Configure Jenkins
1. Access Jenkins at `http://YOUR_EC2_PUBLIC_IP:8080`
2. Install suggested plugins
3. Create admin user
4. Install additional plugins:
   - Docker Pipeline
   - Kubernetes CLI
   - AWS Steps
   - Pipeline: Stage View
   - Blue Ocean

#### Configure Jenkins Credentials
1. Go to "Manage Jenkins" → "Manage Credentials"
2. Add the following credentials:

**DockerHub Credentials (dockerhub-creds)**
- Kind: Username with password
- Username: your-dockerhub-username
- Password: your-dockerhub-password
- ID: dockerhub-creds

**AWS Credentials (aws-creds)**
- Kind: AWS Credentials
- Access Key ID: your-aws-access-key
- Secret Access Key: your-aws-secret-key
- ID: aws-creds

### 4. Install kubectl and AWS CLI on Jenkins Server
```bash
# SSH to Jenkins server
sudo su - jenkins

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure kubeconfig for jenkins user
aws eks update-kubeconfig --region us-east-1 --name hotel-booking-cluster

# Test connection
kubectl get nodes
```

## Jenkins Pipeline Setup

### 1. Create Jenkins Jobs

#### Master Pipeline Job
1. New Item → Pipeline
2. Name: `hotel-booking-master-pipeline`
3. Pipeline script from SCM
4. Repository URL: your-git-repo-url
5. Script Path: `jenkins/master-pipeline.groovy`

#### Individual Service Jobs
Create these pipeline jobs:
1. `hotel-service-pipeline` - Script Path: `backend/hotel-service/Jenkinsfile`
2. `booking-service-pipeline` - Script Path: `backend/booking-service/Jenkinsfile`
3. `user-service-pipeline` - Script Path: `backend/user-service/Jenkinsfile`
4. `review-service-pipeline` - Script Path: `backend/review-service/Jenkinsfile`
5. `payment-service-pipeline` - Script Path: `backend/payment-service/Jenkinsfile`
6. `admin-dashboard-pipeline` - Script Path: `backend/admin-dashboard/Jenkinsfile`

### 2. Build Docker Images
```bash
# Trigger master pipeline with parameters:
# - DEPLOY_ENV: dev
# - ACTION: build-all
# - DEPLOY_INGRESS: false
```

### 3. Deploy to Kubernetes
```bash
# Trigger master pipeline with parameters:
# - DEPLOY_ENV: dev
# - ACTION: build-deploy-all
# - DEPLOY_INGRESS: true
```

## Manual Kubernetes Deployment

### 1. Create Namespace
```bash
kubectl apply -f k8s/namespace.yaml
```

### 2. Deploy Database
```bash
kubectl apply -f k8s/mysql-deployment.yaml

# Wait for MySQL to be ready
kubectl wait --for=condition=ready pod -l app=mysql-db -n hotel-booking --timeout=300s
```

### 3. Deploy Services
```bash
kubectl apply -f k8s/hotel-service.yaml
kubectl apply -f k8s/booking-service.yaml
kubectl apply -f k8s/user-service.yaml
kubectl apply -f k8s/review-service.yaml
kubectl apply -f k8s/payment-service.yaml
kubectl apply -f k8s/admin-dashboard.yaml

# Wait for all deployments
kubectl wait --for=condition=available deployment --all -n hotel-booking --timeout=600s
```

### 4. Check Deployment Status
```bash
# Check all resources
kubectl get all -n hotel-booking

# Check pod logs
kubectl logs -f deployment/hotel-service -n hotel-booking
kubectl logs -f deployment/admin-dashboard -n hotel-booking

# Check service endpoints
kubectl get endpoints -n hotel-booking
```

## Access Application

### Method 1: Port Forwarding (for testing)
```bash
# Forward admin dashboard
kubectl port-forward service/admin-dashboard 8999:8999 -n hotel-booking

# Access at http://localhost:8999
```

### Method 2: LoadBalancer Service
```bash
# Get external IP
kubectl get service admin-dashboard -n hotel-booking

# Access using external IP
```

### Method 3: NodePort (if LoadBalancer not available)
```bash
# Edit service to use NodePort
kubectl patch service admin-dashboard -n hotel-booking -p '{"spec":{"type":"NodePort"}}'

# Get node port
kubectl get service admin-dashboard -n hotel-booking

# Access using any node IP and the assigned port
```

## Database Access in Kubernetes

### Method 1: Port Forward
```bash
# Forward MySQL port
kubectl port-forward service/mysql-db 3306:3306 -n hotel-booking

# Connect from local machine
mysql -h localhost -P 3306 -u hotel_user -p
```

### Method 2: Exec into Pod
```bash
# Get MySQL pod name
kubectl get pods -n hotel-booking | grep mysql

# Exec into pod
kubectl exec -it <mysql-pod-name> -n hotel-booking -- mysql -u hotel_user -p
```

### Method 3: Create MySQL Client Pod
```bash
# Create temporary MySQL client pod
kubectl run mysql-client --image=mysql:8.0 -it --rm --restart=Never -n hotel-booking -- mysql -h mysql-db -u hotel_user -p
```

## Monitoring and Troubleshooting

### Check Pod Status
```bash
# Get all pods
kubectl get pods -n hotel-booking

# Describe problematic pod
kubectl describe pod <pod-name> -n hotel-booking

# Check pod logs
kubectl logs <pod-name> -n hotel-booking

# Follow logs
kubectl logs -f <pod-name> -n hotel-booking
```

### Check Services
```bash
# Get services
kubectl get services -n hotel-booking

# Test service connectivity
kubectl exec -it deployment/hotel-service -n hotel-booking -- curl http://mysql-db:3306
```

### Check Deployments
```bash
# Get deployment status
kubectl get deployments -n hotel-booking

# Check deployment details
kubectl describe deployment hotel-service -n hotel-booking

# Scale deployment
kubectl scale deployment hotel-service --replicas=3 -n hotel-booking
```

### Resource Usage
```bash
# Check node resources
kubectl top nodes

# Check pod resources
kubectl top pods -n hotel-booking

# Check resource quotas
kubectl describe resourcequota -n hotel-booking
```

## Scaling and Updates

### Scale Services
```bash
# Scale specific service
kubectl scale deployment hotel-service --replicas=3 -n hotel-booking

# Auto-scale based on CPU
kubectl autoscale deployment hotel-service --cpu-percent=70 --min=2 --max=10 -n hotel-booking
```

### Rolling Updates
```bash
# Update image
kubectl set image deployment/hotel-service hotel-service=hotel-booking/hotel-service:v2 -n hotel-booking

# Check rollout status
kubectl rollout status deployment/hotel-service -n hotel-booking

# Rollback if needed
kubectl rollout undo deployment/hotel-service -n hotel-booking
```

## Cleanup

### Delete Application
```bash
# Delete all resources
kubectl delete namespace hotel-booking

# Or delete individual resources
kubectl delete -f k8s/
```

### Delete EKS Cluster
```bash
# Delete cluster (this will take 10-15 minutes)
eksctl delete cluster --name hotel-booking-cluster --region us-east-1
```

## Security Best Practices

1. **Use Secrets for Sensitive Data**
```bash
# Create secret for database credentials
kubectl create secret generic mysql-secret \
  --from-literal=username=hotel_user \
  --from-literal=password=hotel_pass \
  -n hotel-booking
```

2. **Network Policies**
```yaml
# Create network policy to restrict traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: hotel-booking-network-policy
  namespace: hotel-booking
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

3. **Resource Limits**
```yaml
# Add to deployment specs
resources:
  limits:
    memory: "512Mi"
    cpu: "500m"
  requests:
    memory: "256Mi"
    cpu: "250m"
```

## Performance Optimization

1. **Use Horizontal Pod Autoscaler**
2. **Configure resource requests and limits**
3. **Use persistent volumes for database**
4. **Implement health checks**
5. **Use readiness and liveness probes**

This completes the Jenkins CI/CD with Kubernetes deployment guide. The system will be accessible via the LoadBalancer external IP or through port forwarding for testing.