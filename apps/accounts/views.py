import json
import uuid

from django.contrib.auth.models import User
from django.core import serializers
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import check_password

from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from twilio.rest import Client

from .models import UserProfile, RegistryCode, UserType
from ..utils.generators import passwordgenerator, codegenerator


class CurrentUserProfile(APIView):
    # Require the user to be authenticated
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        """Get the current user profile.

        This endpoints add a marker in case the user is administrator.
        """
        profile = request.user.profile
        serialized_data = serializers.serialize('json', [profile, ], use_natural_foreign_keys=True)
        payload = {
            "status": "success",
            "data": json.loads(serialized_data)
        }
        payload['data'][0]['fields']['is_admin'] = request.user.is_superuser
        return JsonResponse(payload, status=200, safe=False)

    def post(self, request, format=None):
        """Change the profile of a user."""
        # Terrible hack to be able to update with a dict and avoid 100 sloc
        profile_obj = request.user.profile
        profile = UserProfile.objects.filter(id=profile_obj.id)
        if profile:
            allowed_fields = ['name', 'surname', 'dob', 'email', 'phone']
            payload = json.loads(request.body)
            for field in list(payload.keys()):
                if field in allowed_fields:
                    try:
                        profile.update(**payload)
                    except Exception as e:
                        payload = {
                            "status": "error",
                            "message": "Error updating {}: {}".format(field, e)
                        }
                        return JsonResponse(payload, status=500, safe=False)
                else:
                    payload = {
                        "status": "error",
                        "message": "Field {} does not exist.".format(field)
                    }
                    return JsonResponse(payload, status=400, safe=False)
            payload = {
                "status": "success",
                "data": payload
            }
            return JsonResponse(payload, status=200, safe=False)
        else:
            payload = {
                "status": "critical",
                "message": "User does not have a profile."
            }
            return JsonResponse(payload, status=500, safe=False)

class CreateUser(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        payload = json.loads(request.body)
        try:
            new_username = new_password = passwordgenerator()
            phone = payload.get('phone', '')
            # Check phone/code
            registry_code = RegistryCode.objects.get(phone=phone)
            if payload.get('code', '') == registry_code.code:
                user = User.objects.create_user(new_username, payload.get('email', ''), new_password)
                # Get user type
                usertype = UserType.objects.get(name=payload.get('user_type', ''))
                profile = UserProfile(user=user,
                                      name=payload.get('name', ''),
                                      surname=payload.get('surname', ''),
                                      dob=payload.get('dob', ''),
                                      phone=phone,
                                      email=payload.get('email', ''),
                                      user_type=usertype
                                     )
                profile.save()
                refresh = RefreshToken.for_user(profile.user)
                response = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                return JsonResponse(response, status=200, safe=False)
            else:
                payload = {
                    "status": "error",
                    "message": "Registration code invalid"
                }
                return JsonResponse(payload, status=400, safe=False)
        except Exception as e:
            payload = {
                "status": "error",
                "message": "There has been an error while creating the user: {}".format(e)
            }
            return JsonResponse(payload, status=500, safe=False)


class LoginResource(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        payload = json.loads(request.body)
        try:
            profile = UserProfile.objects.get(phone=payload.get('phone', ''))
            code = codegenerator()
            profile.authentication_code = code
            profile.save()
            twilio_client = Client(settings.TWILIO_ACCOUNTID, settings.TWILIO_AUTH_TOKEN)
            message = twilio_client.messages.create(
                    body="Your code is: {}".format(code),
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to='{}'.format(phone)
            )
            payload = {
                "status": "success"
            }
            return JsonResponse(payload, status=200, safe=False)
        except Exception as e:
            payload = {
                "status": "error",
                "message": "Unable to obtain the user: {}".format(e)
            }
            return JsonResponse(payload, status=500, safe=False)


class ValidateCodeAndLogin(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        payload = json.loads(request.body)
        try:
            profile = UserProfile.objects.get(phone=payload.get('phone', ''))
            code = payload.get('validation_code', 'INVALID')
            if code == profile.authentication_code:
                profile.validated = True
                profile.authentication_code = ''
                profile.save()
                refresh = RefreshToken.for_user(profile.user)
                response = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                return JsonResponse(response, status=200, safe=False)
            else:
                payload = {
                    "status": "error",
                    "message": "Invalid authentication code"
                }
                return JsonResponse(payload, status=403, safe=False)

        except Exception as e:
            payload = {
                "status": "error",
                "message": "Unable to obtain the user: {}".format(e)
            }
            return JsonResponse(payload, status=500, safe=False)


class RegisterPhone(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request):
        payload = json.loads(request.body)
        try:
            phone = payload.get('phone', '')
            if phone:
                code = codegenerator()
                registration = RegistryCode.objects.create(phone=phone, code=code)
                twilio_client = Client(settings.TWILIO_ACCOUNTID, settings.TWILIO_AUTH_TOKEN)
                message = twilio_client.messages.create(
                        body="Your code is: {}".format(code),
                        from_=settings.TWILIO_PHONE_NUMBER,
                        to='{}'.format(phone)
                )
                payload = {
                    "status": "success"
                }
                return JsonResponse(payload, status=200, safe=False)
            else:
                payload = {
                    "status": "error",
                    "message": "Invalid phone number"
                }
                return JsonResponse(payload, status=400, safe=False)
        except Exception as e:
            payload = {
                "status": "error",
                "message": "Unable to create registration: {}".format(e)
            }
            return JsonResponse(payload, status=500, safe=False)
