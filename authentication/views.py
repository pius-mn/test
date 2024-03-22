from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Deposit, Referral,Withdrawal,Investment,Product,CustomUser
from .serializers import  DepositSerializer, ProfileDepositeSerializer, ProfileInvestmentSerializer, TeamSerializer, UserSerializer,WithdrawalSerializer,InvestmentSerializer,ProfileSerializer,ProfileWithdrawSerializer
from decimal import Decimal

class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
               
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        try:
            refresh = request.data.get('refresh')
            token_obj = RefreshToken(refresh)
            token_obj.blacklist()
        except Exception as e:
            pass  # Handle potential token blacklist errors (optional)
        return Response(status=status.HTTP_205_RESET_CONTENT)
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        content = {'message': f'{request.user}'}

        return Response(content)


class DepositAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        username = request.user  # Get the username of the authenticated user
        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            transaction_code = serializer.validated_data.get('transaction_code')

            try:
                # Check if the transaction code already exists for the user
                deposit = Deposit.objects.get(user__username=username, transaction_code=transaction_code)
                return Response({'error': 'Transaction code already exists'}, status=status.HTTP_400_BAD_REQUEST)
            except Deposit.DoesNotExist:
                # If the transaction code is unique, create a new deposit record
                deposit = Deposit.objects.create(user=request.user, transaction_code=transaction_code)
                deposit_serializer = DepositSerializer(deposit)
                return Response(deposit_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WithdrawalAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WithdrawalSerializer(data=request.data)
        
        if serializer.is_valid():
            withdrawal_amount = serializer.validated_data['amount']
            user = request.user
            current_amount = user.current_amount
            
            # Check if the withdrawal amount exceeds the user's current balance or is less than or equal to 0
            if withdrawal_amount > current_amount or withdrawal_amount <= 0:
                return Response({"error": "Invalid withdrawal amount"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if the withdrawal amount meets the minimum withdrawal balance requirement
            minimum_withdrawal_balance = Decimal('100.00')  # Set your minimum withdrawal balance here
            if withdrawal_amount < minimum_withdrawal_balance:
                return Response({"error": f"Withdrawal amount must be at least {minimum_withdrawal_balance}"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if the user already has a pending withdrawal
            if Withdrawal.objects.filter(user=user, status='pending').exists():
                return Response({"error": "User already has a pending withdrawal"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Save the withdrawal if all checks pass
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvestmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InvestmentSerializer(data=request.data)
      
        if serializer.is_valid():
            product_id = serializer.validated_data.get('product_id')
            user = request.user

            # Fetch the product and check if it exists
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check if user has sufficient balance
            if user.current_amount >= product.amount_invested:
                # Create the investment
                Investment.objects.create(
                    user=user,
                    product=product,
                   
                )
               
                return Response({'message': 'Investment created successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Assuming user_id is provided in the request, you can adjust this accordingly
        user_id = request.user.id
        
        try:
            profile_data = CustomUser.objects.get(id=user_id)
            withdraw_data = Withdrawal.objects.filter(user_id=user_id)
            deposite_data = Deposit.objects.filter(user_id=user_id)
            invest_data = Investment.objects.filter(user_id=user_id)
            referreral_data = Referral.objects.filter(referral_code=request.user).count()

        except (CustomUser.DoesNotExist, Withdrawal.DoesNotExist, Deposit.DoesNotExist, Investment.DoesNotExist):
            return Response({"error": "User data not found."}, status=404)
        
        profile_serializer = ProfileSerializer(profile_data)
        withdraw_serializer = ProfileWithdrawSerializer(withdraw_data, many=True)
        deposite_serializer = ProfileDepositeSerializer(deposite_data, many=True)
        investment_serializer = ProfileInvestmentSerializer(invest_data, many=True)  # Use updated serializer

        return Response({
            "profile": profile_serializer.data,
            "withdrawals": withdraw_serializer.data,
            "deposite": deposite_serializer.data,
            "investment": investment_serializer.data,
            "referral": referreral_data,
        })
class TeamAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Assuming user_id is provided in the request, you can adjust this accordingly
        user_id = request.user.username
        
        try:
            # Query the Referral objects with the provided referral_code
            referreral_data = Referral.objects.filter(referral_code=user_id)

            # Check if any referral data is found
            if not referreral_data.exists():
                return Response({"error": "User data not found."}, status=404)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

        # Initialize the serializer with many=False
        team_serializer = TeamSerializer(referreral_data, many=True)

        return Response({
            "referral": team_serializer.data,
        })