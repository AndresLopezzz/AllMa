from django.urls import path
from .views import RegisterView, LoginView, ProfileView, UsageView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Autenticación tradicional (devuelve JWT + Token simple)
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),

    # JWT endpoints puros (solo JWT, sin token simple)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Perfil de usuario (requiere autenticación)
    path('profile/', ProfileView.as_view(), name='profile'),

    # Uso del plan (requiere autenticación)
    path('user/usage/', UsageView.as_view(), name='usage'),
]
