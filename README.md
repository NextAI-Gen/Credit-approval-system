# Credit Approval System - Backend Assignment

A Django REST Framework application for credit approval system based on customer credit scores and loan history.

## 🚀 Features

- **Customer Registration** with automatic credit limit calculation
- **Credit Score Calculation** based on multiple factors:
  - Past loan payment history
  - Number of loans taken
  - Current year loan activity
  - Loan approved volume
- **Loan Eligibility Check** with intelligent interest rate correction
- **Loan Creation** with validation
- **Loan Viewing** endpoints for individual and customer loans

## 🛠️ Tech Stack

- **Django 4.2+**
- **Django REST Framework**
- **PostgreSQL**
- **Celery** for background tasks
- **Redis** as message broker
- **Docker & Docker Compose**
- **Pandas** for data ingestion

## 📋 Prerequisites

- Docker
- Docker Compose

That's it! Everything else runs in containers.

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/NextAI-Gen/Credit-approval-system.git
cd Credit-approval-system
```

### 2. Run the application

```bash
docker-compose up --build
```

This single command will:
- Set up PostgreSQL database
- Set up Redis
- Install all dependencies
- Run migrations
- Ingest data from Excel files
- Start the Django development server on `http://localhost:8000`
- Start Celery worker

### 3. Access the application

- **API Base URL**: `http://localhost:8000`
- **Admin Panel**: `http://localhost:8000/admin`

## 📚 API Endpoints

### 1. Register Customer
**POST** `/register`

Register a new customer with automatic credit limit calculation.

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "monthly_income": 50000,
  "phone_number": 9876543210
}
```

**Response:**
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

### 2. Check Loan Eligibility
**POST** `/check-eligibility`

Check if a customer is eligible for a loan with interest rate correction.

**Request Body:**
```json
{
  "customer_id": 1,
  "loan_amount": 100000,
  "interest_rate": 8.0,
  "tenure": 12
}
```

**Response:**
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

### 3. Create Loan
**POST** `/create-loan`

Create a new loan if eligible.

**Request Body:**
```json
{
  "customer_id": 1,
  "loan_amount": 100000,
  "interest_rate": 10.0,
  "tenure": 12
}
```

**Response (Success):**
```json
{
  "loan_id": 1,
  "customer_id": 1,
  "loan_approved": true,
  "message": "Loan approved successfully",
  "monthly_installment": 8791.59
}
```

**Response (Failure):**
```json
{
  "loan_id": null,
  "customer_id": 1,
  "loan_approved": false,
  "message": "Credit score too low for loan approval",
  "monthly_installment": 8791.59
}
```

### 4. View Loan
**GET** `/view-loan/<loan_id>`

Get details of a specific loan.

**Response:**
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

### 5. View Loans by Customer
**GET** `/view-loans/<customer_id>`

Get all loans for a specific customer.

**Response:**
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

## 🧪 Running Tests

```bash
docker-compose exec web python manage.py test
```

## 📊 Credit Score Algorithm

The credit score (0-100) is calculated based on:

1. **Past Loans Paid On Time (40 points)**
   - Higher percentage of EMIs paid on time = higher score

2. **Number of Loans (20 points)**
   - Optimal: 2-5 loans
   - Too few or too many reduces score

3. **Loan Activity in Current Year (20 points)**
   - Recent loan activity indicates active credit usage

4. **Loan Approved Volume (20 points)**
   - Optimal credit utilization: 30-70% of approved limit

### Loan Approval Rules

- **Credit Score > 50**: Approve at any interest rate
- **30 < Credit Score ≤ 50**: Approve with minimum 12% interest rate
- **10 < Credit Score ≤ 30**: Approve with minimum 16% interest rate
- **Credit Score ≤ 10**: Deny loan
- **EMI > 50% of salary**: Deny loan

## 🗂️ Project Structure

```
.
├── credit_system/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── loans/                  # Main application
│   ├── models.py          # Customer and Loan models
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API endpoints
│   ├── utils.py           # Credit score & EMI calculations
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin configuration
│   ├── tests.py           # Unit tests
│   └── management/
│       └── commands/
│           └── ingest_data.py  # Data ingestion command
├── customer_data.xlsx     # Initial customer data
├── loan_data.xlsx         # Initial loan data
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
└── README.md             # This file
```

## 🔧 Development

### Access Django Shell

```bash
docker-compose exec web python manage.py shell
```

### Create Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

### View Logs

```bash
docker-compose logs -f web
docker-compose logs -f celery
```

### Stop Services

```bash
docker-compose down
```

### Remove All Data

```bash
docker-compose down -v
```

## 📝 Data Ingestion

The application automatically ingests data from `customer_data.xlsx` and `loan_data.xlsx` on startup. The management command:

```bash
python manage.py ingest_data
```

This command:
- Reads Excel files using Pandas
- Creates Customer and Loan records
- Uses database transactions for data integrity
- Skips duplicate entries

## 🏗️ Architecture Decisions

1. **Docker Compose**: Single command deployment with all dependencies
2. **PostgreSQL**: Production-grade relational database
3. **Celery + Redis**: Background task processing (data ingestion)
4. **Decimal Fields**: Accurate financial calculations
5. **Compound Interest**: EMI calculation using standard formula
6. **Atomic Transactions**: Data consistency during ingestion
7. **REST API**: Stateless, scalable API design

## 🎯 Key Highlights

✅ Complete API implementation as per requirements  
✅ Dockerized with single command deployment  
✅ Background data ingestion with Celery  
✅ Comprehensive unit tests  
✅ Clean code organization  
✅ Production-ready error handling  
✅ Proper credit score algorithm  
✅ Compound interest EMI calculation  
✅ Django admin panel integration  

## 📧 Contact

For questions or issues, please contact the repository maintainer.

---

**Assignment completed for Alemeno Backend Internship**
