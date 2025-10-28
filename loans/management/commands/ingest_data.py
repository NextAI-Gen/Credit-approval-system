import os
import pandas as pd
from datetime import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from loans.models import Customer, Loan


class Command(BaseCommand):
    help = 'Ingest customer and loan data from Excel files'

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        customer_file = os.path.join(base_dir, 'customer_data.xlsx')
        loan_file = os.path.join(base_dir, 'loan_data.xlsx')
        
        # Check if files exist
        if not os.path.exists(customer_file):
            self.stdout.write(self.style.ERROR(f'Customer file not found: {customer_file}'))
            return
        
        if not os.path.exists(loan_file):
            self.stdout.write(self.style.ERROR(f'Loan file not found: {loan_file}'))
            return
        
        self.stdout.write(self.style.SUCCESS('Starting data ingestion...'))
        
        try:
            with transaction.atomic():
                # Ingest customers
                self.stdout.write('Ingesting customer data...')
                self.ingest_customers(customer_file)
                
                # Ingest loans
                self.stdout.write('Ingesting loan data...')
                self.ingest_loans(loan_file)
            
            self.stdout.write(self.style.SUCCESS('Data ingestion completed successfully!'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during ingestion: {str(e)}'))
            raise

    def ingest_customers(self, file_path):
        """Ingest customer data from Excel file"""
        df = pd.read_excel(file_path)
        
        customers_created = 0
        
        for _, row in df.iterrows():
            # Check if customer already exists
            if Customer.objects.filter(customer_id=row['Customer ID']).exists():
                continue
            
            Customer.objects.create(
                customer_id=int(row['Customer ID']),
                first_name=str(row['First Name']),
                last_name=str(row['Last Name']),
                age=25,  # Default age as not in Excel
                phone_number=int(row['Phone Number']),
                monthly_salary=Decimal(str(row['Monthly Salary'])),
                approved_limit=Decimal(str(row['Approved Limit'])),
                current_debt=Decimal(str(row.get('Current Debt', 0)))
            )
            customers_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {customers_created} customers'))

    def ingest_loans(self, file_path):
        """Ingest loan data from Excel file"""
        df = pd.read_excel(file_path)
        
        loans_created = 0
        
        for _, row in df.iterrows():
            # Check if loan already exists
            if Loan.objects.filter(loan_id=row['Loan ID']).exists():
                continue
            
            try:
                customer = Customer.objects.get(customer_id=int(row['Customer ID']))
            except Customer.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'Customer {row["Customer ID"]} not found for loan {row["Loan ID"]}, skipping...'
                ))
                continue
            
            # Parse dates
            start_date = pd.to_datetime(row['Date of Approval']).date()
            end_date = pd.to_datetime(row['End Date']).date()
            
            Loan.objects.create(
                loan_id=int(row['Loan ID']),
                customer=customer,
                loan_amount=Decimal(str(row['Loan Amount'])),
                tenure=int(row['Tenure']),
                interest_rate=Decimal(str(row['Interest Rate'])),
                monthly_repayment=Decimal(str(row['Monthly payment'])),
                emis_paid_on_time=int(row['EMIs paid on Time']),
                start_date=start_date,
                end_date=end_date
            )
            loans_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {loans_created} loans'))
