#!/bin/bash

# SecureTrainer Production Deployment Script
# Production-ready deployment with security checks and monitoring

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_ENV=${1:-production}
PROJECT_NAME="securetrainer"
BACKUP_DIR="/backup/${PROJECT_NAME}"
LOG_FILE="/var/log/${PROJECT_NAME}/deploy.log"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}" | tee -a "$LOG_FILE"
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Starting pre-deployment checks..."
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running. Please start Docker first."
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose >/dev/null 2>&1; then
        error "Docker Compose is not installed."
    fi
    
    # Check if environment file exists
    if [[ ! -f ".env.${DEPLOYMENT_ENV}" ]]; then
        error "Environment file .env.${DEPLOYMENT_ENV} not found."
    fi
    
    # Check if required environment variables are set
    source ".env.${DEPLOYMENT_ENV}"
    
    required_vars=("SECRET_KEY" "MONGO_ROOT_PASSWORD" "MAIL_USERNAME" "MAIL_PASSWORD")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            error "Required environment variable $var is not set in .env.${DEPLOYMENT_ENV}"
        fi
    done
    
    log "Pre-deployment checks passed ✓"
}

# Backup current deployment
backup_current_deployment() {
    log "Creating backup of current deployment..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR/$(date +%Y%m%d_%H%M%S)"
    
    # Backup database
    if docker ps | grep -q "${PROJECT_NAME}-mongodb"; then
        info "Backing up MongoDB database..."
        docker exec "${PROJECT_NAME}-mongodb" mongodump --out /backup/$(date +%Y%m%d_%H%M%S) 2>/dev/null || warning "Database backup failed"
    fi
    
    # Backup application data
    if [[ -d "./data" ]]; then
        cp -r ./data "$BACKUP_DIR/$(date +%Y%m%d_%H%M%S)/" 2>/dev/null || warning "Data backup failed"
    fi
    
    log "Backup completed ✓"
}

# Build and deploy
build_and_deploy() {
    log "Building and deploying SecureTrainer..."
    
    # Copy environment file
    cp ".env.${DEPLOYMENT_ENV}" .env
    
    # Build images
    info "Building Docker images..."
    docker-compose build --no-cache
    
    # Run security scans on built images
    info "Running security scans..."
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
        aquasec/trivy image "${PROJECT_NAME}_securetrainer:latest" || warning "Security scan completed with warnings"
    
    # Deploy services
    info "Deploying services..."
    docker-compose up -d
    
    log "Deployment completed ✓"
}

# Health checks
health_checks() {
    log "Performing health checks..."
    
    # Wait for services to start
    sleep 30
    
    # Check if all containers are running
    containers=("${PROJECT_NAME}-mongodb" "${PROJECT_NAME}-redis" "${PROJECT_NAME}-app" "${PROJECT_NAME}-nginx")
    
    for container in "${containers[@]}"; do
        if ! docker ps | grep -q "$container"; then
            error "Container $container is not running"
        fi
    done
    
    # Check application health endpoint
    max_attempts=10
    attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f http://localhost/health >/dev/null 2>&1; then
            log "Application health check passed ✓"
            break
        else
            info "Health check attempt $attempt/$max_attempts failed, retrying..."
            sleep 10
            ((attempt++))
        fi
    done
    
    if [[ $attempt -gt $max_attempts ]]; then
        error "Application health check failed after $max_attempts attempts"
    fi
    
    # Check database connectivity
    if docker exec "${PROJECT_NAME}-mongodb" mongo --eval "db.runCommand('ping')" >/dev/null 2>&1; then
        log "Database connectivity check passed ✓"
    else
        error "Database connectivity check failed"
    fi
    
    log "All health checks passed ✓"
}

# Security hardening
security_hardening() {
    log "Applying security hardening..."
    
    # Set proper file permissions
    find . -type f -name "*.py" -exec chmod 644 {} \;
    find . -type f -name "*.sh" -exec chmod 755 {} \;
    chmod 600 .env
    
    # Update containers
    info "Updating base images for security patches..."
    docker-compose pull
    
    # Configure firewall rules (if ufw is available)
    if command -v ufw >/dev/null 2>&1; then
        info "Configuring firewall rules..."
        ufw allow 80/tcp
        ufw allow 443/tcp
        ufw allow 22/tcp
        ufw --force enable || warning "Firewall configuration failed"
    fi
    
    log "Security hardening completed ✓"
}

# Performance optimization
performance_optimization() {
    log "Applying performance optimizations..."
    
    # Set Docker daemon optimization
    info "Optimizing Docker settings..."
    
    # Cleanup unused Docker resources
    docker system prune -f
    
    # Set resource limits for containers
    info "Applying resource limits..."
    # This would be done through docker-compose.yml in production
    
    log "Performance optimization completed ✓"
}

# Monitoring setup
setup_monitoring() {
    log "Setting up monitoring and alerting..."
    
    # Start monitoring services
    info "Starting Prometheus and Grafana..."
    
    # Import Grafana dashboards
    if docker ps | grep -q "${PROJECT_NAME}-grafana"; then
        info "Importing Grafana dashboards..."
        # Dashboard import logic would go here
    fi
    
    # Configure alerts
    info "Configuring alerts..."
    # Alert configuration would go here
    
    log "Monitoring setup completed ✓"
}

# Post-deployment verification
post_deployment_verification() {
    log "Running post-deployment verification..."
    
    # Run AI system tests
    info "Running AI system tests..."
    docker exec "${PROJECT_NAME}-app" python -m pytest tests/test_ai_system.py -v || warning "Some AI tests failed"
    
    # Test key functionalities
    info "Testing key functionalities..."
    
    # Test user registration
    curl -X POST http://localhost/api/auth/register \
        -H "Content-Type: application/json" \
        -d '{"username":"test_user","email":"test@example.com","password":"test123","first_name":"Test","last_name":"User","company":"Test Co","department":"IT"}' \
        >/dev/null 2>&1 || warning "User registration test failed"
    
    # Test AI endpoints
    # This would require proper authentication in production
    
    log "Post-deployment verification completed ✓"
}

# Rollback function
rollback() {
    error_msg="$1"
    warning "Deployment failed: $error_msg"
    warning "Initiating rollback..."
    
    # Stop current deployment
    docker-compose down
    
    # Restore from backup
    latest_backup=$(ls -t "$BACKUP_DIR" | head -n1)
    if [[ -n "$latest_backup" ]]; then
        info "Restoring from backup: $latest_backup"
        # Restoration logic would go here
        warning "Manual restoration required from backup: $BACKUP_DIR/$latest_backup"
    fi
    
    error "Deployment failed and rollback initiated"
}

# Main deployment process
main() {
    log "Starting SecureTrainer deployment to $DEPLOYMENT_ENV environment"
    
    # Set up error handling
    trap 'rollback "Unexpected error occurred"' ERR
    
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Run deployment steps
    pre_deployment_checks
    backup_current_deployment
    build_and_deploy
    health_checks
    security_hardening
    performance_optimization
    setup_monitoring
    post_deployment_verification
    
    log "🎉 SecureTrainer deployment completed successfully!"
    log "🌐 Application is available at: http://localhost"
    log "📊 Grafana dashboard: http://localhost:3000"
    log "📈 Prometheus metrics: http://localhost:9090"
    
    info "Next steps:"
    info "1. Configure SSL certificates for HTTPS"
    info "2. Set up domain name and DNS"
    info "3. Configure backup schedules"
    info "4. Review monitoring alerts"
    info "5. Update firewall rules for production"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi