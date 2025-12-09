from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.authentication.v1.views.account import AuthenticationView, ProfileView

# Authentication URLs following al-balad pattern
auth_view = AuthenticationView.as_view({
    'post': 'register'
})

signin_view = AuthenticationView.as_view({
    'post': 'signin'
})

verify_email_view = AuthenticationView.as_view({
    'post': 'verify_email'
})

forgot_password_view = AuthenticationView.as_view({
    'post': 'forgot_password'
})

otp_verification_view = AuthenticationView.as_view({
    'post': 'otp_verification'
})

reset_password_view = AuthenticationView.as_view({
    'post': 'reset_password'
})

# Profile URLs
profile_view = ProfileView.as_view({
    'get': 'profile',
    'patch': 'edit_profile'
})

change_password_view = ProfileView.as_view({
    'post': 'change_password'
})

get_2fa_qr_view = ProfileView.as_view({
    'get': 'get_2fa_qr_code'
})

setup_2fa_view = ProfileView.as_view({
    'post': 'setup_2fa'
})

disable_2fa_view = ProfileView.as_view({
    'post': 'disable_2fa'
})

urlpatterns = [
    # Authentication endpoints
    path('register/', auth_view, name='register'),
    path('login/', signin_view, name='login'),
    path('verify-email/', verify_email_view, name='verify_email'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('otp-verification/<uuid:user_id>/', otp_verification_view, name='otp_verification'),
    path('reset-password/<uuid:user_id>/', reset_password_view, name='reset_password'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile endpoints
    path('profile/', profile_view, name='profile'),
    path('change-password/', change_password_view, name='change_password'),
    path('2fa/qr-code/', get_2fa_qr_view, name='2fa_qr_code'),
    path('2fa/setup/', setup_2fa_view, name='setup_2fa'),
    path('2fa/disable/', disable_2fa_view, name='disable_2fa'),
]