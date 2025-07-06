pipeline {
    agent any
    
    environment {
        DOCKER_HUB_CREDS = credentials('dockerhub-creds')
        AWS_CREDS = credentials('aws-creds')
        CLUSTER_NAME = 'kastro-eks'
        REGION = 'us-east-1'
    }
    
    parameters {
        choice(
            name: 'DEPLOY_ENV',
            choices: ['dev', 'staging', 'prod'],
            description: 'Environment to deploy'
        )
        choice(
            name: 'ACTION',
            choices: ['build-all', 'deploy-all', 'build-deploy-all'],
            description: 'Action to perform'
        )
        booleanParam(
            name: 'DEPLOY_INGRESS',
            defaultValue: false,
            description: 'Deploy ingress controller'
        )
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build All Services') {
            when {
                anyOf {
                    expression { params.ACTION == 'build-all' }
                    expression { params.ACTION == 'build-deploy-all' }
                }
            }
            parallel {
                stage('Build Hotel Service') {
                    steps {
                        build job: 'hotel-service-pipeline', 
                              parameters: [
                                  choice(name: 'DEPLOY_ENV', value: params.DEPLOY_ENV),
                                  choice(name: 'ACTION', value: 'build')
                              ]
                    }
                }
                stage('Build Booking Service') {
                    steps {
                        build job: 'booking-service-pipeline', 
                              parameters: [
                                  choice(name: 'DEPLOY_ENV', value: params.DEPLOY_ENV),
                                  choice(name: 'ACTION', value: 'build')
                              ]
                    }
                }
                stage('Build User Service') {
                    steps {
                        build job: 'user-service-pipeline', 
                              parameters: [
                                  choice(name: 'DEPLOY_ENV', value: params.DEPLOY_ENV),
                                  choice(name: 'ACTION', value: 'build')
                              ]
                    }
                }
                stage('Build Review Service') {
                    steps {
                        build job: 'review-service-pipeline', 
                              parameters: [
                                  choice(name: 'DEPLOY_ENV', value: params.DEPLOY_ENV),
                                  choice(name: 'ACTION', value: 'build')
                              ]
                    }
                }
                stage('Build Payment Service') {
                    steps {
                        build job: 'payment-service-pipeline', 
                              parameters: [
                                  choice(name: 'DEPLOY_ENV', value: params.DEPLOY_ENV),
                                  choice(name: 'ACTION', value: 'build')
                              ]
                    }
                }
                stage('Build Admin Dashboard') {
                    steps {
                        build job: 'admin-dashboard-pipeline', 
                              parameters: [
                                  choice(name: 'DEPLOY_ENV', value: params.DEPLOY_ENV),
                                  choice(name: 'ACTION', value: 'build')
                              ]
                    }
                }
            }
        }
        
        stage('Deploy Infrastructure') {
            when {
                anyOf {
                    expression { params.ACTION == 'deploy-all' }
                    expression { params.ACTION == 'build-deploy-all' }
                }
            }
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'aws-creds', variable: 'AWS_ACCESS_KEY_ID'),
                        string(credentialsId: 'aws-creds', variable: 'AWS_SECRET_ACCESS_KEY')
                    ]) {
                        sh """
                            # Update kubeconfig
                            aws eks update-kubeconfig --region ${REGION} --name ${CLUSTER_NAME}
                            
                            # Create namespace
                            kubectl apply -f k8s/namespace.yaml
                            
                            # Deploy database
                            kubectl apply -f k8s/mysql-deployment.yaml
                            
                            # Wait for database to be ready
                            kubectl wait --for=condition=ready pod -l app=mysql-db -n hotel-booking --timeout=300s
                        """
                    }
                }
            }
        }
        
        stage('Deploy Ingress Controller') {
            when {
                expression { params.DEPLOY_INGRESS == true }
            }
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'aws-creds', variable: 'AWS_ACCESS_KEY_ID'),
                        string(credentialsId: 'aws-creds', variable: 'AWS_SECRET_ACCESS_KEY')
                    ]) {
                        sh """
                            # Deploy ingress controller
                            kubectl apply -f k8s/ingress-controller.yaml
                            
                            # Wait for ingress controller to be ready
                            kubectl wait --namespace ingress-nginx \
                                --for=condition=ready pod \
                                --selector=app.kubernetes.io/name=ingress-nginx \
                                --timeout=300s
                        """
                    }
                }
            }
        }
        
        stage('Deploy Services') {
            when {
                anyOf {
                    expression { params.ACTION == 'deploy-all' }
                    expression { params.ACTION == 'build-deploy-all' }
                }
            }
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'aws-creds', variable: 'AWS_ACCESS_KEY_ID'),
                        string(credentialsId: 'aws-creds', variable: 'AWS_SECRET_ACCESS_KEY')
                    ]) {
                        sh """
                            # Deploy all services
                            kubectl apply -f k8s/hotel-service.yaml
                            kubectl apply -f k8s/booking-service.yaml
                            kubectl apply -f k8s/user-service.yaml
                            kubectl apply -f k8s/review-service.yaml
                            kubectl apply -f k8s/payment-service.yaml
                            kubectl apply -f k8s/admin-dashboard.yaml
                            
                            # Deploy ingress
                            kubectl apply -f k8s/ingress.yaml
                            
                            # Wait for all deployments to be ready
                            kubectl wait --for=condition=available deployment --all -n hotel-booking --timeout=600s
                        """
                    }
                }
            }
        }
        
        stage('Verify Deployment') {
            when {
                anyOf {
                    expression { params.ACTION == 'deploy-all' }
                    expression { params.ACTION == 'build-deploy-all' }
                }
            }
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'aws-creds', variable: 'AWS_ACCESS_KEY_ID'),
                        string(credentialsId: 'aws-creds', variable: 'AWS_SECRET_ACCESS_KEY')
                    ]) {
                        sh """
                            # Check deployment status
                            kubectl get deployments -n hotel-booking
                            kubectl get services -n hotel-booking
                            kubectl get pods -n hotel-booking
                            
                            # Check ingress
                            kubectl get ingress -n hotel-booking
                            
                            # Test service endpoints
                            echo "Testing service health endpoints..."
                            kubectl exec -n hotel-booking deployment/hotel-service -- curl -f http://localhost:81/health || echo "Hotel service health check failed"
                            kubectl exec -n hotel-booking deployment/booking-service -- curl -f http://localhost:82/health || echo "Booking service health check failed"
                            kubectl exec -n hotel-booking deployment/user-service -- curl -f http://localhost:83/health || echo "User service health check failed"
                            kubectl exec -n hotel-booking deployment/review-service -- curl -f http://localhost:84/health || echo "Review service health check failed"
                            kubectl exec -n hotel-booking deployment/payment-service -- curl -f http://localhost:85/health || echo "Payment service health check failed"
                            kubectl exec -n hotel-booking deployment/admin-dashboard -- curl -f http://localhost:8999/health || echo "Admin dashboard health check failed"
                        """
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo 'Hotel Booking System deployment completed successfully!'
            script {
                if (params.ACTION.contains('deploy')) {
                    echo 'Access URLs:'
                    echo '- Admin Dashboard: http://hotel-booking.local/admin'
                    echo '- API Gateway: http://hotel-booking.local/api'
                    echo '- Database: kubectl port-forward service/mysql-db 3306:3306 -n hotel-booking'
                }
            }
        }
        failure {
            echo 'Hotel Booking System deployment failed!'
        }
    }
}
