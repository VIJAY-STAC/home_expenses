import re
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from django.conf import settings
from django.dispatch import receiver
from rest_framework.decorators import action
from django.db.models import Sum, F
from django.utils import timezone
from .permissions import IsInternalAdmin
from .pagination import CommanPagination
from django.db.models.functions import TruncSecond
from .querysets import ExpensesDetailsQueryset, ExpensesQueryset, ExpensesTypeSourceQueryset, IncomeSourceQueryset, UserQueryset
from .filters import ExpensesDetailsFilter, ExpensesFilter, ExpensesTypeFilter, IncomeSourceFilter, UserFilter
from .utils import generate_otp_and_key, send_custom_email, spend_money
from .serializers import ExpensesCreateSerializer, ExpensesDetailsCreateSerializer, ExpensesDetailsSerializer, ExpensesDetailsUpdateSerializer, ExpensesSerializer, ExpensesTypeSerializer, FamilyMemberSerializer, IncomeSourceCreateSerializer, IncomeSourceSerializer, UserRoleSerializer, UserSerializer
from .models import BulkBuyerResvStock, BusinessTermsTable, Expenses, ExpensesType, IncomeSource, User, ExpensesDetails
from datetime import datetime, timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group
from rest_framework import parsers, status, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from django.db.models import Q
User = get_user_model()

# Create your views here.


class UserViewSet(viewsets.ModelViewSet, UserQueryset):
    model = User
    serializer_class = UserSerializer
    parser_classes = (parsers.FormParser, parsers.JSONParser)
    filter_backends = (DjangoFilterBackend,)
    filter_class = UserFilter
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CommanPagination



    def get_queryset(self):
        queryset = self.custom_get_queryset()
        return queryset

    def create(self, request, *args, **kwargs):
        return Response({},status=status.HTTP_405_METHOD_NOT_ALLOWED)


    @action(detail=False, methods=['post'],  permission_classes=[])
    def user_create(self, request, *args, **kwargs):
        user_data = request.data
        email = user_data.get('email', None)
        mb = user_data.get('phone_number', None)
        pincode = request.data.get('pincode', None)
        user_type = request.data.get('user_type', None)
        if not pincode:
            return Response({"error": "Pincode is required"},status=status.HTTP_400_BAD_REQUEST)
        if not user_type:
            return Response({"error": "user_type is required"},status=status.HTTP_400_BAD_REQUEST)
        
        if len(pincode)>6:
             return Response({"error": "pincode should be contains 6 digits."},status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(Q(phone_number=mb) | Q(email=email))

        if user:
            return Response({"error": "user already exist with given email or mobile number"},status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        if not id:
            return Response({"error":"product id is missing"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            route=User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"error":"user does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(route, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_route=serializer.save()
        serializer=UserSerializer(updated_route)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def retrieve(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        try:
            user=User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"error":"user does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)
        serializer=UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def destroy(self, request, *args, **kwargs):  
        id = kwargs.get('pk')
        if not request.user.is_superuser and request.user.user_type != 'admin':
            return Response({"error":"permission not allowed."}, status=status.HTTP_403_FORBIDDEN)
        try:
            user=User.objects.get(id=id).delete()
        except User.DoesNotExist:
            return Response({"error":"user does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({},status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'],  permission_classes=[])
    def login(self, request, *args, **kwargs):
        try:
            email = request.data['email']
            password = request.data['password']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": f"Email id is not registered.", "stat": False}, status=status.HTTP_400_BAD_REQUEST)

            if not user.check_password(password):
                return Response({"error": "incorrect_credentials","stat": False}, status=status.HTTP_400_BAD_REQUEST)

            refresh = RefreshToken.for_user(user)

            user_details = {
                'id': user.id,
                'name': f"{user.first_name} {user.last_name}",
                'access_token': str(refresh.access_token),
                'stat': True,
	            'message': "Login successful",
                'user_type': user.user_type,
                'pincode': user.pincode,
                'latitude': user.latitude,
                'longitude': user.longitude,
                "success": True
               
            }

            return Response(user_details, status=status.HTTP_200_OK)
        except KeyError:
            res = {'error': 'Please provide an email and a password'}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[])
    def forgot_password(self, request, *args, **kwargs):
        from django.core.mail import send_mail
        PASSWORD_RESET_KEY = "user_password_reset_key.{otp_key}"
        email = request.data.get('email')
        
        if not email:
            return Response({"error": "Email field is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": f"User with email {email} is not registered."}, status=status.HTTP_400_BAD_REQUEST)

        if user.otp:
            otp = str(user.otp)[:6]
        else:
            otp, otp_key = generate_otp_and_key(
                uuid=user.id, secret_key=PASSWORD_RESET_KEY)
            user.otp = otp
            user.save()

        subject = "OTP from Home Expense App"
        message = f"Your One Time Password (OTP) is: {otp}"
        print(message)
        recipient_list = [user.email]
        
        try:
            send_custom_email(recipient_list, subject, message)
        except Exception as e:
            return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "OTP sent to the registered email ID."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[])
    def set_new_password(self, request, *args, **kwargs):
        email = request.data['email']
        password = request.data['password']
        otp = request.data['otp']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": f"user with {email} is not registered."}, status=status.HTTP_400_BAD_REQUEST)

        if user.otp:
            if otp !=user.otp:
                return Response({"error":"invalid otp."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error":"otp expired."}, status=status.HTTP_400_BAD_REQUEST)

        
        user.set_password(password)
        user.save(update_fields=["password"])
        user.otp=None
        user.save()
        return Response({"message":"Password changed succesfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[])
    def otp_verification(self, request, *args, **kwargs):
        otp = request.data.get('otp', None)
        email = request.data['email']
        user = User.objects.get(email=email)
        if not otp:
            return Response({"error":"opt is required."}, status=status.HTTP_400_BAD_REQUEST)
        # response, otp_key = verify_otp(user_id=user.id, otp=otp)        
        if user.otp:
            if otp !=user.otp:
                return Response({"error":"invalid otp."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error":"otp expired."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"OTP verified."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def create_roles(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"error":"permission not allowed."}, status=status.HTTP_403_FORBIDDEN)
        role_name= request.data.get("role_name")
        pattern = r"^[a-z_]+$"
        if not re.match(pattern, role_name):
            return Response({"error":"Role name should be in lowercase, does not contain spaces and should contains alphabetical characters and underscores."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            role = Group.objects.get(name=role_name)
            if role:
                return Response({"error":"Roles alerady exist with given name."}, status=status.HTTP_400_BAD_REQUEST)
        except:
            pass
        new_role = Group.objects.create(name=role_name)
        serializer = UserRoleSerializer(new_role)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["get"])
    def family_list(self, request, *args, **kwargs):
        members = User.objects.all()
        serializer = FamilyMemberSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class IncomeSourceViewSet(viewsets.ModelViewSet, IncomeSourceQueryset):
    model = IncomeSource
    serializer_class = IncomeSourceSerializer
    parser_classes = (parsers.FormParser, parsers.JSONParser)
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IncomeSourceFilter
    pagination_class = CommanPagination

    def get_queryset(self):
        queryset = self.custom_get_queryset()
        return queryset
    
    def create(self, request, *args, **kwargs):
        if request.user.user_type !="admin":
            return Response({"error": "You do not have permissions to perform this operations"}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        data["unutilized_amount"]=data["amount"]
        serializer = IncomeSourceCreateSerializer(data=data)
        if serializer.is_valid():
            income_source_instance = serializer.save()  # Save the instance
            response_serializer = IncomeSourceSerializer(income_source_instance)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        

    def update(self, request, *args, **kwargs):
        if request.user.user_type !="admin":
            return Response({"error": "You do not have permissions to perform this operations"}, status=status.HTTP_404_NOT_FOUND)
        
        id = kwargs.get('pk')
        data=request.data
        if not id:
            return Response({"error":"Income source id is missing"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            income_souce=IncomeSource.objects.get(id=id)
        except IncomeSource.DoesNotExist:
            return Response({"error":"IncomeSource does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)
        if income_souce.utilized_amount>data["amount"]:
            return Response({"error":"Income source amount should be greater than utilized income amount."}, status=status.HTTP_400_BAD_REQUEST)
       
        data["unutilized_amount"]=data["amount"]- float(income_souce.utilized_amount)
        serializer = IncomeSourceCreateSerializer(income_souce, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        income_souce=serializer.save()
        serializer=IncomeSourceSerializer(income_souce)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        total_income_amount = queryset.aggregate(total_income=Sum('amount'))['total_income'] or 0
        spent_income_amount = queryset.aggregate(utilized_amount=Sum('utilized_amount'))['utilized_amount'] or 0
        avai_income_amount = total_income_amount - spent_income_amount
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = {
                'total_income_amount': float(total_income_amount),
                'spent_income_amount':float(spent_income_amount),
                'available_income_amount':float(avai_income_amount),
                'results': serializer.data
            }
            return self.get_paginated_response(response_data)
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            'total_income_amount': total_income_amount,
            'results': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):  
       return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


class ExpensesTypeViewSet(viewsets.ModelViewSet, ExpensesTypeSourceQueryset):
    model = ExpensesType
    serializer_class = ExpensesTypeSerializer
    parser_classes = (parsers.FormParser, parsers.JSONParser)
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CommanPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ExpensesTypeFilter
    

    def get_queryset(self):
        queryset = self.custom_get_queryset()
        return queryset
    
    def destroy(self, request, *args, **kwargs):  
       return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
class ExpensesViewSet(viewsets.ModelViewSet, ExpensesQueryset):
    model = Expenses
    serializer_class = ExpensesSerializer
    parser_classes = (parsers.FormParser, parsers.JSONParser)
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CommanPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ExpensesFilter
    

    def get_queryset(self):
        queryset = self.custom_get_queryset()
        return queryset
    

    @action(detail=False, methods=["post"])
    def create_expenses(self, request, *args, **kwargs):

        if request.user.user_type !="admin":
            return Response({"error": "You do not have permissions to perform this operations"}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        expst_id = data.get('expst_id')
        try:
            expense_type = ExpensesType.objects.get(id=expst_id)
        except ExpensesType.DoesNotExist:
            return Response({"error": "expense_type not found with given id"}, status=status.HTTP_404_NOT_FOUND)
        data["expense_type"] = expense_type.id
        data["pending_amount"]= data["amount"]
        serializer = ExpensesCreateSerializer(data=data)
        if serializer.is_valid():
            expense_instance = serializer.save()  
            response_serializer = ExpensesSerializer(expense_instance)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    def update(self, request, *args, **kwargs):
        if request.user.user_type !="admin":
            return Response({"error": "You do not have permissions to perform this operations"}, status=status.HTTP_404_NOT_FOUND)
        
        id = kwargs.get('pk')
        if not id:
            return Response({"error":"Expense id is missing."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            expense=Expenses.objects.get(id=id)
        except IncomeSource.DoesNotExist:
            return Response({"error":"Expense does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)
        data=request.data
        amount = data["amount"]

        if expense.spent_amount>amount:
            return Response({"error":"Expense amount should greater than  spent amount of expese."}, status=status.HTTP_400_BAD_REQUEST)
    
        data["pending_amount"]=data["amount"]- float(expense.spent_amount)
        serializer = ExpensesCreateSerializer(expense, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        expense=serializer.save()
        serializer=ExpensesSerializer(expense)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        total_amount = queryset.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        total_spent_amount = queryset.aggregate(total_spent_amount=Sum('spent_amount'))['total_spent_amount'] or 0
        total_pending_amount = queryset.aggregate(total_pending_amount=Sum('pending_amount'))['total_pending_amount'] or 0
        sd = request.query_params.get('sd', None)
        ed = request.query_params.get('ed', None)
        month = request.query_params.get('month', None)

        if not month:
            month = datetime.now().strftime('%B')
        available_amount=IncomeSource.objects.filter(month__icontains=month).aggregate(total_unutilized_amount=Sum('unutilized_amount'))['total_unutilized_amount'] or 0
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = {
                'total_expense_amount': total_amount,
                'total_spent_amount': total_spent_amount,
                'total_pending_amount': total_pending_amount,
                'available_amount': available_amount,
                'amt_diff': available_amount-total_pending_amount,
                'results': serializer.data
            }
            return self.get_paginated_response(response_data)
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            'total_amount': total_amount,
            'results': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):  
       return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

   

    

class ExpensesDetailsViewSet(viewsets.ModelViewSet, ExpensesDetailsQueryset):
    model = ExpensesDetails
    serializer_class = ExpensesDetailsSerializer
    parser_classes = (parsers.FormParser, parsers.JSONParser)
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CommanPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ExpensesDetailsFilter


    def get_queryset(self):
        queryset = self.custom_get_queryset()
        return queryset

    
    def create(self, request, *args, **kwargs):
        data = request.data
        amt = data.get('amount')
        id = data.pop('expense_id')
        try:
            expense = Expenses.objects.get(id=id)
        except Expenses.DoesNotExist:
            return Response({"error": "expense not found with given id"}, status=status.HTTP_404_NOT_FOUND)
        data["expense"]=str(expense.id)
        curr_month = request.data.get("month")

        
        if expense.pending_amount<float(amt):
            return Response({"error": f"You can not spent {float(amt) - float(expense.pending_amount)} rs extra for {curr_month} month's {expense.expense_type.expense_type} expense."}, status=status.HTTP_404_NOT_FOUND)

       
        incomes = IncomeSource.objects.filter(month=curr_month, unutilized_amount__gt=0.0).order_by("created_at")
        remain_amt = incomes.aggregate(avail_amt=Sum("unutilized_amount"))["avail_amt"]
       
        if remain_amt<=0.0:
            return Response({"error": "Currently we don't have money. We spent all money on expenses."}, status=status.HTTP_404_NOT_FOUND)
        if remain_amt<amt:
            return Response({"error": f"Currently we don't have sufficient money. We have {amt}rs only ."}, status=status.HTTP_404_NOT_FOUND)
        spend_money(expense,amt,incomes,request)

        return Response("ok", status=status.HTTP_201_CREATED)
    

    def update(self, request, *args, **kwargs):
        print("update funciton called.")
        id = kwargs.get('pk')
        if not id:
            return Response({"error":""}, status=status.HTTP_400_BAD_REQUEST)
        try:
            expense_dtl=ExpensesDetails.objects.get(id=id)
        except ExpensesDetails.DoesNotExist:
            return Response({"error":"ExpensesDetails does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)
        amount = request.data.get('amount', None)
        curr_month = request.data.get("month",None)
        income_source = IncomeSource.objects.get(id=expense_dtl.income_sorce_id)
        expense=Expenses.objects.get(id=expense_dtl.expense_id)

        print("1", expense.spent_amount)
        if amount:
            if amount<expense_dtl.amount:
                print("2", expense.spent_amount)
                amt_diff = float(expense_dtl.amount) - float(amount)
                """ update income source"""
                income_source.unutilized_amount = float(float(income_source.unutilized_amount)) + float(amt_diff)
                income_source.utilized_amount = float(income_source.utilized_amount) - float(amt_diff)

                income_source.save(update_fields=["unutilized_amount", "utilized_amount"])
                """ update expense """
                expense.spent_amount=float(expense.spent_amount) - float(amt_diff)
                expense.pending_amount = float(expense.pending_amount) + float(amt_diff)
                expense.save(update_fields=["spent_amount","pending_amount"])


                """ update expense details """
                expense_dtl.amount=float(expense_dtl.amount) - float(amt_diff)
                expense_dtl.save(update_fields=["amount"])


                

            elif float(amount)>float(expense_dtl.amount):
                print("3", expense.spent_amount)
                amt_diff =  float(amount) - float(expense_dtl.amount)
                if float(amt_diff)> float(expense.pending_amount):
                     return Response({"error": f"You can not spent {float(amount - expense.pending_amount)} rs extra for {curr_month} month's {expense.expense_type.expense_type} expense."}, status=status.HTTP_404_NOT_FOUND)
                
                """ update income source"""
                if float(amt_diff)>float(income_source.unutilized_amount) and float(income_source.unutilized_amount)>0:
                    remaining_amount = float(amt_diff) - float(float(income_source.unutilized_amount))
                    ex_untilized_amt= float(income_source.unutilized_amount)
                    income_source.unutilized_amount = float(income_source.unutilized_amount) -  float(income_source.unutilized_amount)
                    income_source.utilized_amount = float(income_source.utilized_amount) + float(ex_untilized_amt)
                    incomes = IncomeSource.objects.filter(month=curr_month, unutilized_amount__gt=0.0).order_by("created_at")
                    remain_amt = incomes.aggregate(avail_amt=Sum("unutilized_amount"))["avail_amt"]
                    if remain_amt<=0.0:
                        return Response({"error": "Currently we don't have money. We spent all money on expenses."}, status=status.HTTP_404_NOT_FOUND)
                    if remain_amt<remaining_amount:
                        return Response({"error": f"Currently we don't have sufficient money. We have {remain_amt}rs only ."}, status=status.HTTP_404_NOT_FOUND)
                    

                    if (float(expense.spent_amount) + float(ex_untilized_amt)) == float(expense.amount):
                        expense.status="done"
                    else:
                        expense.status="pending"


                    expense.spent_amount=float(expense.spent_amount) + float(ex_untilized_amt)
                    expense.pending_amount = float(expense.pending_amount )- float(ex_untilized_amt)
                    expense.save(update_fields=["spent_amount","pending_amount","status"])

                    """ update expense details """
                    expense_dtl.amount=float(expense_dtl.amount) + float(ex_untilized_amt)
                    expense_dtl.save(update_fields=["amount"])
                    income_source.save(update_fields=["unutilized_amount","utilized_amount"])
                    if remaining_amount>0.0:
                        spend_money(expense,remaining_amount, incomes, request)

                elif float(amt_diff)>float(income_source.unutilized_amount) and float(income_source.unutilized_amount)==0.0:
                    incomes = IncomeSource.objects.filter(month=curr_month, unutilized_amount__gt=0.0).order_by("created_at")
                    remain_amt = incomes.aggregate(avail_amt=Sum("unutilized_amount"))["avail_amt"]
                    spend_money(expense,amt_diff, incomes, request)
                elif float(amt_diff)<=float(income_source.unutilized_amount):               
                    
                    income_source.unutilized_amount = float(float(income_source.unutilized_amount)) - float(amt_diff)
                    income_source.utilized_amount = float(income_source.utilized_amount) + float(amt_diff)
                    income_source.save(update_fields=["unutilized_amount","utilized_amount"])

                    """ update expense details """
                    expense_dtl.amount=float(expense_dtl.amount) + float(amt_diff)
                    expense_dtl.save(update_fields=["amount"])
                    income_source.save(update_fields=["unutilized_amount","utilized_amount"])
                    

                    """ update expense  """
                    if (float(expense.spent_amount) + float(amt_diff)) == float(expense.amount):
                        expense.status="done"
                    else:
                        expense.status="pending"

                    expense.spent_amount=float(expense.spent_amount) + float(amt_diff)
                    expense.pending_amount = float(expense.pending_amount) - float(amt_diff)
                    expense.save(update_fields=["spent_amount","pending_amount","status"])


            

        serializer = ExpensesDetailsUpdateSerializer(expense_dtl, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        expense_dt=serializer.save()
        serializer=ExpensesDetailsSerializer(expense_dt)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    