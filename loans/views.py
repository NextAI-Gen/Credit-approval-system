from decimal import Decimal
from datetime import date, timedelta
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Customer, Loan
from .serializers import (
    RegisterSerializer, CheckEligibilitySerializer, CreateLoanSerializer,
    CustomerSerializer, LoanSerializer, LoanListSerializer
)
from .utils import (
    calculate_monthly_installment, check_loan_eligibility,
    calculate_credit_score
)


@api_view(['POST'])
def register_customer(request):
    """
    Register a new customer with approved limit calculation
    approved_limit = 36 * monthly_salary (rounded to nearest lakh)
    """
    serializer = RegisterSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # Check if customer with this phone number already exists
    if Customer.objects.filter(phone_number=data['phone_number']).exists():
        return Response({
            'error': 'Customer with this phone number already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate approved limit
    monthly_income = Decimal(str(data['monthly_income']))
    approved_limit = monthly_income * 36
    
    # Round to nearest lakh (100,000)
    approved_limit = round(approved_limit / 100000) * 100000
    
    # Create customer
    customer = Customer.objects.create(
        first_name=data['first_name'],
        last_name=data['last_name'],
        age=data['age'],
        phone_number=data['phone_number'],
        monthly_salary=monthly_income,
        approved_limit=approved_limit,
        current_debt=0
    )
    
    response_data = {
        'customer_id': customer.customer_id,
        'name': f"{customer.first_name} {customer.last_name}",
        'age': customer.age,
        'monthly_income': int(customer.monthly_salary),
        'approved_limit': int(customer.approved_limit),
        'phone_number': customer.phone_number
    }
    
    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def check_eligibility(request):
    """
    Check loan eligibility based on credit score
    """
    serializer = CheckEligibilitySerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        customer = Customer.objects.get(customer_id=data['customer_id'])
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    loan_amount = data['loan_amount']
    interest_rate = data['interest_rate']
    tenure = data['tenure']
    
    # Check eligibility
    approval, corrected_rate, monthly_installment, message = check_loan_eligibility(
        customer, loan_amount, interest_rate, tenure
    )
    
    response_data = {
        'customer_id': customer.customer_id,
        'approval': approval,
        'interest_rate': float(interest_rate),
        'corrected_interest_rate': float(corrected_rate),
        'tenure': tenure,
        'monthly_installment': float(monthly_installment)
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_loan(request):
    """
    Process a new loan based on eligibility
    """
    serializer = CreateLoanSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        customer = Customer.objects.get(customer_id=data['customer_id'])
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    loan_amount = data['loan_amount']
    interest_rate = data['interest_rate']
    tenure = data['tenure']
    
    # Check eligibility
    approval, corrected_rate, monthly_installment, message = check_loan_eligibility(
        customer, loan_amount, interest_rate, tenure
    )
    
    if not approval:
        return Response({
            'loan_id': None,
            'customer_id': customer.customer_id,
            'loan_approved': False,
            'message': message,
            'monthly_installment': float(monthly_installment)
        }, status=status.HTTP_200_OK)
    
    # Create loan
    start_date = date.today()
    end_date = start_date + timedelta(days=tenure * 30)  # Approximate
    
    loan = Loan.objects.create(
        customer=customer,
        loan_amount=loan_amount,
        tenure=tenure,
        interest_rate=corrected_rate,
        monthly_repayment=monthly_installment,
        emis_paid_on_time=0,
        start_date=start_date,
        end_date=end_date
    )
    
    # Update customer's current debt
    customer.current_debt += loan_amount
    customer.save()
    
    return Response({
        'loan_id': loan.loan_id,
        'customer_id': customer.customer_id,
        'loan_approved': True,
        'message': 'Loan approved successfully',
        'monthly_installment': float(monthly_installment)
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def view_loan(request, loan_id):
    """
    View loan details by loan_id
    """
    loan = get_object_or_404(Loan, loan_id=loan_id)
    serializer = LoanSerializer(loan)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def view_loans_by_customer(request, customer_id):
    """
    View all loans for a customer
    """
    customer = get_object_or_404(Customer, customer_id=customer_id)
    loans = Loan.objects.filter(customer=customer)
    serializer = LoanListSerializer(loans, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
