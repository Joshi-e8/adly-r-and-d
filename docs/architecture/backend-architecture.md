# ADLY Backend Architecture

## System Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                        ADLY Backend System                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Django    │    │   Celery    │    │ PostgreSQL  │         │
│  │   REST API  │◄──►│   Workers   │◄──►│  Database   │         │
│  │             │    │             │    │             │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                   │                   │              │
│         │                   │                   │              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │    Redis    │    │   Content   │    │ External    │         │
│  │   Cache/    │◄──►│ Generation  │◄──►│ Platform    │         │
│  │   Queue     │    │  Services   │    │   APIs      │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Django REST API Layer
- **Authentication**: JWT + OAuth2
- **Authorization**: Role-based access control
- **API Endpoints**: RESTful design
- **Middleware**: CORS, Rate limiting, Logging

### 2. Database Layer (PostgreSQL)
- **User Management**: Users, Workspaces, Permissions
- **E-commerce**: Stores, Products, Orders
- **Campaigns**: Campaigns, Ad Sets, Ads, Creative Assets
- **Analytics**: Performance metrics, Attribution data
- **Audit**: Activity logs, API calls

### 3. Background Workers (Celery)
- **Data Sync**: E-commerce platforms, Ad platforms
- **Content Generation**: Text, Images, Videos
- **Analytics**: Performance data collection
- **Notifications**: Email, Webhooks

### 4. External Integrations
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   E-commerce    │    │  Ad Platforms   │    │    Content      │
│   Platforms     │    │                 │    │  Generation     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Shopify       │    │ • Meta (FB/IG)  │    │ • OpenAI        │
│ • WooCommerce   │    │ • TikTok        │    │ • Anthropic     │
│ • Salla         │    │ • Snapchat      │    │ • Stability AI  │
│ • Zid           │    │ • Google Ads    │    │ • ElevenLabs    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Data Flow Architecture

### Campaign Creation Flow
```
Frontend Request → Django API → Campaign Parser → Content Generation → Platform Publishing
     ↓                ↓              ↓                    ↓                    ↓
  Validation    → Database Save → Celery Task → AI Services → External APIs
```

### Analytics Sync Flow
```
Celery Scheduler → Platform APIs → Data Processing → Database Storage → Real-time Updates
       ↓               ↓               ↓                ↓                    ↓
   Hourly Task → Fetch Metrics → Transform Data → PostgreSQL → WebSocket Push
```

## Security Architecture

### Authentication & Authorization
```python
# Multi-layer security implementation
class SecurityMiddleware:
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.jwt_handler = JWTHandler()
        self.permission_checker = PermissionChecker()
    
    async def authenticate_request(self, request):
        # 1. Rate limiting
        await self.rate_limiter.check_limit(request.client_ip)
        
        # 2. JWT validation
        token = self.extract_token(request)
        user = await self.jwt_handler.validate_token(token)
        
        # 3. 2FA check for sensitive operations
        if self.requires_2fa(request.endpoint):
            await self.verify_2fa(user, request.headers.get('X-2FA-Token'))
        
        # 4. Workspace permission check
        workspace_id = self.extract_workspace_id(request)
        await self.permission_checker.check_access(user, workspace_id, request.method)
        
        return user
```

### Data Protection
- **Encryption at Rest**: AES-256 for sensitive data
- **Encryption in Transit**: TLS 1.3 for all communications
- **API Key Management**: AWS Secrets Manager integration
- **PII Protection**: Automatic PII detection and masking
- **Audit Logging**: Complete request/response logging

### Security Headers
```python
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
    'Referrer-Policy': 'strict-origin-when-cross-origin'
}
```

## Monitoring & Observability

### Application Monitoring
```python
# Comprehensive monitoring setup
MONITORING_STACK = {
    'APM': 'Sentry',           # Error tracking & performance
    'Metrics': 'Prometheus',   # Custom metrics collection
    'Logging': 'ELK Stack',    # Centralized logging
    'Uptime': 'Pingdom',       # Service availability
    'Alerts': 'PagerDuty'      # Incident management
}

# Custom metrics
class MetricsCollector:
    def __init__(self):
        self.campaign_creation_time = Histogram('campaign_creation_duration_seconds')
        self.api_request_count = Counter('api_requests_total', ['method', 'endpoint'])
        self.content_generation_success = Counter('content_generation_success_total', ['type'])
        self.platform_api_errors = Counter('platform_api_errors_total', ['platform', 'error_type'])
```

### Health Checks
```python
# Comprehensive health check endpoint
@api_view(['GET'])
def health_check(request):
    health_status = {
        'database': check_database_connection(),
        'redis': check_redis_connection(),
        'celery': check_celery_workers(),
        'external_apis': check_external_api_health(),
        'disk_space': check_disk_space(),
        'memory_usage': check_memory_usage()
    }
    
    overall_status = 'healthy' if all(health_status.values()) else 'unhealthy'
    
    return Response({
        'status': overall_status,
        'timestamp': timezone.now(),
        'checks': health_status
    })
```

## Deployment Architecture

### Production Infrastructure
```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS/GCP Cloud                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │     ALB     │    │   ECS/GKE   │    │     RDS     │         │
│  │ Load Balancer│◄──►│  Containers │◄──►│ PostgreSQL  │         │
│  │             │    │             │    │             │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                   │                   │              │
│         │                   │                   │              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ CloudFront  │    │ ElastiCache │    │     S3      │         │
│  │     CDN     │    │    Redis    │    │ File Storage│         │
│  │             │    │             │    │             │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Container Configuration
```dockerfile
# Production Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash adly
USER adly

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "adly.wsgi:application"]
```