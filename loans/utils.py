from datetime import datetime
from decimal import Decimal
from django.db.models import Sum, Count, Q
from .models import Loan


def calculate_credit_score(customer):
    """
    Calculate credit score based on:
    i. Past Loans paid on time
    ii. Number of loans taken in past
    iii. Loan activity in current year
    iv. Loan approved volume
    v. Current loans vs approved limit
    """
    
    # Get all loans for the customer
    loans = Loan.objects.filter(customer=customer)
    
    if not loans.exists():
        return 50  # Default score for new customers
    
    # Check if sum of current loans > approved limit
    current_loans_sum = loans.aggregate(
        total=Sum('loan_amount')
    )['total'] or Decimal('0')
    
    if current_loans_sum > customer.approved_limit:
        return 0
    
    score = 0
    total_loans = loans.count()
    
    # Component 1: Past Loans paid on time (40 points)
    if total_loans > 0:
        on_time_payments = sum([
            min(loan.emis_paid_on_time / loan.tenure, 1.0) 
            for loan in loans if loan.tenure > 0
        ]) / total_loans
        score += on_time_payments * 40
    
    # Component 2: Number of loans (20 points)
    # Optimal: 2-5 loans. Too few or too many reduces score
    if total_loans == 0:
        loan_count_score = 0
    elif 2 <= total_loans <= 5:
        loan_count_score = 20
    elif total_loans == 1:
        loan_count_score = 10
    elif 6 <= total_loans <= 10:
        loan_count_score = 15
    else:
        loan_count_score = 5
    score += loan_count_score
    
    # Component 3: Loan activity in current year (20 points)
    current_year = datetime.now().year
    current_year_loans = loans.filter(
        Q(start_date__year=current_year) | Q(end_date__year=current_year)
    ).count()
    
    if current_year_loans > 0:
        score += min(current_year_loans * 5, 20)
    
    # Component 4: Loan approved volume (20 points)
    total_approved_volume = loans.aggregate(
        total=Sum('loan_amount')
    )['total'] or Decimal('0')
    
    if customer.approved_limit > 0:
        utilization_ratio = float(total_approved_volume / customer.approved_limit)
        # Optimal utilization: 30-70%
        if 0.3 <= utilization_ratio <= 0.7:
            score += 20
        elif 0.1 <= utilization_ratio < 0.3:
            score += 15
        elif 0.7 < utilization_ratio <= 0.9:
            score += 10
        else:
            score += 5
    
    return min(round(score), 100)


def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    """
    Calculate monthly installment using compound interest formula
    EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)
    where:
    P = loan_amount
    r = monthly interest rate (annual rate / 12 / 100)
    n = tenure in months
    """
    if tenure == 0:
        return Decimal('0')
    
    P = Decimal(str(loan_amount))
    r = Decimal(str(interest_rate)) / Decimal('12') / Decimal('100')
    n = Decimal(str(tenure))
    
    if r == 0:
        return P / n
    
    # EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)
    one_plus_r = Decimal('1') + r
    one_plus_r_power_n = one_plus_r ** n
    
    emi = (P * r * one_plus_r_power_n) / (one_plus_r_power_n - Decimal('1'))
    
    return round(emi, 2)


def get_corrected_interest_rate(credit_score, requested_rate):
    """
    Return corrected interest rate based on credit score
    """
    if credit_score > 50:
        # Any rate is acceptable
        return requested_rate
    elif 30 < credit_score <= 50:
        # Minimum 12%
        return max(requested_rate, Decimal('12.0'))
    elif 10 < credit_score <= 30:
        # Minimum 16%
        return max(requested_rate, Decimal('16.0'))
    else:
        # No loan approval
        return requested_rate


def check_loan_eligibility(customer, loan_amount, interest_rate, tenure):
    """
    Check if loan can be approved based on credit score and EMI ratio
    Returns: (approval_status, corrected_interest_rate, monthly_installment, message)
    """
    credit_score = calculate_credit_score(customer)
    corrected_rate = get_corrected_interest_rate(credit_score, Decimal(str(interest_rate)))
    
    # Calculate monthly installment with corrected rate
    monthly_installment = calculate_monthly_installment(loan_amount, corrected_rate, tenure)
    
    # Check if credit score allows loan
    if credit_score <= 10:
        return False, corrected_rate, monthly_installment, "Credit score too low for loan approval"
    
    # Check if sum of all current EMIs > 50% of monthly salary
    current_emis = Loan.objects.filter(customer=customer).aggregate(
        total_emi=Sum('monthly_repayment')
    )['total_emi'] or Decimal('0')
    
    total_emi_with_new_loan = current_emis + monthly_installment
    
    if total_emi_with_new_loan > (customer.monthly_salary * Decimal('0.5')):
        return False, corrected_rate, monthly_installment, "Sum of EMIs exceeds 50% of monthly salary"
    
    # Loan approved
    return True, corrected_rate, monthly_installment, "Loan approved"
