# ⚡ Quick Start - 5 Minutes to Running App

## Step 1: Start Application (2 minutes)
```bash
docker-compose up --build
```

Wait for: `"Data ingestion completed successfully!"`

## Step 2: Test API (1 minute)

**Register a customer:**
```bash
curl -X POST http://localhost:8000/register -H "Content-Type: application/json" -d '{"first_name":"John","last_name":"Doe","age":30,"monthly_income":50000,"phone_number":9876543210}'
```

**Check eligibility:**
```bash
curl -X POST http://localhost:8000/check-eligibility -H "Content-Type: application/json" -d '{"customer_id":1,"loan_amount":100000,"interest_rate":10,"tenure":12}'
```

**Create loan:**
```bash
curl -X POST http://localhost:8000/create-loan -H "Content-Type: application/json" -d '{"customer_id":1,"loan_amount":100000,"interest_rate":10,"tenure":12}'
```

## Step 3: View Results

**View loan by ID:**
```bash
curl http://localhost:8000/view-loan/1
```

**View all customer loans:**
```bash
curl http://localhost:8000/view-loans/1
```

## Done! 🎉

Your Credit Approval System is running!

---

## All API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register new customer |
| POST | `/check-eligibility` | Check loan eligibility |
| POST | `/create-loan` | Create new loan |
| GET | `/view-loan/<id>` | View loan details |
| GET | `/view-loans/<customer_id>` | View customer loans |

## Stop Application
```bash
docker-compose down
```

## Run Tests
```bash
docker-compose exec web python manage.py test
```

For detailed documentation, see `README.md`
