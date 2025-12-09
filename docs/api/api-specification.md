# ADLY Platform - API Specification

## Base URL
- Development: `http://localhost:8000/api/v1`
- Production: `https://api.adly.com/v1`

## Authentication
All authenticated endpoints require Bearer token in header:
```
Authorization: Bearer <jwt_token>
```

## Response Format
```json
{
  "success": true,
  "data": {},
  "message": "Success message",
  "errors": []
}
```

---

## 🔐 Authentication Endpoints

### POST /auth/register
Register new user
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe"
}
```

### POST /auth/login
Login user
```json
{
  "email": "user@example.com",
  "password": "password123",
  "otp_token": "123456" // Optional if 2FA enabled
}
```

### POST /auth/verify-email
Verify email with OTP
```json
{
  "email": "user@example.com",
  "token": "123456"
}
```

### POST /auth/forgot-password
Request password reset
```json
{
  "email": "user@example.com"
}
```

### POST /auth/reset-password
Reset password with token
```json
{
  "token": "123456",
  "new_password": "newpassword123"
}
```

### POST /auth/enable-2fa
Enable 2FA
```json
{
  "secret": "base32_secret",
  "token": "123456"
}
```

---

## 🏢 Workspace Endpoints

### GET /workspaces
List user workspaces
Response:
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "My Workspace",
      "slug": "my-workspace",
      "role": "owner",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /workspaces
Create workspace
```json
{
  "name": "New Workspace",
  "slug": "new-workspace"
}
```

### GET /workspaces/{id}
Get workspace details

### PUT /workspaces/{id}
Update workspace

### DELETE /workspaces/{id}
Delete workspace

### GET /workspaces/{id}/members
List workspace members

### POST /workspaces/{id}/members
Invite member
```json
{
  "email": "member@example.com",
  "role": "member"
}
```

### PUT /workspaces/{id}/members/{user_id}
Update member role
```json
{
  "role": "viewer"
}
```

### DELETE /workspaces/{id}/members/{user_id}
Remove member

---

## 🛒 Store Integration Endpoints

### GET /workspaces/{id}/stores
List connected stores

### POST /workspaces/{id}/stores
Connect new store
```json
{
  "platform": "shopify",
  "store_name": "My Store",
  "store_url": "https://mystore.myshopify.com",
  "access_token": "access_token_here"
}
```

### PUT /workspaces/{id}/stores/{store_id}
Update store connection

### DELETE /workspaces/{id}/stores/{store_id}
Disconnect store

### POST /workspaces/{id}/stores/{store_id}/sync
Trigger manual sync

### GET /workspaces/{id}/stores/{store_id}/products
List products
Query params: `page`, `limit`, `search`, `category`

### GET /workspaces/{id}/stores/{store_id}/orders
List orders
Query params: `page`, `limit`, `start_date`, `end_date`, `status`

---

## 🎨 Content Creation Endpoints

### GET /workspaces/{id}/assets
List content assets
Query params: `type`, `page`, `limit`

### POST /workspaces/{id}/assets/upload
Upload asset (multipart/form-data)

### DELETE /workspaces/{id}/assets/{asset_id}
Delete asset

### POST /workspaces/{id}/generate/text
Generate text content
```json
{
  "type": "headline", // "headline", "cta", "description"
  "prompt": "Generate Arabic headline for Ramadan sale",
  "language": "ar",
  "product_context": {
    "name": "Traditional Dress",
    "category": "Fashion"
  }
}
```

### POST /workspaces/{id}/generate/image
Generate image
```json
{
  "prompt": "Modern Arabic calligraphy for Eid celebration",
  "style": "modern",
  "dimensions": "1080x1080",
  "language": "ar"
}
```

### POST /workspaces/{id}/generate/video
Generate video
```json
{
  "template_id": "uuid",
  "scenes": [
    {
      "type": "product_showcase",
      "product_id": "uuid",
      "text_overlay": "خصم 50% على الأزياء التراثية"
    }
  ],
  "duration": 15,
  "language": "ar"
}
```

### POST /workspaces/{id}/generate/voice
Generate voiceover
```json
{
  "text": "اكتشف مجموعتنا الجديدة من الأزياء التراثية",
  "language": "ar",
  "voice": "female",
  "speed": 1.0
}
```

### GET /workspaces/{id}/generation-jobs
List generation jobs

### GET /workspaces/{id}/generation-jobs/{job_id}
Get generation job status

---

## 🤖 Campaign Parser Endpoints

### POST /workspaces/{id}/campaigns/parse
Parse campaign instruction
```json
{
  "instruction": "Create Instagram and TikTok campaign for Ramadan sale with 1000 SAR budget targeting women 25-40 in Riyadh"
}
```

Response:
```json
{
  "data": {
    "platforms": ["instagram", "tiktok"],
    "objective": "conversions",
    "budget": {
      "amount": 1000,
      "currency": "SAR",
      "type": "total"
    },
    "duration": {
      "start_date": "2024-03-01",
      "end_date": "2024-03-31"
    },
    "audience": {
      "age_min": 25,
      "age_max": 40,
      "gender": "female",
      "locations": ["Riyadh"]
    },
    "theme": "ramadan",
    "language": "ar"
  }
}
```

---

## 📢 Ad Platform Endpoints

### GET /workspaces/{id}/ad-accounts
List connected ad accounts

### POST /workspaces/{id}/ad-accounts
Connect ad account
```json
{
  "platform": "meta",
  "access_token": "access_token_here"
}
```

### DELETE /workspaces/{id}/ad-accounts/{account_id}
Disconnect ad account

### GET /workspaces/{id}/campaigns
List campaigns
Query params: `platform`, `status`, `page`, `limit`

### POST /workspaces/{id}/campaigns
Create campaign
```json
{
  "ad_account_id": "uuid",
  "name": "Ramadan Sale Campaign",
  "objective": "CONVERSIONS",
  "budget_type": "daily",
  "budget_amount": 100,
  "start_date": "2024-03-01",
  "end_date": "2024-03-31",
  "target_audience": {
    "age_min": 25,
    "age_max": 40,
    "gender": "female",
    "locations": ["SA"]
  }
}
```

### GET /workspaces/{id}/campaigns/{campaign_id}
Get campaign details

### PUT /workspaces/{id}/campaigns/{campaign_id}
Update campaign

### DELETE /workspaces/{id}/campaigns/{campaign_id}
Delete campaign

### POST /workspaces/{id}/campaigns/{campaign_id}/publish
Publish campaign to platform

### POST /workspaces/{id}/campaigns/{campaign_id}/pause
Pause campaign

### POST /workspaces/{id}/campaigns/{campaign_id}/resume
Resume campaign

### GET /workspaces/{id}/campaigns/{campaign_id}/ad-sets
List ad sets

### POST /workspaces/{id}/campaigns/{campaign_id}/ad-sets
Create ad set
```json
{
  "name": "Ad Set 1",
  "budget_amount": 50,
  "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
  "targeting": {
    "interests": ["fashion", "traditional_clothing"],
    "behaviors": ["online_shoppers"]
  }
}
```

### GET /workspaces/{id}/ad-sets/{ad_set_id}/ads
List ads

### POST /workspaces/{id}/ad-sets/{ad_set_id}/ads
Create ad
```json
{
  "name": "Ramadan Sale Ad",
  "creative_data": {
    "headline": "خصم 50% على الأزياء التراثية",
    "description": "اكتشف مجموعتنا الجديدة",
    "cta": "تسوق الآن"
  },
  "media_assets": [
    {
      "asset_id": "uuid",
      "type": "image"
    }
  ]
}
```

---

## 📊 Analytics Endpoints

### GET /workspaces/{id}/analytics/overview
Get analytics overview
Query params: `start_date`, `end_date`, `platform`

Response:
```json
{
  "data": {
    "total_spend": 5000.00,
    "total_revenue": 15000.00,
    "roas": 3.0,
    "total_impressions": 100000,
    "total_clicks": 2500,
    "ctr": 2.5,
    "conversions": 150
  }
}
```

### GET /workspaces/{id}/analytics/campaigns
Get campaign performance
Query params: `start_date`, `end_date`, `campaign_ids[]`

### GET /workspaces/{id}/analytics/platforms
Get platform breakdown

### GET /workspaces/{id}/analytics/attribution
Get attribution data

### POST /workspaces/{id}/analytics/export
Export analytics data
```json
{
  "format": "csv", // "csv", "pdf"
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "metrics": ["impressions", "clicks", "spend", "conversions"]
}
```

---

## 💳 Billing Endpoints

### GET /workspaces/{id}/subscription
Get current subscription

### POST /workspaces/{id}/subscription
Create subscription
```json
{
  "plan_id": "uuid",
  "payment_method_id": "pm_stripe_id"
}
```

### PUT /workspaces/{id}/subscription
Update subscription
```json
{
  "plan_id": "uuid"
}
```

### DELETE /workspaces/{id}/subscription
Cancel subscription

### GET /workspaces/{id}/invoices
List invoices

### GET /workspaces/{id}/invoices/{invoice_id}
Get invoice details

### GET /subscription-plans
List available plans

---

## 🛠️ Admin Endpoints

### GET /admin/users
List all users (admin only)

### GET /admin/workspaces
List all workspaces (admin only)

### GET /admin/system-health
Get system health status

### GET /admin/api-logs
Get API usage logs

### GET /admin/generation-logs
Get content generation logs

---

## Error Codes

- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

## Rate Limiting
- Authentication endpoints: 5 requests/minute
- Content generation: 10 requests/minute
- Other endpoints: 100 requests/minute