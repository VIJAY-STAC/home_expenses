from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import BulkBuyerResvStock, BusinessTermsTable, Expenses, ExpensesDetails, ExpensesType, User, IncomeSource

class UserAdmin(BaseUserAdmin):
    # Define what fields to display in the admin list view
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'user_type', 'is_active', 'is_staff')
    
    # Define fields to be used in the detail/edit view
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'date_of_birth', 'phone_number', 'address', 'pincode', 'latitude', 'longitude', 'gender')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('OTP Info', {'fields': ('otp', 'otp2')}),
        ('User Type', {'fields': ('user_type',)}),
    )
    
    # Customize how the user is created in the admin form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'user_type'),
        }),
    )
    
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

# Register the customized UserAdmin
admin.site.register(User, UserAdmin)



class IncomeSourceAdmin(admin.ModelAdmin):
    list_display = ("created_at","user","date", "month","year","amount", "income_source","amount","unutilized_amount","utilized_amount")
admin.site.register(IncomeSource, IncomeSourceAdmin)




class ExpensesAdmin(admin.ModelAdmin):
    list_display = ("expense_type","date","year", "month","amount","spent_amount","pending_amount","status")
admin.site.register(Expenses, ExpensesAdmin)

class ExpensesTypesAdmin(admin.ModelAdmin):
    list_display = ("id","expense_type","amount","discription","priority")
admin.site.register(ExpensesType, ExpensesTypesAdmin)


class ExpensesDetailsAdmin(admin.ModelAdmin):
    list_display = ("created_at","expense","income_sorce","date", "month","year","user","amount","notes")
admin.site.register(ExpensesDetails, ExpensesDetailsAdmin)




class BusinessTermsTableAdmin(admin.ModelAdmin):
    list_display = ("id","created_at","term_name","term_value")
admin.site.register(BusinessTermsTable, BusinessTermsTableAdmin)


class BulkBuyerResvStockAdmin(admin.ModelAdmin):
    list_display = ("id","created_at","modified_at","last_synced_at","notes")
admin.site.register(BulkBuyerResvStock, BulkBuyerResvStockAdmin)