from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F,Sum
from django.utils import timezone


class CustomUser(AbstractUser):
   
    phone = models.CharField(max_length=10, blank=False, unique=True)

    @property
    def current_amount(self):
        # Calculate total deposits
        total_deposits = self.deposit_set.filter(status='complete').aggregate(sum=Sum('amount'))['sum'] or Decimal('0.0')

        # Calculate total withdrawals
        total_withdrawals = self.withdrawal_set.filter(status='complete').aggregate(sum=Sum('amount'))['sum'] or Decimal('0.0')
        bonus = Referral.objects.filter(referral_code=self.username).aggregate(sum=Sum('amount'))['sum'] or Decimal('0.0')
        # Calculate total product prices
        total_product_prices = Investment.objects.filter(user=self).aggregate(
            sum=Sum('amount_invested'))['sum'] or Decimal('0.0')
        

        # Calculate total daily earnings from active investments
        total_daily_earnings = Decimal('0.0')
        active_investments = Investment.objects.filter(user=self)
        for investment in active_investments:
            if investment.expiration_date>=timezone.now():
                duration = (timezone.now() - investment.investment_date).days
                total_daily_earnings +=  (investment.amount_invested * Decimal('0.08')) * duration
            else:
                duration = (investment.expiration_date - investment.investment_date).days
                total_daily_earnings +=  (investment.amount_invested * Decimal('0.08')) * duration               


        # Update current amount
        current_amount = total_daily_earnings+bonus+total_deposits-total_withdrawals-total_product_prices
        return current_amount

    def __str__(self):
        return self.username
 


    def __str__(self):
        return self.username


class Referral(models.Model):
    referrer = models.ForeignKey(CustomUser, related_name='referrals', on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=20)
    amount=models.DecimalField(max_digits=10, decimal_places=2,default=0.0) 

class Deposit(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('complete', 'Complete')], default='pending')
    transaction_code = models.CharField(unique=True, max_length=20, blank=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'complete':
            referral_earnings = Decimal(self.amount) * Decimal('0.1')
            Referral.objects.filter(referrer=self.user).update(amount=F('amount') + referral_earnings)
        

class Withdrawal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('complete', 'Complete')], default='pending')

class Investment(models.Model):


    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    amount_invested = models.DecimalField(max_digits=10, decimal_places=2)  
    investment_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField() 

    @property
    def status(self):
        """
        Return 'active' if the investment is still active, otherwise return 'done'.
        """
        if timezone.now() >= self.expiration_date:
            return 'done'
        else:
            return 'acive'

    def __str__(self):
        return f"Investment in {self.product_name} by {self.user.username} ({self.status})"



