from rest_framework import serializers
from .models import Expenses, ExpensesDetails, ExpensesType, IncomeSource, User
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

class UserSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = User
        fields = (  'id',
                    'email',
                    'first_name',
                    'last_name',
                    'address',
                    'pincode',
                    'gender',
                    'user_type',
                    'phone_number',
                    'username',
                    'date_of_birth',
                    'latitude',
                    'longitude'
                
                )

        extra_kwargs = {
            'latitude': {'required': False},
            'longitude': {'required': False},
        }
     

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "name")

class IncomeSourceCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = IncomeSource
        fields = ( 
            "user",
            "date",
            "month",
            "income_source",
            "amount",
            "unutilized_amount"
         )
        
class IncomeSourceSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
   
    class Meta:
        model = IncomeSource
        fields = ( 
            "id",
            "created_at",
            "name",
            "date",
            "month",
            "income_source",
            "amount",
            "unutilized_amount",
            "utilized_amount"
         )
    def get_name(self,obj):
        return obj.user.full_name


class ExpensesTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpensesType
        fields = ( 
            "id",
            "created_at",
            "expense_type"
         )


class ExpensesCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expenses
        fields = ( 
            "expense_type",
            "date",
            "month",
            "amount",
            "pending_amount"
         )
        
class ExpensesSerializer(serializers.ModelSerializer):
    expenses_name = serializers.SerializerMethodField()

    class Meta:
        model = Expenses
        fields = ( 
            "id",
            "created_at",
            "expenses_name",
            "expense_type",
            "month",
            "date",
            "amount",
            "spent_amount",
            "pending_amount",
            "status",
            "note",
            "note2"
            
         )
        
    def get_expenses_name(self,obj):
        return obj.expense_type.expense_type  if obj.expense_type else None
    




class ExpensesDetailsSerializer(serializers.ModelSerializer):
    expenses_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    class Meta:
        model = ExpensesDetails
        fields = ( 
            "id",
            "created_at",
            "user_name",
            "expenses_name",
            "date",
            "month",
            "amount",
            "notes"

        )

    def get_user_name(self,obj):
        return obj.user.full_name
    
    def get_expenses_name(self,obj):
        return obj.expense.expense_type.expense_type
    
    

    

class ExpensesDetailsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpensesDetails
        fields = ( 
            "expense",
            "user",
            "date",
            "month",
            "amount",
            "notes"
        )


class FamilyMemberSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ( 
            "id",
            "name",
            "first_name"
        )

    def get_name(self,obj):
        return obj.full_name
