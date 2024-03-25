from django.contrib import admin
from .models import Deposit, Withdrawal,CustomUser,Investment,Referral
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'current_amount')

admin.site.register(CustomUser, CustomUserAdmin)

class DepositAdmin(admin.ModelAdmin):
    list_display = ('user','user_email', 'amount', 'status', 'transaction_code')
    search_fields = ['user__email', 'transaction_code__contains']

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'User Email'

admin.site.register(Deposit, DepositAdmin)

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status')
    list_filter = ('status',)
    search_fields = ('user__username',)

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display=('user', 'amount_invested', 'status')
@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display=('referral_code',  'referrer','amount')
