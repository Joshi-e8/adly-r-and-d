import pyotp
import secrets
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from apps.authentication.models import User, OTPToken, User2FA


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['email'],
            **validated_data
        )
        
        # Generate email verification OTP
        otp_token = secrets.randbelow(900000) + 100000  # 6-digit OTP
        OTPToken.objects.create(
            user=user,
            token=str(otp_token),
            purpose='verification',
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        
        return user


class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    otp_token = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        otp_token = attrs.get('otp_token')
        
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        
        if not user.is_verified:
            raise serializers.ValidationError('Email not verified')
        
        # Check 2FA if enabled
        if user.two_factor_auth and hasattr(user, 'two_factor') and user.two_factor.is_enabled:
            if not otp_token:
                raise serializers.ValidationError('2FA token required')
            
            if not user.two_factor.verify_token(otp_token):
                raise serializers.ValidationError('Invalid 2FA token')
        
        attrs['user'] = user
        return attrs


class OtpVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    
    def validate_otp(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError('OTP must be 6 digits')
        return value


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField(max_length=6)
    
    def validate(self, attrs):
        email = attrs.get('email')
        token = attrs.get('token')
        
        try:
            user = User.objects.get(email=email)
            otp = OTPToken.objects.get(
                user=user,
                token=token,
                purpose='verification'
            )
            
            if not otp.is_valid():
                raise serializers.ValidationError('Token expired or already used')
            
            attrs['user'] = user
            attrs['otp'] = otp
            return attrs
            
        except (User.DoesNotExist, OTPToken.DoesNotExist):
            raise serializers.ValidationError('Invalid token')


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            self.context['user'] = user
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError('User with this email does not exist')


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(validators=[validate_password])
    password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs


class Setup2FASerializer(serializers.Serializer):
    token = serializers.CharField(max_length=6)
    
    def validate_token(self, value):
        user = self.context['request'].user
        
        # Get or create 2FA record
        two_factor, created = User2FA.objects.get_or_create(
            user=user,
            defaults={'secret': pyotp.random_base32()}
        )
        
        if not two_factor.verify_token(value):
            raise serializers.ValidationError('Invalid token')
        
        return value
    
    def save(self):
        user = self.context['request'].user
        two_factor = user.two_factor
        two_factor.is_enabled = True
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4) for _ in range(10)]
        two_factor.backup_codes = backup_codes
        two_factor.save()
        
        # Enable 2FA on user
        user.two_factor_auth = True
        user.save()
        
        return two_factor


class ProfileSerializer(serializers.ModelSerializer):
    has_2fa = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_verified', 'has_2fa', 'created_at']
        read_only_fields = ['id', 'email', 'is_verified', 'created_at']
    
    def get_has_2fa(self, obj):
        return obj.two_factor_auth and hasattr(obj, 'two_factor') and obj.two_factor.is_enabled


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect')
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user