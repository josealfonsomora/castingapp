import json

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

from .serializers import CustomTokenObtainPairSerializer
from .models import UserProfile
from ..utils.pwdgenerator import randomStringDigits


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


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
            allowed_fields = ['name', 'surname', 'language', 'dob', 'address',
                              'email', 'parent_email', 'parent_phone', 'phone']
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


class UserRecoverPassword(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        """Request a neew password for a user."""
        payload = json.loads(request.body)
        try:
            user = User.objects.get(email=payload)
            school = School.objects.filter(Q(students=request.user)|Q(admins=request.user)).first()
            new_password = randomStringDigits(8)
            user.set_password(new_password)
            user.save()
            send_mail(
                    'Your new TYM password',
                    'Hello {}, you have requested a new password for TYM, here it comes! {}'.format(user.profile.name, new_password),
                    settings.EMAIL_SEND_FROM,
                    user.profile.email,
                    fail_silently=False,
                )
            payload = {
                "status": "success"
            }
            return JsonResponse(payload, status=200, safe=False)
        except:
            return JsonResponse({'status': 'error', 'message': 'Error obtaining the user'}, status=500)


class UserDeactivate(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, userid, format=None):
        try:
            selected_user = User.objects.get(id=userid)
            # Check that the user has a school
            school = selected_user.school_students.all()
            if school:
                # Check im an admin for that school
                if request.user in school[0].admins.all() or request.user.is_superuser:
                    selected_user.is_active = False
                    selected_user.save()
                    payload = {
                        "status": "success",
                        "message": "User deactivated"
                    }
                    return JsonResponse(payload, status=200, safe=False)
                else:
                    payload = {
                        "status": "error",
                        "message": "You don't have access to this resource"
                    }
                    return JsonResponse(payload, status=403, safe=False)
            else:
                payload = {
                    "status": "error",
                    "message": "No school found for that user"
                }
                return JsonResponse(payload, status=403, safe=False)
        except Exception as e:
            payload = {
                "status": "error",
                "message": "An error has ocurred: {}".format(e)
            }
            return JsonResponse(payload, status=500, safe=False)


class UserChangePassword(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        """Change the password of a user."""
        payload = json.loads(request.body)
        try:
            user = request.user
            current_password = request.user.password
            old_password = payload['old_password']
            new_password = payload['password']
            password_valid = check_password(old_password, current_password)
            if password_valid:
                user.set_password(new_password)
                user.save()
                send_mail(
                        'Your TYM password has changed',
                        'Hello {}, you or someone else has changed your password for TYM.',
                        settings.EMAIL_SEND_FROM,
                        user.profile.email,
                        fail_silently=False,
                    )
                payload = {
                    "status": "success"
                }
                return JsonResponse(payload, status=200, safe=False)
            else:
                payload = {
                    "status": "failed",
                    "message": "Current password is invalid."
                }
                return JsonResponse(payload, status=400, safe=False)
        except:
            return JsonResponse({'status': 'error', 'message': 'Error obtaining the user'}, status=500)
