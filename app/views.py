from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from .serialziers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class Signup(APIView):
    def post(self, request):
        try:
            # Extract data from the request
            email = request.data.get('email')
            password = request.data.get('password')

            # Basic validation
            if not email or not password:
                return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user already exists
            if User.objects.filter(email=email).exists():
                return Response({"error": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

            # Create a new user
            user = User.objects.create(
                username=email,
                email=email,
                password=make_password(password)  # Hash the password before saving it
            )

            # Return a success response
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Log the exception
            print(f"An error occurred: {e}")

            # Return a generic error response
            return Response({"error": "An error occurred while creating the user"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Login(APIView):
    def post(self, request):
        try:
            # Extract data from the request
            email = request.data.get('email')
            password = request.data.get('password')

            # Basic validation
            if not email or not password:
                return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user exists
            user = authenticate(username=email, password=password)

            if user is None:
                return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)
            
            refresh = RefreshToken.for_user(user)
            print(str(refresh))

            # Successful authentication
            return Response({"message": "Login successful",
                             "access":str(refresh.access_token),
                             "refresh":str(refresh)}, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the exception
            print(f"An error occurred: {e}")

            # Return a generic error response
            return Response({"error": "An error occurred while logging in"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UsersDetails(APIView):
    def get(self,request):
        users = User.objects.filter(is_superuser=False)
        serializer = UserSerializer(users,many=True)
        return Response({'data':serializer.data},status=status.HTTP_200_OK)
    

class UserDetails(APIView):
    def get(self,request):
        user = request.user
        user = User.objects.get(username=user)
        print(user)
        serializer = UserSerializer(user)
        print(serializer.data)
        return Response({'data':serializer.data},status=status.HTTP_200_OK)
    

class token_refresh(APIView):
   def post(self, request):
       refresh_token = request.data.get('refresh')
       if not refresh_token:
           return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
       
       try:
           refresh = RefreshToken(refresh_token)
           new_access_token = str(refresh.access_token)
           new_refresh_token = str(refresh)

           # Return the new tokens
           return Response({
               'access': new_access_token,
               'refresh': new_refresh_token,
           }, status=status.HTTP_200_OK)
       except Exception as e:
           print(e)
           return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
