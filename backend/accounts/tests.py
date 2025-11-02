from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User


class UserRegistrationTests(APITestCase):
    """
    Tests para el registro de usuarios.
    """

    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()
        self.register_url = reverse('register')
        self.valid_user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'name': 'Test User',
            'role': 'empleado',
            'plan': 'free'
        }

    def test_user_registration_success(self):
        """
        Test: Registro exitoso de un nuevo usuario
        """
        response = self.client.post(
            self.register_url,
            self.valid_user_data,
            format='json'
        )

        # Verificar status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar que se creó el usuario en la base de datos
        self.assertTrue(User.objects.filter(email='test@example.com').exists())

        # Verificar que la respuesta contiene los datos esperados
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        self.assertEqual(response.data['user']['name'], 'Test User')

        # Verificar que devuelve tokens
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_registration_duplicate_email(self):
        """
        Test: No se puede registrar un usuario con email duplicado
        """
        # Crear primer usuario
        User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='First User'
        )

        # Intentar crear usuario con mismo email
        response = self.client.post(
            self.register_url,
            self.valid_user_data,
            format='json'
        )

        # Verificar que falla
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_missing_fields(self):
        """
        Test: Registro falla si faltan campos requeridos
        """
        invalid_data = {
            'email': 'test@example.com'
            # Falta password y name
        }

        response = self.client.post(
            self.register_url,
            invalid_data,
            format='json'
        )

        # Verificar que falla
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_invalid_email(self):
        """
        Test: Registro falla con email inválido
        """
        invalid_data = {
            'email': 'not-an-email',
            'password': 'testpass123',
            'password2': 'testpass123',
            'name': 'Test User',
            'role': 'empleado',
            'plan': 'free'
        }

        response = self.client.post(
            self.register_url,
            invalid_data,
            format='json'
        )

        # Verificar que falla
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTests(APITestCase):
    """
    Tests para el login de usuarios.
    """

    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()
        self.login_url = reverse('login')

        # Crear un usuario de prueba
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User',
            plan='free'
        )

    def test_user_login_success(self):
        """
        Test: Login exitoso con credenciales correctas
        """
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        response = self.client.post(
            self.login_url,
            login_data,
            format='json'
        )

        # Verificar status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que devuelve tokens
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('token', response.data)  # Token antiguo para compatibilidad

        # Verificar que devuelve datos del usuario
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')

    def test_user_login_invalid_credentials(self):
        """
        Test: Login falla con contraseña incorrecta
        """
        login_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }

        response = self.client.post(
            self.login_url,
            login_data,
            format='json'
        )

        # Verificar que falla
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_login_nonexistent_user(self):
        """
        Test: Login falla con usuario que no existe
        """
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }

        response = self.client.post(
            self.login_url,
            login_data,
            format='json'
        )

        # Verificar que falla
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_login_missing_credentials(self):
        """
        Test: Login falla si faltan credenciales
        """
        login_data = {
            'email': 'test@example.com'
            # Falta password
        }

        response = self.client.post(
            self.login_url,
            login_data,
            format='json'
        )

        # Verificar que falla
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileTests(APITestCase):
    """
    Tests para el endpoint de perfil de usuario.
    """

    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()
        self.profile_url = reverse('profile')

        # Crear un usuario de prueba
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User',
            plan='free'
        )

    def test_profile_requires_authentication(self):
        """
        Test: Endpoint de perfil requiere autenticación
        """
        response = self.client.get(self.profile_url)

        # Sin token, debe retornar 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_with_valid_token(self):
        """
        Test: Perfil se obtiene correctamente con token válido
        """
        # Autenticar al usuario (forzar autenticación en tests)
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.profile_url)

        # Verificar status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que devuelve los datos del usuario
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['name'], 'Test User')
        self.assertEqual(response.data['plan'], 'free')

    def test_profile_update(self):
        """
        Test: Usuario puede actualizar su perfil
        """
        # Autenticar al usuario
        self.client.force_authenticate(user=self.user)

        update_data = {
            'name': 'Updated Name'
        }

        # La vista usa PUT, no PATCH
        response = self.client.put(
            self.profile_url,
            update_data,
            format='json'
        )

        # Verificar status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que se actualizó en la base de datos
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'Updated Name')


class UserModelTests(TestCase):
    """
    Tests para el modelo User.
    """

    def test_create_user(self):
        """
        Test: Crear un usuario básico
        """
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )

        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.name, 'Test User')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.check_password('testpass123'))

    def test_create_superuser(self):
        """
        Test: Crear un superusuario
        """
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            name='Admin User'
        )

        self.assertEqual(admin.email, 'admin@example.com')
        self.assertTrue(admin.is_active)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_user_str_method(self):
        """
        Test: Método __str__ del modelo User
        """
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )

        self.assertEqual(str(user), 'test@example.com')

    def test_email_normalization(self):
        """
        Test: Email se normaliza (lowercase en dominio)
        """
        user = User.objects.create_user(
            email='test@EXAMPLE.COM',
            password='testpass123',
            name='Test User'
        )

        # Django normaliza el email automáticamente
        self.assertEqual(user.email, 'test@example.com')
