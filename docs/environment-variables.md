# ADLY Platform - Environment Variables

## Core Application Settings
```bash
# Application
DEBUG=false
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,api.adly.com
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://app.adly.com

# Environment
ENVIRONMENT=production  # development, staging, production
```

## Database Configuration
```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/adly_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=adly_db
DB_USER=adly_user
DB_PASSWORD=secure_password
DB_SSL_MODE=require  # For production
```

## Redis Configuration
```bash
# Redis (for Celery and caching)
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=redis_password
```

## Celery Configuration
```bash
# Celery Worker Settings
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_TASK_SERIALIZER=json
CELERY_ACCEPT_CONTENT=json
CELERY_RESULT_SERIALIZER=json
CELERY_TIMEZONE=Asia/Riyadh
```

## Email Configuration
```bash
# SMTP Settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=noreply@adly.com
EMAIL_HOST_PASSWORD=email_app_password
DEFAULT_FROM_EMAIL=ADLY Platform <noreply@adly.com>
```

## File Storage
```bash
# AWS S3 for file storage
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_STORAGE_BUCKET_NAME=adly-media-assets
AWS_S3_REGION_NAME=me-south-1  # Middle East (Bahrain)
AWS_S3_CUSTOM_DOMAIN=cdn.adly.com
AWS_DEFAULT_ACL=public-read
```

## Content Generation Providers
```bash
# OpenAI
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000

# Anthropic Claude
ANTHROPIC_API_KEY=your-anthropic-key
ANTHROPIC_MODEL=claude-3-sonnet

# Image Generation
MIDJOURNEY_API_KEY=your-midjourney-key
DALL_E_API_KEY=your-dalle-key
STABILITY_AI_KEY=your-stability-key

# Video Generation
RUNWAY_API_KEY=your-runway-key
PIKA_API_KEY=your-pika-key

# Voice Generation
ELEVEN_LABS_API_KEY=your-elevenlabs-key
MURF_API_KEY=your-murf-key
```

## Ad Platform Integrations
```bash
# Meta (Facebook/Instagram)
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret
META_WEBHOOK_VERIFY_TOKEN=your_webhook_token
META_API_VERSION=v18.0

# TikTok
TIKTOK_APP_ID=your_tiktok_app_id
TIKTOK_APP_SECRET=your_tiktok_app_secret
TIKTOK_WEBHOOK_SECRET=your_tiktok_webhook_secret

# Snapchat
SNAPCHAT_CLIENT_ID=your_snapchat_client_id
SNAPCHAT_CLIENT_SECRET=your_snapchat_client_secret
SNAPCHAT_WEBHOOK_SECRET=your_snapchat_webhook_secret
```

## E-Commerce Platform Integrations
```bash
# Shopify
SHOPIFY_API_KEY=your_shopify_api_key
SHOPIFY_API_SECRET=your_shopify_api_secret
SHOPIFY_WEBHOOK_SECRET=your_shopify_webhook_secret

# WooCommerce
WOOCOMMERCE_CONSUMER_KEY=your_woocommerce_key
WOOCOMMERCE_CONSUMER_SECRET=your_woocommerce_secret

# Salla (KSA)
SALLA_CLIENT_ID=your_salla_client_id
SALLA_CLIENT_SECRET=your_salla_client_secret
SALLA_WEBHOOK_SECRET=your_salla_webhook_secret

# Zid (KSA)
ZID_CLIENT_ID=your_zid_client_id
ZID_CLIENT_SECRET=your_zid_client_secret
ZID_WEBHOOK_SECRET=your_zid_webhook_secret
```

## Payment Processing
```bash
# Stripe
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_stripe_webhook_secret
STRIPE_PRICE_MONTHLY=price_monthly_plan_id
STRIPE_PRICE_YEARLY=price_yearly_plan_id
```

## Security & Authentication
```bash
# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME=3600  # 1 hour in seconds
JWT_REFRESH_TOKEN_LIFETIME=604800  # 7 days in seconds

# 2FA Settings
TOTP_ISSUER_NAME=ADLY Platform
TOTP_VALIDITY_PERIOD=30  # seconds

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REDIS_URL=redis://localhost:6379/1
```

## Monitoring & Logging
```bash
# Sentry (Error Tracking)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json  # json, text

# Health Checks
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_DATABASE=true
HEALTH_CHECK_REDIS=true
HEALTH_CHECK_EXTERNAL_APIS=true
```

## Analytics & Tracking
```bash
# Google Analytics
GA_TRACKING_ID=GA-XXXXXXXXX

# Attribution Tracking
ATTRIBUTION_WINDOW_DAYS=7  # Attribution window for conversions
UTM_TRACKING_ENABLED=true
```

## Localization
```bash
# Language Settings
DEFAULT_LANGUAGE=ar  # Arabic first
SUPPORTED_LANGUAGES=ar,en
TIMEZONE=Asia/Riyadh
CURRENCY=SAR
```

## Development Only
```bash
# Development Settings (DO NOT USE IN PRODUCTION)
DEV_SKIP_EMAIL_VERIFICATION=false
DEV_MOCK_EXTERNAL_APIS=false
DEV_SEED_DATABASE=false
```

## Production Security
```bash
# SSL/TLS
SECURE_SSL_REDIRECT=true
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=true
SECURE_HSTS_PRELOAD=true
SECURE_CONTENT_TYPE_NOSNIFF=true
SECURE_BROWSER_XSS_FILTER=true
X_FRAME_OPTIONS=DENY

# Session Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Strict
CSRF_COOKIE_SECURE=true
CSRF_COOKIE_HTTPONLY=true
```

## Backup & Recovery
```bash
# Database Backups
BACKUP_ENABLED=true
BACKUP_S3_BUCKET=adly-backups
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
```

## Performance
```bash
# Caching
CACHE_ENABLED=true
CACHE_TIMEOUT=3600  # 1 hour
CACHE_KEY_PREFIX=adly

# API Rate Limits
API_RATE_LIMIT_PER_MINUTE=100
CONTENT_GENERATION_RATE_LIMIT=10
AUTH_RATE_LIMIT=5
```

---

## Environment-Specific Files

### Development (.env.development)
```bash
DEBUG=true
DATABASE_URL=postgresql://localhost:5432/adly_dev
REDIS_URL=redis://localhost:6379/0
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEV_MOCK_EXTERNAL_APIS=true
```

### Staging (.env.staging)
```bash
DEBUG=false
DATABASE_URL=postgresql://staging-db:5432/adly_staging
SENTRY_ENVIRONMENT=staging
```

### Production (.env.production)
```bash
DEBUG=false
SECURE_SSL_REDIRECT=true
SENTRY_ENVIRONMENT=production
```

---

## Security Notes

1. **Never commit .env files to version control**
2. **Use different keys for each environment**
3. **Rotate secrets regularly**
4. **Use AWS Secrets Manager or similar for production**
5. **Validate all environment variables on startup**
6. **Use strong, unique passwords for all services**