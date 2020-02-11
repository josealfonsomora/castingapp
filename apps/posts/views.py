import json
import uuid

from django.shortcuts import render
from django.contrib.auth.models import User
from django.core import serializers
from django.http import JsonResponse
from django.views.generic.base import View
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.parsers import FileUploadParser, MultiPartParser

from .models import Post, PostMedia


class PostResource(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        """
        Get all posts
        """
        posts = Post.objects.all()
        serialized_data = serializers.serialize('json', posts, use_natural_foreign_keys=True)
        payload = {
            "status": "success",
            "data": json.loads(serialized_data)
        }
        return JsonResponse(payload, status=200)

    def post(self, request):
        """Createe a new post"""
        payload = json.loads(request.body)
        try:
            post = Post.objects.create(user=request.user, text=payload['text'], title=payload['title'])
            response = {
                "status": "success",
                "data": {
                    "id": post.id,
                    "text": payload['text'],
                    "title": payload['title'],
                },
            }
            return JsonResponse(response, status=200)
        except Exception as e:
            response = {
                "status": "error",
                "message": "There has been an error saving the post: {}".format(e)
            }
            return JsonResponse(response, status=500)


class PostSingleResource(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, postid):
        posts = Post.objects.get(id=postid)
        serialized_data = serializers.serialize('json', [posts, ], use_natural_foreign_keys=True)
        payload = {
            "status": "success",
            "data": json.loads(serialized_data)
        }
        return JsonResponse(payload, status=200)

    def put(self, request, postid):
        try:
            payload = json.loads(request.body)
            post = Post.objects.filter(id=postid)
            post.update(**payload)
            response = {
                "status": "success",
                "data": {
                    "id": post.first().id,
                    "text": payload['text'],
                    "title": payload['title'],
                },
            }
            return JsonResponse(response, status=200)
        except Exception as e:
            response = {
                "status": "error",
                "message": "Unable to edit the post: {}".format(e)
            }
            return JsonResponse(response, status=500)

    def delete(self, request, postid):
        """
        """
        post = Post.objects.get(id=postid)
        if request.user.is_superuser:
            post.delete()
            payload = {
                "status": "success",
                "data": "Post deleted correctly"
            }
            return JsonResponse(payload)
        else:
            payload = {
                "status": "error",
                "data": "Unauthorized"
            }
            return JsonResponse(payload, status=403)


class PostMediaResource(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, postid):
        post = Post.objects.get(id=postid)
        media = post.media.all()
        serialized_data = serializers.serialize('json', media, use_natural_foreign_keys=True)

        payload = {
            "status": "success",
            "data": json.loads(serialized_data)
        }
        return JsonResponse(payload, status=200)


class PostMediaSingleResource(APIView):
    """This view is meant only for school admins and students."""
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    def post(self, request, postid, format=None):
        try:
            post = Post.objects.get(id=postid)
        except Exception as e:
            response = {
                "status": "error",
                "message": "No school or post found with that ID: {}".format(e)
            }
            return JsonResponse(response, status=500)
        try:
            post_media = PostMedia.objects.create(post=post, title=request.data['title'], datafile=request.data['file'])
            post.media.add(post_media)
            response = {
                "status": "success",
                "data": {
                    "id": post.id,
                    "title": request.data['title'],
                    "file": post_media.datafile.url
                },
            }
            return JsonResponse(response, status=200)
        except Exception as e:
            response = {
                "status": "error",
                "message": "There has been an error saving the media: {}".format(e)
            }
            return JsonResponse(response, status=500)
