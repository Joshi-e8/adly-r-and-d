import traceback
import pyotp
import qrcode
import io
import base64
import secrets
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from apps.authentication.models import User, OTPToken, User2FA
from apps.authentication.v1.serializer.account import (
    UserRegistrationSerializer,
    SignInSerializer,
    OtpVerificationSerializer,
    EmailVerificationSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    Setup2FASerializer,
    ProfileSerializer,
    ChangePasswordSerializer
)


class AuthenticationView(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        serializer_mapping = {
            'register': UserRegistrationSerializer,
            'signin': SignInSerializer,
            'verify_email': EmailVerificationSerializer,
            'forgot_password': ForgotPasswordSerializer,
            'reset_password': ResetPasswordSerializer,
            'otp_verification': OtpVerificationSerializer,
        }
        return serializer_mapping.get(self.action, UserRegistrationSerializer)
    
    def register(self, request, *args, **kwargs):
        """User registration endpoint"""
        response, status_code = {}, status.HTTP_201_CREATED
        
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                otp_obj = OTPToken.objects.filter(user=user, purpose='verification', used_at__isnull=True).order_by('-created_at').first()
                response.update({
                    'result': 'success',
                    'message': _('Registration successful. Please check your email for verification.'),
                    'user_id': str(user.id),
                    **({'otp': otp_obj.token} if settings.DEBUG and otp_obj else {})
                })
            else:
                response.update({
                    'result': 'failure',
                    'errors': {key: serializer.errors[key][0] for key in serializer.errors.keys()}
                })
                status_code = status.HTTP_400_BAD_REQUEST
                
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)
    
    def signin(self, request, *args, **kwargs):
        """User sign in endpoint"""
        response, status_code = {}, status.HTTP_200_OK
        
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                
                # Check if 2FA is enabled but no token provided
                if (user.two_factor_auth and hasattr(user, 'two_factor') and 
                    user.two_factor.is_enabled and not request.data.get('otp_token')):
                    
                    response.update({
                        'result': 'success',
                        'two_factor_auth_enabled': True,
                        'message': _('2FA token required'),
                        'user_id': str(user.id)
                    })
                else:
                    # Generate tokens
                    refresh = RefreshToken.for_user(user)
                    response.update({
                        'result': 'success',
                        'message': _('Login successful'),
                        'access_token': str(refresh.access_token),
                        'refresh_token': str(refresh),
                        'user': ProfileSerializer(user).data
                    })
            else:
                response.update({
                    'result': 'failure',
                    'errors': {key: serializer.errors[key][0] for key in serializer.errors.keys()}
                })
                status_code = status.HTTP_400_BAD_REQUEST
                
        except Exception as error:
            print(error,'-----------')
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)
    
    def verify_email(self, request, *args, **kwargs):
        """Email verification endpoint"""
        response, status_code = {}, status.HTTP_200_OK
        
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                otp = serializer.validated_data['otp']
                
                user.is_verified = True
                user.save()
                otp.mark_used()
                
                response.update({
                    'result': 'success',
                    'message': _('Email verified successfully')
                })
            else:
                response.update({
                    'result': 'failure',
                    'errors': {key: serializer.errors[key][0] for key in serializer.errors.keys()}
                })
                status_code = status.HTTP_400_BAD_REQUEST
                
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)
    
    def forgot_password(self, request, *args, **kwargs):
        """Forgot password endpoint"""
        response, status_code = {}, status.HTTP_200_OK
        
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.context['user']
                
                # Generate OTP
                otp_token = secrets.randbelow(900000) + 100000
                OTPToken.objects.create(
                    user=user,
                    token=str(otp_token),
                    purpose='reset',
                    expires_at=timezone.now() + timedelta(minutes=15)
                )
                
                # TODO: Send email with OTP
                
                response.update({
                    'result': 'success',
                    'message': _('Password reset OTP sent to your email'),
                    'otp': str(otp_token),  # Remove in production
                    'user_id': str(user.id)
                })
            else:
                response.update({
                    'result': 'failure',
                    'errors': {key: serializer.errors[key][0] for key in serializer.errors.keys()}
                })
                status_code = status.HTTP_400_BAD_REQUEST
                
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)
    
    def otp_verification(self, request, *args, **kwargs):
        """OTP verification for password reset"""
        response, status_code = {}, status.HTTP_200_OK
        user_id = kwargs.get('user_id')
        
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = User.objects.get(id=user_id)
                otp_obj = OTPToken.objects.filter(
                    user=user,
                    token=serializer.validated_data['otp'],
                    purpose='reset'
                ).first()
                
                if otp_obj and otp_obj.is_valid():
                    otp_obj.mark_used()
                    response.update({
                        'result': 'success',
                        'message': _('OTP verified successfully'),
                        'reset_token': str(user.id)  # In production, use a secure token
                    })
                else:
                    response.update({
                        'result': 'failure',
                        'message': _('Invalid or expired OTP')
                    })
                    status_code = status.HTTP_400_BAD_REQUEST
            else:
                response.update({
                    'result': 'failure',
                    'errors': {key: serializer.errors[key][0] for key in serializer.errors.keys()}
                })
                status_code = status.HTTP_400_BAD_REQUEST
                
        except User.DoesNotExist:
            response.update({
                'result': 'failure',
                'message': _('Invalid user')
            })
            status_code = status.HTTP_400_BAD_REQUEST
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)
    
    def reset_password(self, request, *args, **kwargs):
        """Reset password endpoint"""
        response, status_code = {}, status.HTTP_200_OK
        user_id = kwargs.get('user_id')
        
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = User.objects.get(id=user_id)
                user.set_password(serializer.validated_data['password'])
                user.save()
                
                response.update({
                    'result': 'success',
                    'message': _('Password reset successfully')
                })
            else:
                response.update({
                    'result': 'failure',
                    'errors': {key: serializer.errors[key][0] for key in serializer.errors.keys()}
                })
                status_code = status.HTTP_400_BAD_REQUEST
                
        except User.DoesNotExist:
            response.update({
                'result': 'failure',
                'message': _('Invalid user')
            })
            status_code = status.HTTP_400_BAD_REQUEST
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)


class ProfileView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        serializer_mapping = {
            'profile': ProfileSerializer,
            'edit_profile': ProfileSerializer,
            'change_password': ChangePasswordSerializer,
            'setup_2fa': Setup2FASerializer,
        }
        return serializer_mapping.get(self.action, ProfileSerializer)
    
    def profile(self, request, *args, **kwargs):
        """Get user profile"""
        response, status_code = {}, status.HTTP_200_OK
        
        try:
            serializer = self.get_serializer(request.user)
            response.update({
                'result': 'success',
                'message': _('Profile fetched successfully'),
                'records': serializer.data
            })
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)
    
    def edit_profile(self, request, *args, **kwargs):
        """Edit user profile"""
        response, status_code = {}, status.HTTP_200_OK
        
        try:
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response.update({
                    'result': 'success',
                    'message': _('Profile updated successfully')
                })
            else:
                response.update({
                    'result': 'failure',
                    'errors': {key: serializer.errors[key][0] for key in serializer.errors.keys()}
                })
                status_code = status.HTTP_400_BAD_REQUEST
                
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)
    
    def change_password(self, request, *args, **kwargs):
        """Change user password"""
        response, status_code = {}, status.HTTP_200_OK
        
        try:
            serializer = self.get_serializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                response.update({
                    'result': 'success',
                    'message': _('Password changed successfully')
                })
            else:
                response.update({
                    'result': 'failure',
                    'errors': {key: serializer.errors[key][0] for key in serializer.errors.keys()}
                })
                status_code = status.HTTP_400_BAD_REQUEST
                
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)
    
    def get_2fa_qr_code(self, request, *args, **kwargs):
        """Get 2FA QR code"""
        response, status_code = {}, status.HTTP_200_OK
        
        try:
            user = request.user
            
            # Get or create 2FA record
            two_factor, created = User2FA.objects.get_or_create(
                user=user,
                defaults={'secret': pyotp.random_base32()}
            )
            
            # Generate QR code
            provisioning_uri = two_factor.generate_qr_code()
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            response.update({
                'result': 'success',
                'records': {
                    'qr_code': f'data:image/png;base64,{img_str}',
                    'secret': two_factor.secret,
                    'is_enabled': two_factor.is_enabled
                }
            })
            
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)
    
    def setup_2fa(self, request, *args, **kwargs):
        """Setup 2FA"""
        response, status_code = {}, status.HTTP_200_OK
        
        try:
            serializer = self.get_serializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                two_factor = serializer.save()
                response.update({
                    'result': 'success',
                    'message': _('2FA enabled successfully'),
                    'backup_codes': two_factor.backup_codes
                })
            else:
                response.update({
                    'result': 'failure',
                    'errors': {key: serializer.errors[key][0] for key in serializer.errors.keys()}
                })
                status_code = status.HTTP_400_BAD_REQUEST
                
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)
    
    def disable_2fa(self, request, *args, **kwargs):
        """Disable 2FA"""
        response, status_code = {}, status.HTTP_200_OK
        
        try:
            user = request.user
            if hasattr(user, 'two_factor'):
                user.two_factor.is_enabled = False
                user.two_factor.save()
                user.two_factor_auth = False
                user.save()
                
                response.update({
                    'result': 'success',
                    'message': _('2FA disabled successfully')
                })
            else:
                response.update({
                    'result': 'failure',
                    'message': _('2FA not enabled')
                })
                status_code = status.HTTP_400_BAD_REQUEST
                
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)
