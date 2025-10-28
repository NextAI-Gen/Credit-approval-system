from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Customer, Loan
from .utils import calculate_credit_score, calculate_monthly_installment


class CustomerModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            phone_number=9876543210,
            monthly_salary=50000,
            approved_limit=1800000,
            current_debt=0
        )

    def test_customer_creation(self):
        self.assertEqual(self.customer.first_name, 'John')
        self.assertEqual(self.customer.monthly_salary, 50000)


class RegisterAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_customer(self):
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'age': 25,
            'monthly_income': 60000,
            'phone_number': 9876543211
        }
        response = self.client.post('/register', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('customer_id', response.data)
        self.assertEqual(response.data['approved_limit'], 2200000)  # 60000 * 36 rounded to nearest lakh


class CreditScoreTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name='Test',
            last_name='User',
            age=30,
            phone_number=1234567890,
            monthly_salary=50000,
            approved_limit=1800000,
            current_debt=0
        )

    def test_new_customer_credit_score(self):
        score = calculate_credit_score(self.customer)
        self.assertEqual(score, 50)

    def test_credit_score_with_loans(self):
        Loan.objects.create(
            customer=self.customer,
            loan_amount=100000,
            tenure=12,
            interest_rate=10,
            monthly_repayment=8792,
            emis_paid_on_time=12,
            start_date=date.today() - timedelta(days=365),
            end_date=date.today()
        )
        score = calculate_credit_score(self.customer)
        self.assertGreater(score, 50)


class EMICalculationTest(TestCase):
    def test_emi_calculation(self):
        loan_amount = Decimal('100000')
        interest_rate = Decimal('10')
        tenure = 12
        
        emi = calculate_monthly_installment(loan_amount, interest_rate, tenure)
        self.assertGreater(emi, 0)
        self.assertIsInstance(emi, Decimal)


class CheckEligibilityAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create(
            first_name='Test',
            last_name='User',
            age=30,
            phone_number=1234567890,
            monthly_salary=50000,
            approved_limit=1800000,
            current_debt=0
        )

    def test_check_eligibility(self):
        data = {
            'customer_id': self.customer.customer_id,
            'loan_amount': 100000,
            'interest_rate': 10,
            'tenure': 12
        }
        response = self.client.post('/check-eligibility', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('approval', response.data)


class CreateLoanAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create(
            first_name='Test',
            last_name='User',
            age=30,
            phone_number=1234567890,
            monthly_salary=50000,
            approved_limit=1800000,
            current_debt=0
        )

    def test_create_loan_success(self):
        data = {
            'customer_id': self.customer.customer_id,
            'loan_amount': 100000,
            'interest_rate': 10,
            'tenure': 12
        }
        response = self.client.post('/create-loan', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['loan_approved'])
        self.assertIsNotNone(response.data['loan_id'])


class ViewLoanAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create(
            first_name='Test',
            last_name='User',
            age=30,
            phone_number=1234567890,
            monthly_salary=50000,
            approved_limit=1800000,
            current_debt=0
        )
        self.loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=100000,
            tenure=12,
            interest_rate=10,
            monthly_repayment=8792,
            emis_paid_on_time=0,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365)
        )

    def test_view_loan(self):
        response = self.client.get(f'/view-loan/{self.loan.loan_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loan_id'], self.loan.loan_id)

    def test_view_loans_by_customer(self):
        response = self.client.get(f'/view-loans/{self.customer.customer_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
