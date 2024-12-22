
import uuid
from django.db import models
from datetime import datetime, timedelta
import base64
import string 
from django.core.cache import cache
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.mail import send_mail

from .models import Expenses, ExpensesDetails, IncomeSource

def verify_otp(user_id, otp):
    PASSWORD_RESET_KEY = "user_password_reset_key.{otp_key}"
    base_otp_key = base64.b64encode(str(user_id).encode()).decode()

    otp_key = PASSWORD_RESET_KEY.format(otp_key=base_otp_key)

    cached_otp = cache.get(otp_key)

    if cached_otp is None:
        return "otp_expired", None

    if not cached_otp == otp:
        return "otp_invalid", None

    return None, otp_key


def generate_otp_and_key(uuid, secret_key):
    otp = get_random_string(length=6, allowed_chars=string.digits)
    base_otp_key = base64.b64encode(str(uuid).encode()).decode()
    otp_key = secret_key.format(otp_key=base_otp_key)

    return otp, otp_key


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_custom_email(recipient_email, subject, body):
    # Create a MIMEMultipart object
    sender_email= settings.EMAIL_HOST_USER
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = "vijaythorat0804@gmail.com"
    msg['Subject'] = subject
    
    # Attach the email body to the message
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Set up the SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Start TLS for security
        
        # Log in to the server
        server.login(sender_email, settings.EMAIL_HOST_PASSWORD)
        
        # Send the email
        server.send_message(msg)
        
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")
    finally:
        server.quit()




def spend_money(expense, amt, incomes, request):
    user_id = request.data.get('user')
    date=request.data.get('date')
    month=request.data.get('month')
    notes=request.data.get('notes')
    new_spent_amt = float(expense.spent_amount) + float(amt)
    expense.spent_amount= new_spent_amt
    expense.pending_amount = float(expense.amount) - new_spent_amt
    if expense.amount<=new_spent_amt:
        expense.status="done"
    expense.save()


    create_expense_dtl = []
    update_rows = []
    amount = amt
    for income in incomes:
        if amount!=0.0:
            if amount > income.unutilized_amount:
                action_amt= income.unutilized_amount
                print("amout is less")
                amount = amount - float(income.unutilized_amount)
                income.utilized_amount = float(income.utilized_amount) + float(action_amt)
                income.unutilized_amount= 0.0
                update_rows.append(income)
            elif amount < income.unutilized_amount:
                action_amt= amount
                print("amout is less")
                income.utilized_amount = float(income.utilized_amount) + amount
                income.unutilized_amount= float(income.unutilized_amount) - amount
                update_rows.append(income)
                amount= 0.0

            elif amount == income.unutilized_amount:
                action_amt= amount
                print("amout perfect match")
                income.utilized_amount = float(income.utilized_amount) + amount
                income.unutilized_amount= float(income.unutilized_amount) - amount
                update_rows.append(income)
                amount= 0.0

            
            create_expense_dtl.append(
                ExpensesDetails(
                    expense=expense,
                    user_id=user_id,
                    income_sorce=income,
                    date=date,
                    month=month,
                    amount=action_amt,
                    notes=notes
                )

            )

    if create_expense_dtl:
        ExpensesDetails.objects.bulk_create(create_expense_dtl)

    if update_rows:
        print("inside update_rows")
        IncomeSource.objects.bulk_update(update_rows, ["utilized_amount", "unutilized_amount"])

    
    return True


def settle_income(income_source_instance,request):

    date=str(datetime.now().date())
    year = date.split('-')[0]
    current_datetime = datetime.now()
    month_name = current_datetime.strftime('%B').lower()

    expenses = Expenses.objects.filter(year=year,month=month_name,status="pending").order_by("expense_type__priority")
                
    amount=income_source_instance.unutilized_amount
    update_expense = []
    create_expense_dtl =[]
    used_amt = 0.0
    for expense in expenses:
        print("amt",amount)
        if amount>0.0:
            expense_dtl = ExpensesDetails(
                expense=expense,
                user=request.user,
                income_sorce=income_source_instance,
                date=date,
                month=month_name,
                year=year,
                notes="Auto setteled"

            )
        
            ex_pending = float(expense.pending_amount)
            print("ex_pending",ex_pending)
            if amount>=ex_pending:
                print("amount is greater")
                expense.pending_amount=float(expense.pending_amount)- ex_pending
                expense.spent_amount = float(expense.spent_amount) + ex_pending
                expense.status = "done"
                update_expense.append(expense)

                expense_dtl.amount= ex_pending
                amount= amount - ex_pending
                print(ex_pending)
                used_amt = used_amt + ex_pending
                print(used_amt)

            elif amount<ex_pending:
                print("amount is less")
                expense.pending_amount=float(expense.pending_amount) - amount
                expense.spent_amount = float(expense.spent_amount) + amount
                expense.status = "pending"
                update_expense.append(expense)
                expense_dtl.amount= amount
                used_amt = used_amt + amount
                amount= amount - amount
                
                print(used_amt)
        else:
            break

        create_expense_dtl.append(expense_dtl)
    ExpensesDetails.objects.bulk_create(create_expense_dtl, ignore_conflicts=True)
    Expenses.objects.bulk_update(update_expense,["pending_amount","spent_amount","status"])
   
    print(used_amt)
    print(income_source_instance.unutilized_amount)
    print(income_source_instance.utilized_amount)

    income_source_instance.unutilized_amount=income_source_instance.unutilized_amount - used_amt
    income_source_instance.utilized_amount=float(income_source_instance.utilized_amount) + used_amt
    income_source_instance.save()
    return True