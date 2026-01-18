from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login  # Django authentication functions
from rest_framework.authtoken.models import Token  # Token authentication
from accounts.models import User  # Custom User model
from django.core.exceptions import ValidationError
from .serializers import UserSerializer  # Serializer for user data
from django.core.validators import validate_email  # Email validation
from accounts.utility import generate_username
import logging  # For error logging

# Get logger instance for this module
logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    data = {
        'firstname': request.data.get('firstname'),
        'lastname': request.data.get('lastname'),
        'email': request.data.get('email'),
        'password': request.data.get('password'),
        'password2': request.data.get('password2'),
    }

    if data['password'] != data['password2']:
        return Response({'error': 'Passwords do not match'}, status=400)

    if User.objects.filter(email=data['email']).exists():
        return Response({'error': 'Email already exists'}, status=400)

    serializer = UserSerializer(data=data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    user = serializer.save()
    user.username = generate_username(data['email'])
    user.set_password(data['password'])
    user.is_active = True
    user.save()

    token = Token.objects.create(user=user)

    return Response({
        'token': token.key,
        'user': serializer.data
    }, status=201)

@api_view(['POST'])
@permission_classes([AllowAny])
def signin(request):
    """
    User login endpoint
    Authenticates user and returns authentication token
    """
    # Extract credentials from request
    username = request.data.get("username")  # Can be username or email
    password = request.data.get("password")  # Plain text password
    
    # STEP 1: Validate required fields
    if not username or not password:
        return Response(
            {"error": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        try:
            user_obj = User.objects.get(username=username)
            username = user_obj.username
        except User.DoesNotExist:
            pass

        # STEP 2: Authenticate user using Django's authenticate
        user = authenticate(request, username=username, password=password)
        
        # STEP 3: Check if authentication failed
        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # STEP 4: Check account status (if custom User model has this field)
        if hasattr(user, 'account_status'):
            if user.account_status == "Inactive":
                return Response(
                    {'error': "Your account has not been activated"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif user.account_status == "Suspended":
                return Response(
                    {'error': "Your account has been blocked or suspended"},
                    status=status.HTTP_403_FORBIDDEN
                )
            elif user.account_status == "Unverified":
                return Response(
                    {"error": "Your account is not verified"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
        # STEP 5: Check if user account is active in Django
        if not user.is_active:
            return Response(
                {'error': "There is a problem with your account. Please contact us for details"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # STEP 6: Log the user in (sets session data)
        login(request, user)
        
        # STEP 7: Get or create authentication token
        token, created = Token.objects.get_or_create(user=user)
        
        # STEP 8: Return success response with token and user info
        user_data = UserSerializer(user)
        
        return Response({
            "token": token.key,
            "user": user_data.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Login error for {username}: {str(e)}")
        return Response(
            {'error': 'An error occurred during login'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])  # Only accept GET requests
@permission_classes([IsAuthenticated])  # Requires authentication
def profile(request):
    """
    Get user profile information
    Returns basic profile data for authenticated users
    """
    # Get the authenticated user from request
    user = request.user
    
    # Return user profile data
    return Response({
        'id': user.id,  # User ID
        'email': user.email,  # Email address
        'name': f"{user.first_name} {user.last_name}".strip()  # Full name
        # .strip() removes extra whitespace if names are empty
    })