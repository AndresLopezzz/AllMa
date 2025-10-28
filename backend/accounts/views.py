from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UserProfileSerializer
from .models import User

class RegisterView(APIView):
    """
    Registro de usuarios - Ahora devuelve JWT tokens (access y refresh)
    además del token simple para compatibilidad con código antiguo
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generar token simple (compatibilidad)
            token, created = Token.objects.get_or_create(user=user)

            # Generar JWT tokens (nuevo sistema)
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "User created successfully",
                # Token simple (antiguo - para compatibilidad)
                "token": token.key,
                # JWT tokens (nuevo - usa estos)
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role,
                    "plan": user.plan,
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(ObtainAuthToken):
    """
    Login con JWT - Devuelve access token (1h) y refresh token (7 días)
    También devuelve token simple para compatibilidad
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generar token simple (compatibilidad)
        token, created = Token.objects.get_or_create(user=user)

        # Generar JWT tokens (nuevo sistema)
        refresh = RefreshToken.for_user(user)

        return Response({
            # Token simple (antiguo - para compatibilidad)
            "token": token.key,
            # JWT tokens (nuevo - usa estos)
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "plan": user.plan,
                "is_active": user.is_active,
            }
        })

class ProfileView(APIView):
    """
    Perfil de usuario - Requiere autenticación JWT o Token
    GET: Obtener datos del usuario actual
    PUT: Actualizar datos del usuario actual
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
