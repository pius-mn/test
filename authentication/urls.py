from django.urls import path
from .views import ProtectedView, RegisterView, LogoutView,DepositAPIView, TeamAPIView,WithdrawalAPIView,InvestmentAPIView,ProfileAPIView
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    # Authentication endpoints
    path('login/',jwt_views.TokenObtainPairView.as_view(), name ='token_obtain_pair'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh-token/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('deposite/', DepositAPIView.as_view(), name='deposite'),
    path('withdraw/', WithdrawalAPIView.as_view(), name="withdraw"),
    path('invest/',InvestmentAPIView.as_view(), name='invest'),
    path('profile/',ProfileAPIView.as_view(),name='profile'),
    path('team/',TeamAPIView.as_view(),name='team'),

    # Protected endpoint
    path('home/', ProtectedView.as_view(), name='protected-view'),
]
