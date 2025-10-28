# API Testing Examples

Quick reference for testing all API endpoints using curl or Postman.

## Base URL
```
http://localhost:8000
```

## 1. Register Customer

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "monthly_income": 50000,
    "phone_number": 9876543210
  }'
```

**Expected Response:**
```json
{
  "customer_id": 1,
  "name": "John Doe",
  "age": 30,
  "monthly_income": 50000,
  "approved_limit": 1800000,
  "phone_number": 9876543210
}
```

## 2. Check Eligibility

```bash
curl -X POST http://localhost:8000/check-eligibility \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "loan_amount": 100000,
    "interest_rate": 8.0,
    "tenure": 12
  }'
```

**Expected Response:**
```json
{
  "customer_id": 1,
  "approval": true,
  "interest_rate": 8.0,
  "corrected_interest_rate": 8.0,
  "tenure": 12,
  "monthly_installment": 8698.84
}
```

## 3. Create Loan

```bash
curl -X POST http://localhost:8000/create-loan \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "loan_amount": 100000,
    "interest_rate": 10.0,
    "tenure": 12
  }'
```

**Expected Response (Success):**
```json
{
  "loan_id": 1,
  "customer_id": 1,
  "loan_approved": true,
  "message": "Loan approved successfully",
  "monthly_installment": 8791.59
}
```

## 4. View Loan by ID

```bash
curl -X GET http://localhost:8000/view-loan/1
```

**Expected Response:**
```json
{
  "loan_id": 1,
  "customer": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": 9876543210,
    "age": 30
  },
  "loan_amount": 100000.0,
  "interest_rate": 10.0,
  "monthly_installment": 8791.59,
  "tenure": 12
}
```

## 5. View Loans by Customer

```bash
curl -X GET http://localhost:8000/view-loans/1
```

**Expected Response:**
```json
[
  {
    "loan_id": 1,
    "loan_amount": 100000.0,
    "interest_rate": 10.0,
    "monthly_installment": 8791.59,
    "repayments_left": 12
  }
]
```

## Testing Scenarios

### Test Case 1: New Customer with Good Income
```bash
# Register customer with high income
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Alice",
    "last_name": "Smith",
    "age": 35,
    "monthly_income": 100000,
    "phone_number": 9876543211
  }'

# Expected approved_limit: 3600000 (100000 * 36)
```

### Test Case 2: Check Eligibility with Low Interest Rate (Should be corrected)
```bash
# Assuming customer has credit score between 10-30
curl -X POST http://localhost:8000/check-eligibility \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "loan_amount": 50000,
    "interest_rate": 5.0,
    "tenure": 24
  }'

# If credit score is 10-30, corrected_interest_rate should be 16%
```

### Test Case 3: Loan Denial Due to High EMI
```bash
# Try to create loan with very high amount
curl -X POST http://localhost:8000/create-loan \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "loan_amount": 5000000,
    "interest_rate": 10.0,
    "tenure": 12
  }'

# Should deny if EMI > 50% of monthly salary
```

## Postman Collection

Import this JSON into Postman:

```json
{
  "info": {
    "name": "Credit Approval System",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Register Customer",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"first_name\": \"John\",\n  \"last_name\": \"Doe\",\n  \"age\": 30,\n  \"monthly_income\": 50000,\n  \"phone_number\": 9876543210\n}"
        },
        "url": "http://localhost:8000/register"
      }
    },
    {
      "name": "Check Eligibility",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"customer_id\": 1,\n  \"loan_amount\": 100000,\n  \"interest_rate\": 8.0,\n  \"tenure\": 12\n}"
        },
        "url": "http://localhost:8000/check-eligibility"
      }
    },
    {
      "name": "Create Loan",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"customer_id\": 1,\n  \"loan_amount\": 100000,\n  \"interest_rate\": 10.0,\n  \"tenure\": 12\n}"
        },
        "url": "http://localhost:8000/create-loan"
      }
    },
    {
      "name": "View Loan",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/view-loan/1"
      }
    },
    {
      "name": "View Loans by Customer",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/view-loans/1"
      }
    }
  ]
}
```
