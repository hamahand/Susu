# SusuSave API Documentation

## Base URL

```
Development: http://localhost:8000
Production: https://api.sususave.com
```

## Authentication

All authenticated endpoints require a JWT Bearer token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

### Get Token

```http
POST /auth/login
Content-Type: application/json

{
  "phone_number": "+233244123456",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

## Endpoints

### Authentication

#### Register User

```http
POST /auth/register
```

**Request Body:**
```json
{
  "phone_number": "+233244123456",
  "name": "John Doe",
  "password": "securepassword123",
  "user_type": "app"
}
```

**Response: 201 Created**
```json
{
  "id": 1,
  "phone_number": "+233244123456",
  "name": "John Doe",
  "user_type": "app",
  "created_at": "2024-01-15T10:30:00"
}
```

#### Login

```http
POST /auth/login
```

**Request Body:**
```json
{
  "phone_number": "+233244123456",
  "password": "securepassword123"
}
```

**Response: 200 OK**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### Get Current User

```http
GET /auth/me
Authorization: Bearer <token>
```

**Response: 200 OK**
```json
{
  "id": 1,
  "phone_number": "+233244123456",
  "name": "John Doe",
  "user_type": "app",
  "created_at": "2024-01-15T10:30:00"
}
```

---

### Groups

#### Create Group

```http
POST /groups
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Monthly Rent Fund",
  "contribution_amount": 50.00,
  "num_cycles": 10
}
```

**Response: 201 Created**
```json
{
  "id": 1,
  "group_code": "SUSU1A2B",
  "name": "Monthly Rent Fund",
  "contribution_amount": 50.00,
  "num_cycles": 10,
  "current_round": 1,
  "status": "active",
  "creator_id": 1,
  "created_at": "2024-01-15T11:00:00"
}
```

#### Join Group

```http
POST /groups/join
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "group_code": "SUSU1A2B"
}
```

**Response: 200 OK**
```json
{
  "message": "Successfully joined group",
  "group_id": 1,
  "rotation_position": 2
}
```

#### Get My Groups

```http
GET /groups/my-groups
Authorization: Bearer <token>
```

**Response: 200 OK**
```json
[
  {
    "id": 1,
    "group_code": "SUSU1A2B",
    "name": "Monthly Rent Fund",
    "contribution_amount": 50.00,
    "num_cycles": 10,
    "current_round": 1,
    "status": "active",
    "creator_id": 1,
    "created_at": "2024-01-15T11:00:00"
  }
]
```

#### Get Group Details

```http
GET /groups/{group_id}
Authorization: Bearer <token>
```

**Response: 200 OK**
```json
{
  "id": 1,
  "group_code": "SUSU1A2B",
  "name": "Monthly Rent Fund",
  "contribution_amount": 50.00,
  "num_cycles": 10,
  "current_round": 1,
  "status": "active",
  "creator_id": 1,
  "created_at": "2024-01-15T11:00:00"
}
```

#### Get Group Dashboard

```http
GET /groups/{group_id}/dashboard
Authorization: Bearer <token>
```

**Response: 200 OK**
```json
{
  "group": {
    "id": 1,
    "group_code": "SUSU1A2B",
    "name": "Monthly Rent Fund",
    "contribution_amount": 50.00,
    "num_cycles": 10,
    "current_round": 1,
    "status": "active",
    "creator_id": 1,
    "created_at": "2024-01-15T11:00:00"
  },
  "members": [
    {
      "user_id": 1,
      "name": "John Doe",
      "phone_number": "+233244123456",
      "rotation_position": 1,
      "is_admin": true,
      "paid_current_round": true
    },
    {
      "user_id": 2,
      "name": "Jane Smith",
      "phone_number": "+233244987654",
      "rotation_position": 2,
      "is_admin": false,
      "paid_current_round": false
    }
  ],
  "total_collected_current_round": 50.00,
  "next_recipient": {
    "user_id": 1,
    "name": "John Doe",
    "phone_number": "+233244123456",
    "rotation_position": 1,
    "is_admin": true,
    "paid_current_round": false
  },
  "next_payout_date": "2024-01-20T12:00:00"
}
```

---

### Payments

#### Manual Payment Trigger

```http
POST /payments/manual-trigger
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "group_id": 1
}
```

**Response: 200 OK**
```json
{
  "id": 1,
  "transaction_id": "MOMO1A2B3C4D5E6F",
  "user_id": 1,
  "group_id": 1,
  "round_number": 1,
  "amount": 50.00,
  "payment_date": "2024-01-15T12:00:00",
  "status": "success",
  "retry_count": 0,
  "created_at": "2024-01-15T12:00:00"
}
```

**Error Response: 402 Payment Required**
```json
{
  "detail": "Payment failed: Insufficient funds. Balance: 25.00, Required: 50.00"
}
```

#### Get Payment History

```http
GET /payments/history
Authorization: Bearer <token>
```

**Response: 200 OK**
```json
[
  {
    "id": 1,
    "transaction_id": "MOMO1A2B3C4D5E6F",
    "user_id": 1,
    "group_id": 1,
    "round_number": 1,
    "amount": 50.00,
    "payment_date": "2024-01-15T12:00:00",
    "status": "success",
    "retry_count": 0,
    "created_at": "2024-01-15T12:00:00"
  }
]
```

#### Retry Failed Payment

```http
POST /payments/{payment_id}/retry
Authorization: Bearer <token>
```

**Response: 200 OK**
```json
{
  "id": 1,
  "transaction_id": "MOMO7G8H9I0J1K2L",
  "user_id": 1,
  "group_id": 1,
  "round_number": 1,
  "amount": 50.00,
  "payment_date": "2024-01-15T12:30:00",
  "status": "success",
  "retry_count": 1,
  "created_at": "2024-01-15T12:00:00"
}
```

---

### Payouts

#### Approve Payout

```http
POST /payouts/{payout_id}/approve
Authorization: Bearer <token>
```

**Response: 200 OK**
```json
{
  "id": 1,
  "group_id": 1,
  "round_number": 1,
  "recipient_id": 1,
  "amount": 500.00,
  "payout_date": "2024-01-20T12:00:00",
  "status": "paid",
  "transaction_id": "MOMOM1N2O3P4Q5R6",
  "created_at": "2024-01-20T11:00:00"
}
```

**Error Response: 403 Forbidden**
```json
{
  "detail": "Only group admins can approve payouts"
}
```

#### Get Current Payout

```http
GET /payouts/{group_id}/current
Authorization: Bearer <token>
```

**Response: 200 OK**
```json
{
  "id": 1,
  "group_id": 1,
  "round_number": 1,
  "recipient_id": 1,
  "amount": 500.00,
  "payout_date": null,
  "status": "pending",
  "transaction_id": null,
  "created_at": "2024-01-20T11:00:00"
}
```

---

### USSD

#### USSD Callback (Africa's Talking)

```http
POST /ussd/callback
Content-Type: application/x-www-form-urlencoded
```

**Request Body:**
```
sessionId=ATUid_12345
phoneNumber=%2B233244123456
text=
```

**Response: 200 OK**
```
CON Welcome to SusuSave
1. Join Group
2. Pay Contribution
3. Check Balance/Status
4. My Payout Date
```

**Subsequent Request (User selects option 1):**
```
sessionId=ATUid_12345
phoneNumber=%2B233244123456
text=1
```

**Response:**
```
CON Enter Group Code (e.g., SUSU1234):
```

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication
- **402 Payment Required**: Payment failed
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

### Validation Errors

```json
{
  "detail": [
    {
      "loc": ["body", "contribution_amount"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

---

## Rate Limiting

USSD endpoint is rate-limited to prevent spam:
- **Limit**: 20 requests per minute per phone number
- **Response**: 429 Too Many Requests

---

## Webhooks

### Payment Status Webhook (Future)

When integrating with real MoMo API:

```http
POST /webhooks/momo
```

**Payload:**
```json
{
  "transaction_id": "MOMO123456",
  "status": "success",
  "amount": 50.00,
  "currency": "GHS"
}
```

---

## Testing

### Postman Collection

Import the Postman collection from `/docs/postman_collection.json`

### cURL Examples

**Register:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+233244123456",
    "name": "John Doe",
    "password": "password123",
    "user_type": "app"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+233244123456",
    "password": "password123"
  }'
```

**Create Group:**
```bash
curl -X POST http://localhost:8000/groups \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Monthly Rent Fund",
    "contribution_amount": 50.00,
    "num_cycles": 10
  }'
```

---

For interactive API testing, visit: **http://localhost:8000/docs**

