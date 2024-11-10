from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.gis.db.models import PointField
from .constants import GENDERS, USER_TYPES, EXPENSES_STATUS,MONTH_CHOICES, PAYMENT_TYPE
from django.urls import reverse
# Create your models here.



class PrimaryUUIDTimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    class Meta(object):
        abstract = True

class User(AbstractUser, PrimaryUUIDTimeStampedModel):
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)
    date_of_birth = models.DateField(null=True, blank=True)
    email = models.EmailField(max_length=40, unique=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    address = models.CharField(max_length=500, null=False,blank=False)
    pincode = models.CharField(max_length=6, blank=False, null=False)
    latitude = models.CharField(max_length=15, blank=True, null=True)
    longitude = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(choices=GENDERS,null=True, blank=True, max_length=50)
    otp = models.CharField(null=True, blank=True, max_length=6)
    otp2 = models.CharField(null=True, blank=True, max_length=6)
    user_type = models.CharField(
        null=False, blank=False, max_length=32, choices=USER_TYPES, 
    )

    
    
    @property
    def full_name(self):
        return "{first_name} {last_name}".format(
            first_name=self.first_name, last_name=self.last_name
        )

    def __str__(self):
        return "{first_name} {last_name}".format(
            first_name=self.first_name, last_name=self.last_name
        )

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
    
    @property
    def is_internal_admin(self):
        if self.user_type =="admin":
            groups = [group.name for group in self.groups.all()]
            return "admin" in groups
        return False
    

class IncomeSource(PrimaryUUIDTimeStampedModel):  # Remove AbstractUser inheritance here
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="user_income_source"
    )
    date = models.DateField(null=False, blank=False)
    month = models.CharField(max_length=50, choices=MONTH_CHOICES, null=False, blank=False)
    income_source = models.CharField(null=False, blank=False,max_length=50)
    amount = models.DecimalField(decimal_places=2, null=False, blank=False, max_digits=10)
    unutilized_amount = models.DecimalField(decimal_places=2, null=False, blank=False, max_digits=10, default=0.0)
    utilized_amount = models.DecimalField(decimal_places=2, null=False, blank=False, max_digits=10,default=0.0)
    


    
class ExpensesType(PrimaryUUIDTimeStampedModel):
    expense_type = models.CharField(max_length=30)

    def __str__(self):
        return self.expense_type


class Expenses(PrimaryUUIDTimeStampedModel):
    expense_type = models.ForeignKey(
        ExpensesType,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="expenses_type"
    )
    date = models.DateField(null=False, blank=False)
    month = models.CharField(max_length=50, choices=MONTH_CHOICES, null=False, blank=False)
    amount = models.DecimalField(decimal_places=2, null=False, blank=False, max_digits=10)
    spent_amount = models.DecimalField(decimal_places=2, null=False, blank=False, max_digits=10, default=0.0)
    pending_amount = models.DecimalField(decimal_places=2, null=False, blank=False, max_digits=10, default=0.0)
    status = models.CharField(max_length=30, choices=EXPENSES_STATUS, default="pending")
    note=models.TextField(max_length=10, null=True, blank=True)
    note2=models.TextField(max_length=10, null=True, blank=True)

    def __str__(self):
            return self.expense_type.expense_type 



class ExpensesDetails(PrimaryUUIDTimeStampedModel):
    expense = models.ForeignKey(
        Expenses,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="expenses_details"
    )
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="user_expenses"
    )
    date = models.DateField(null=False, blank=False)
    month = models.CharField(max_length=50, choices=MONTH_CHOICES, null=False, blank=False)
    amount = models.DecimalField(decimal_places=2, null=False, blank=False, max_digits=10)
    notes = models.TextField(blank=True, max_length=100)

    def __str__(self):
        return self.expense.expense_type.expense_type