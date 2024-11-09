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

from .permissions import IsInternalAdmin
from .pagination import CommanPagination

from .querysets import ExpensesDetailsQueryset, ExpensesQueryset, ExpensesTypeSourceQueryset, IncomeSourceQueryset, UserQueryset
from .filters import ExpensesDetailsFilter, ExpensesFilter, ExpensesTypeFilter, IncomeSourceFilter, UserFilter
from .utils import generate_otp_and_key, send_custom_email, spend_money
from .serializers import ExpensesCreateSerializer, ExpensesDetailsCreateSerializer, ExpensesDetailsSerializer, ExpensesSerializer, ExpensesTypeSerializer, FamilyMemberSerializer, IncomeSourceCreateSerializer, IncomeSourceSerializer, UserRoleSerializer, UserSerializer
from .models import Expenses, ExpensesType, IncomeSource, User, ExpensesDetails
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
        if not request.user.is_superuser:
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
            return Response({"error":"Income source id is missing"}, status=status.HTTP_400_BAD_REQUEST)
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
        


        available_amount=IncomeSource.objects.filter(month=month).aggregate(total_unutilized_amount=Sum('unutilized_amount'))['total_unutilized_amount'] or 0
       
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
        curr_month = datetime.now().strftime('%B')
        print("********", curr_month)
        incomes = IncomeSource.objects.all()#sfilter(month="October").order_by("created_at")
        print("********",len(incomes))
        remain_amt = incomes.aggregate(avail_amt=Sum("unutilized_amount"))["avail_amt"]
        print("********",remain_amt)
        if remain_amt<=0.0:
            return Response({"error": "Currently we don't have money. We spent all money on expenses."}, status=status.HTTP_404_NOT_FOUND)
        if remain_amt<amt:
            return Response({"error": f"Currently we don't have sufficient money. We have {amt}rs only ."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExpensesDetailsCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save() 
            spend_money(expense,amt, incomes)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)