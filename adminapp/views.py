from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import * 
from .serializer import TagSerializer
from rest_framework import viewsets

# Create your views here.

class ManageTag(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
