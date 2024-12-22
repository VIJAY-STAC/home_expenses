from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import IncomeSourceViewSet, UserViewSet, ExpensesTypeViewSet,ExpensesViewSet, ExpensesDetailsViewSet


router = DefaultRouter()
router.register(r"users",UserViewSet,basename="users")
router.register(r"income_source",IncomeSourceViewSet,basename="income_source")
router.register(r"expense_type",ExpensesTypeViewSet,basename="expense_type")
router.register(r"expenses",ExpensesViewSet,basename="expenses")
router.register(r"expenses_details",ExpensesDetailsViewSet,basename="expenses_details")


def trigger_error(request):
    division_by_zero = 1 / 0
    
urlpatterns = [
    path('sentry-debug/', trigger_error),
    path('api/v1/',include(router.urls))
]