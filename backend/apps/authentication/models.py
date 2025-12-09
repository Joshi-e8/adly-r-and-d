import uuid
import pyotp
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    two_factor_auth = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.email


class OTPToken(models.Model):
    PURPOSE_CHOICES = [
        ('verification', 'Email Verification'),
        ('login', 'Login'),
        ('reset', 'Password Reset'),
        ('two_factor', 'Two Factor Authentication'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_tokens')
    token = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'otp_tokens'
    
    def is_valid(self):
        return not self.used_at and timezone.now() < self.expires_at
    
    def mark_used(self):
        self.used_at = timezone.now()
        self.save()


class User2FA(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='two_factor')
    secret = models.CharField(max_length=255)
    is_enabled = models.BooleanField(default=False)
    backup_codes = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_2fa'
    
    def generate_qr_code(self):
        """Generate QR code for 2FA setup"""
        totp = pyotp.TOTP(self.secret)
        provisioning_uri = totp.provisioning_uri(
            name=self.user.email,
            issuer_name="ADLY Platform"
        )
        return provisioning_uri
    
    def verify_token(self, token):
        """Verify TOTP token"""
        totp = pyotp.TOTP(self.secret)
        return totp.verify(token, valid_window=1)