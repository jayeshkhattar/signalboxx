# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/users/views.py
# Compiled at: 2026-05-09 22:01:59
# Size of source mod 2**32: 3858 bytes
import logging
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import RegisterSerializer, UserSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
logger = logging.getLogger("users")

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        logger.debug("Registration attempt | email=%s", request.data.get("email", "—"))
        response = (super().create)(request, *args, **kwargs)
        logger.info("New user registered | email=%s status=%s", request.data.get("email"), response.status_code)
        return response


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        logger.debug("Profile fetched | user_id=%s email=%s", user.id, user.email)
        return user

    def update(self, request, *args, **kwargs):
        mode = request.data.get("preferred_mode")
        if mode:
            logger.info("Mode updated | user_id=%s preferred_mode=%s", request.user.id, mode)
        return (super().update)(request, *args, **kwargs)


class ForgotPasswordView(APIView):
    permission_classes = [
     permissions.AllowAny]

    def post(self, request):
        ser = ForgotPasswordSerializer(data=(request.data))
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f"{settings.FRONTEND_URL}/?uid={uid}&token={token}#reset"
            send_mail(subject="Reset your SignalBoxx password",
              message=f"Hi {user.username},\n\nClick the link below to reset your password:\n\n{reset_url}\n\nThis link expires in 24 hours. If you didn't request this, ignore this email.\n\n— SignalBoxx",
              from_email=(settings.DEFAULT_FROM_EMAIL),
              recipient_list=[
             email],
              fail_silently=True)
            logger.info("Password reset email sent | user_id=%s", user.id)
        except User.DoesNotExist:
            logger.debug("Password reset requested for unknown email | email=%s", email)

        return Response({"detail": "If that email exists, a reset link has been sent."})


class ResetPasswordView(APIView):
    permission_classes = [
     permissions.AllowAny]

    def post(self, request):
        ser = ResetPasswordSerializer(data=(request.data))
        ser.is_valid(raise_exception=True)
        try:
            uid = force_str(urlsafe_base64_decode(ser.validated_data["uid"]))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Invalid or expired link."}, status=(status.HTTP_400_BAD_REQUEST))
        else:
            if not default_token_generator.check_token(user, ser.validated_data["token"]):
                return Response({"error": "Invalid or expired link."}, status=(status.HTTP_400_BAD_REQUEST))
            user.set_password(ser.validated_data["new_password"])
            user.save()
            logger.info("Password reset successful | user_id=%s", user.id)
            return Response({"detail": "Password updated. You can now sign in."})

# okay decompiling ./users/__pycache__/views.cpython-37.pyc


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from .serializers import ChangePasswordSerializer
        ser = ChangePasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(ser.validated_data['old_password']):
            logger.warning('Change password: wrong current password | user_id=%s', user.id)
            return Response({'error': 'Current password is incorrect.'},
                            status=status.HTTP_400_BAD_REQUEST)
        user.set_password(ser.validated_data['new_password'])
        user.save()
        logger.info('Password changed | user_id=%s', user.id)
        return Response({'detail': 'Password updated successfully.'})
