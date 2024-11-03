import datetime
import django_filters
from .models import Expenses, ExpensesDetails, ExpensesType, IncomeSource, User
from django_filters import rest_framework as filters
from time import mktime, strptime
from django.db.models import Q



class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'address', 'pincode',
            'gender', 'user_type', 'phone_number', 'username', 'date_of_birth',
        ]


class IncomeSourceFilter(django_filters.FilterSet):
    ed = filters.CharFilter(method= "to_method")
    sd = filters.CharFilter(method= "from_method")
    name = filters.CharFilter(method= "search_name")


    def to_method(self, queryset, name, value):
        t =strptime(value, '%Y-%m-%d')
        dt = datetime.datetime.fromtimestamp(mktime(t)) + datetime.timedelta(hours=18, minutes=30)
        dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        queryset = queryset.filter(date__lte =value)
        return queryset

    def from_method(self, queryset, name, value):
        t =strptime(value, '%Y-%m-%d')
        dt = datetime.datetime.fromtimestamp(mktime(t)) - datetime.timedelta(hours=5, minutes=30)
        dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        queryset = queryset.filter(date__gte = value)
        return queryset
    
    def search_name(self, queryset, name, value):
        queryset = queryset.filter(
                                    Q(user__first_name__icontains = value) | Q(user__last_name__icontains = value) 
                                   )
        return queryset
    
    class Meta:
        model = IncomeSource
        fields = ["date", "month", "user"]





class ExpensesFilter(django_filters.FilterSet):
    ed = filters.CharFilter(method= "to_method")
    sd = filters.CharFilter(method= "from_method")
    q = filters.CharFilter(method= "search_q")


    def to_method(self, queryset, name, value):
        t =strptime(value, '%Y-%m-%d')
        dt = datetime.datetime.fromtimestamp(mktime(t)) + datetime.timedelta(hours=18, minutes=30)
        dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        queryset = queryset.filter(date__lte = value)
        return queryset

    def from_method(self, queryset, name, value):
        t =strptime(value, '%Y-%m-%d')
        dt = datetime.datetime.fromtimestamp(mktime(t)) - datetime.timedelta(hours=5, minutes=30)
        dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        queryset = queryset.filter(date__gte = value)
        return queryset
    
    def search_q(self, queryset, name, value):
        queryset = queryset.filter(
                                    Q(expense_type__expense_type__icontains = value)
                                   )
        return queryset
    
    class Meta:
        model = Expenses
        fields = ["date", "month", "amount","status"]


class  ExpensesDetailsFilter(django_filters.FilterSet):
    ed = filters.CharFilter(method= "to_method")
    sd = filters.CharFilter(method= "from_method")
    q = filters.CharFilter(method= "search_q")


    def to_method(self, queryset, name, value):
        t =strptime(value, '%Y-%m-%d')
        dt = datetime.datetime.fromtimestamp(mktime(t)) + datetime.timedelta(hours=18, minutes=30)
        dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        queryset = queryset.filter(date__lte = value)
        return queryset

    def from_method(self, queryset, name, value):
        t =strptime(value, '%Y-%m-%d')
        dt = datetime.datetime.fromtimestamp(mktime(t)) - datetime.timedelta(hours=5, minutes=30)
        dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        queryset = queryset.filter(date__gte = value)
        return queryset
    
    def search_q(self, queryset, name, value):
        queryset = queryset.filter(
                                    Q(expense__expense_type__expense_type__icontains = value)
                                   )
        return queryset
    
    class Meta:
        model = ExpensesDetails
        fields = ["date", "month", "amount"]


class ExpensesTypeFilter(django_filters.FilterSet):
    ed = filters.CharFilter(method= "to_method")
    sd = filters.CharFilter(method= "from_method")
    q = filters.CharFilter(method= "search_q")


    def to_method(self, queryset, name, value):
        t =strptime(value, '%Y-%m-%d')
        dt = datetime.datetime.fromtimestamp(mktime(t)) + datetime.timedelta(hours=18, minutes=30)
        dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        queryset = queryset.filter(date__lte = value)
        return queryset

    def from_method(self, queryset, name, value):
        t =strptime(value, '%Y-%m-%d')
        dt = datetime.datetime.fromtimestamp(mktime(t)) - datetime.timedelta(hours=5, minutes=30)
        dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        queryset = queryset.filter(date__gte = value)
        return queryset
    
    def search_q(self, queryset, name, value):
        queryset = queryset.filter(
                                    Q(expense_type__icontains = value)
                                   )
        return queryset
    
    class Meta:
        model = ExpensesType
        fields = ["expense_type"]