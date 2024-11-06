from .models import *


class UserQueryset:
    def custom_get_queryset(self):
        if self.action =="list":
            queryset = User.objects.all()
            return queryset.order_by("-created_at")
        

class IncomeSourceQueryset:
    def custom_get_queryset(self):
        if self.action =="list":
            queryset = IncomeSource.objects.all()
            return queryset.order_by("-created_at")
        
class ExpensesTypeSourceQueryset:
    def custom_get_queryset(self):
        if self.action =="list":
            queryset = ExpensesType.objects.all()
            return queryset.order_by("-created_at")
        
class ExpensesQueryset:
    def custom_get_queryset(self):
        if self.action =="list":
            queryset = Expenses.objects.all()
            return queryset.order_by("-status")
        
class ExpensesDetailsQueryset:
    def custom_get_queryset(self):
        if self.action =="list":
            queryset = ExpensesDetails.objects.all()
            return queryset.order_by("-created_at")