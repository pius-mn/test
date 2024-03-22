from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F,Sum,Case, When, Value, DurationField


class CustomUser(AbstractUser):
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    phone= models.CharField(max_length=10, blank=False,unique=True)

    def update_current_amount(self):
        total_deposits = self.deposit_set.filter(status='complete').aggregate(sum=Sum('amount'))['sum'] or Decimal('0.0')
        total_withdrawals = self.withdrawal_set.filter(status='complete').aggregate(sum=Sum('amount'))['sum'] or Decimal('0.0')

        # Calculate total investment returns with status 'done'
        total_returns = Investment.objects.filter(user=self, status='done').aggregate(sum=Sum('product__fixed_return_amount'))['sum'] or Decimal('0.0')

        # Calculate total investments with status 'active'
        total_active_investments = Investment.objects.filter(user=self, status='active').aggregate(sum=Sum('product__amount_invested'))['sum'] or Decimal('0.0')

        # Update current amount
        self.current_amount = total_deposits - total_withdrawals + total_returns - total_active_investments
        self.save()

    def __str__(self):
        return self.username


class Referral(models.Model):
    referrer = models.ForeignKey(CustomUser, related_name='referrals', on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=20)


class Deposit(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('complete', 'Complete')], default='pending')
    transaction_code = models.CharField(unique=True, max_length=20, blank=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'complete':
            referral_earnings = Decimal(self.amount) * Decimal('0.15')
            CustomUser.objects.filter(username__in=Referral.objects.filter(referrer=self.user).values_list('referral_code', flat=True)).update(current_amount=F('current_amount') + referral_earnings)


class Withdrawal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('complete', 'Complete')], default='pending')

class Product(models.Model):
    name = models.CharField(max_length=100)
    amount_invested = models.DecimalField(max_digits=10, decimal_places=2)
    fixed_return_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name

class Investment(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_DONE = 'done'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_DONE, 'Done'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    investment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    def __str__(self):
        return f"Investment in {self.product.name} by {self.user.username} ({self.status})"

@receiver(post_save, sender=Deposit)
@receiver(post_delete, sender=Deposit)
@receiver(post_save, sender=Withdrawal)
@receiver(post_delete, sender=Withdrawal)
@receiver(post_save, sender=Investment)
@receiver(post_delete, sender=Investment)
def update_user_balance(sender, instance, **kwargs):
    instance.user.update_current_amount()
