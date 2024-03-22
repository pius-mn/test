from rest_framework import serializers
from .models import Referral, Deposit, Withdrawal,CustomUser,Investment

class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = ('referrer', 'referral_code')
class UserSerializer(serializers.ModelSerializer):
    referral_code = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'phone', 'password', 'referral_code')
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': True},
            'phone': {'required': True}
        }

    def validate_phone(self, value):
        """
        Validate that the phone number has exactly 10 digits.
        """
        if len(value) != 10 or not value.isdigit():
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return value

    def create(self, validated_data):
        referral_code = validated_data.pop('referral_code', None)


        user = CustomUser.objects.create_user(**validated_data)

        # Only create referral if referral code exists
        if referral_code and CustomUser.objects.filter(username=referral_code).exists():
            Referral.objects.create(referral_code=referral_code, referrer=user)


        return user

class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = ['transaction_code']

class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ['amount']

class InvestmentSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username','phone','current_amount')
class ProfileWithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ('amount','status')
class ProfileDepositeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = ('amount','status')
class ProfileInvestmentSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = Investment
        fields = ['id', 'product', 'product_name', 'investment_date', 'status']

    def get_product_name(self, obj):
        return obj.product.name
class TeamSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser  # Assuming referrer is a ForeignKey in Referral pointing to CustomUser
        fields = ['username']

    def get_username(self, obj):
        return obj.referrer.username
