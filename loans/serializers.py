from rest_framework import serializers
from .models import Customer, Loan


class CustomerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'age', 'monthly_salary', 'approved_limit', 'phone_number']

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class CustomerDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='customer_id', read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'age']


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    age = serializers.IntegerField(min_value=18)
    monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    phone_number = serializers.IntegerField()


class CheckEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0)
    tenure = serializers.IntegerField(min_value=1)


class CreateLoanSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0)
    tenure = serializers.IntegerField(min_value=1)


class LoanSerializer(serializers.ModelSerializer):
    customer = CustomerDetailSerializer(read_only=True)
    monthly_installment = serializers.DecimalField(source='monthly_repayment', max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'loan_amount', 'interest_rate', 'monthly_installment', 'tenure']


class LoanListSerializer(serializers.ModelSerializer):
    repayments_left = serializers.IntegerField(read_only=True)
    monthly_installment = serializers.DecimalField(source='monthly_repayment', max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_installment', 'repayments_left']
