from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User
from inventory.models import BusinessTemplate, Inventory, Product
from decimal import Decimal


class ProductCreateTests(APITestCase):
    """
    Tests para la creación de productos.
    """

    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()

        # Crear usuario de prueba
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User',
            plan='free'
        )

        # Crear otro usuario para tests de permisos
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            name='Other User',
            plan='free'
        )

        # Crear una plantilla de negocio
        self.template = BusinessTemplate.objects.create(
            name='Ferretería',
            description='Plantilla para ferreterías',
            custom_fields={
                'marca': {'type': 'text', 'required': True},
                'material': {'type': 'text', 'required': False}
            },
            created_by=self.user,
            is_active=True
        )

        # Crear inventario del usuario
        self.inventory = Inventory.objects.create(
            name='Mi Ferretería',
            owner=self.user,
            template=self.template
        )

        # Crear inventario del otro usuario
        self.other_inventory = Inventory.objects.create(
            name='Otra Ferretería',
            owner=self.other_user,
            template=self.template
        )

        self.products_url = reverse('product-list')

    def test_create_product_success(self):
        """
        Test: Crear un producto exitosamente
        """
        # Autenticar usuario
        self.client.force_authenticate(user=self.user)

        product_data = {
            'name': 'Martillo',
            'sku': 'MART-001',
            'description': 'Martillo de acero',
            'quantity': 50,
            'price': '25.99',
            'category': 'Herramientas',
            'inventory': self.inventory.id,
            'custom_data': {
                'marca': 'Stanley'
            }
        }

        response = self.client.post(
            self.products_url,
            product_data,
            format='json'
        )

        # Verificar status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar que se creó en la base de datos
        self.assertTrue(Product.objects.filter(sku='MART-001').exists())

        # Verificar datos en la respuesta
        self.assertEqual(response.data['name'], 'Martillo')
        self.assertEqual(response.data['sku'], 'MART-001')
        self.assertEqual(Decimal(response.data['price']), Decimal('25.99'))

    def test_create_product_requires_authentication(self):
        """
        Test: Crear producto requiere autenticación
        """
        product_data = {
            'name': 'Martillo',
            'sku': 'MART-001',
            'quantity': 50,
            'price': '25.99',
            'inventory': self.inventory.id
        }

        response = self.client.post(
            self.products_url,
            product_data,
            format='json'
        )

        # Sin autenticación debe fallar
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_product_duplicate_sku_same_inventory(self):
        """
        Test: No se puede crear producto con SKU duplicado en el mismo inventario
        """
        self.client.force_authenticate(user=self.user)

        # Crear primer producto
        Product.objects.create(
            name='Martillo 1',
            sku='MART-001',
            quantity=10,
            price=Decimal('25.99'),
            inventory=self.inventory
        )

        # Intentar crear segundo producto con mismo SKU
        product_data = {
            'name': 'Martillo 2',
            'sku': 'MART-001',
            'quantity': 20,
            'price': '30.00',
            'inventory': self.inventory.id,
            'custom_data': {'marca': 'Stanley'}
        }

        response = self.client.post(
            self.products_url,
            product_data,
            format='json'
        )

        # Debe fallar
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_same_sku_different_inventory(self):
        """
        Test: Se puede usar mismo SKU en diferentes inventarios
        """
        self.client.force_authenticate(user=self.user)

        # Crear producto en el primer inventario
        Product.objects.create(
            name='Martillo 1',
            sku='MART-001',
            quantity=10,
            price=Decimal('25.99'),
            inventory=self.inventory
        )

        # Crear inventario adicional para el mismo usuario
        another_inventory = Inventory.objects.create(
            name='Sucursal 2',
            owner=self.user,
            template=self.template
        )

        # Crear producto con mismo SKU en otro inventario
        product_data = {
            'name': 'Martillo 2',
            'sku': 'MART-001',
            'quantity': 20,
            'price': '30.00',
            'inventory': another_inventory.id,
            'custom_data': {'marca': 'Stanley'}
        }

        response = self.client.post(
            self.products_url,
            product_data,
            format='json'
        )

        # Debe funcionar
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_validates_custom_data(self):
        """
        Test: Crear producto valida custom_data según template
        """
        self.client.force_authenticate(user=self.user)

        # custom_data falta campo requerido 'marca'
        product_data = {
            'name': 'Martillo',
            'sku': 'MART-001',
            'quantity': 50,
            'price': '25.99',
            'inventory': self.inventory.id,
            'custom_data': {
                'material': 'Acero'  # Falta 'marca' que es requerido
            }
        }

        response = self.client.post(
            self.products_url,
            product_data,
            format='json'
        )

        # Debe fallar por validación
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProductListTests(APITestCase):
    """
    Tests para listar productos.
    """

    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()

        # Crear usuarios
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpass123',
            name='User 1',
            plan='free'
        )

        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpass123',
            name='User 2',
            plan='free'
        )

        # Crear plantilla
        self.template = BusinessTemplate.objects.create(
            name='General',
            created_by=self.user1
        )

        # Crear inventarios
        self.inventory1 = Inventory.objects.create(
            name='Inventario 1',
            owner=self.user1,
            template=self.template
        )

        self.inventory2 = Inventory.objects.create(
            name='Inventario 2',
            owner=self.user2,
            template=self.template
        )

        # Crear productos para user1
        self.product1 = Product.objects.create(
            name='Producto 1',
            sku='PROD-001',
            quantity=10,
            price=Decimal('10.00'),
            inventory=self.inventory1
        )

        self.product2 = Product.objects.create(
            name='Producto 2',
            sku='PROD-002',
            quantity=20,
            price=Decimal('20.00'),
            inventory=self.inventory1
        )

        # Crear productos para user2
        self.product3 = Product.objects.create(
            name='Producto 3',
            sku='PROD-003',
            quantity=30,
            price=Decimal('30.00'),
            inventory=self.inventory2
        )

        self.products_url = reverse('product-list')

    def test_list_products_filtered_by_inventory(self):
        """
        Test: Usuario solo ve productos de sus propios inventarios
        """
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.products_url)

        # Verificar status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que solo ve sus productos (2 productos)
        self.assertEqual(response.data['count'], 2)

        # Verificar que no ve productos de otros usuarios
        product_names = [p['name'] for p in response.data['results']]
        self.assertIn('Producto 1', product_names)
        self.assertIn('Producto 2', product_names)
        self.assertNotIn('Producto 3', product_names)

    def test_user_cannot_access_other_user_products(self):
        """
        Test: Usuario no puede acceder a productos de otros usuarios
        """
        self.client.force_authenticate(user=self.user1)

        # Intentar acceder al producto del user2
        product_detail_url = reverse('product-detail', kwargs={'pk': self.product3.id})
        response = self.client.get(product_detail_url)

        # Debe retornar 404 (no encontrado) porque no es de su inventario
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_products_filter_by_category(self):
        """
        Test: Filtrar productos por categoría
        """
        # Actualizar categorías
        self.product1.category = 'Herramientas'
        self.product1.save()

        self.product2.category = 'Pinturas'
        self.product2.save()

        self.client.force_authenticate(user=self.user1)

        # Filtrar por categoría
        response = self.client.get(f'{self.products_url}?category=Herramientas')

        # Verificar que solo retorna productos de esa categoría
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Producto 1')


class ProductUpdateTests(APITestCase):
    """
    Tests para actualizar productos.
    """

    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()

        # Crear usuarios
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='User',
            plan='free'
        )

        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            name='Other User',
            plan='free'
        )

        # Crear plantilla
        self.template = BusinessTemplate.objects.create(
            name='Ferretería',
            custom_fields={
                'marca': {'type': 'text', 'required': True}
            },
            created_by=self.user
        )

        # Crear inventarios
        self.inventory = Inventory.objects.create(
            name='Mi Inventario',
            owner=self.user,
            template=self.template
        )

        self.other_inventory = Inventory.objects.create(
            name='Otro Inventario',
            owner=self.other_user,
            template=self.template
        )

        # Crear productos
        self.product = Product.objects.create(
            name='Martillo',
            sku='MART-001',
            quantity=10,
            price=Decimal('25.99'),
            inventory=self.inventory,
            custom_data={'marca': 'Stanley'}
        )

        self.other_product = Product.objects.create(
            name='Destornillador',
            sku='DEST-001',
            quantity=20,
            price=Decimal('15.50'),
            inventory=self.other_inventory,
            custom_data={'marca': 'Bosch'}
        )

    def test_update_product_validates_custom_data(self):
        """
        Test: Actualizar producto valida custom_data
        """
        self.client.force_authenticate(user=self.user)

        product_url = reverse('product-detail', kwargs={'pk': self.product.id})

        # Intentar actualizar sin campo requerido
        update_data = {
            'custom_data': {
                'material': 'Acero'  # Falta 'marca' que es requerido
            }
        }

        response = self.client.patch(
            product_url,
            update_data,
            format='json'
        )

        # Debe fallar por validación
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_success(self):
        """
        Test: Actualizar producto exitosamente
        """
        self.client.force_authenticate(user=self.user)

        product_url = reverse('product-detail', kwargs={'pk': self.product.id})

        update_data = {
            'quantity': 100,
            'price': '30.00'
        }

        response = self.client.patch(
            product_url,
            update_data,
            format='json'
        )

        # Verificar status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que se actualizó en la base de datos
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 100)
        self.assertEqual(self.product.price, Decimal('30.00'))

    def test_user_cannot_update_other_user_product(self):
        """
        Test: Usuario no puede actualizar productos de otros usuarios
        """
        self.client.force_authenticate(user=self.user)

        # Intentar actualizar producto de otro usuario
        other_product_url = reverse('product-detail', kwargs={'pk': self.other_product.id})

        update_data = {
            'quantity': 999
        }

        response = self.client.patch(
            other_product_url,
            update_data,
            format='json'
        )

        # Debe fallar (404 porque no está en su queryset)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Verificar que NO se actualizó
        self.other_product.refresh_from_db()
        self.assertEqual(self.other_product.quantity, 20)


class ProductDeleteTests(APITestCase):
    """
    Tests para eliminar productos (soft delete).
    """

    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()

        # Crear usuario
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='User',
            plan='free'
        )

        # Crear plantilla e inventario
        self.template = BusinessTemplate.objects.create(
            name='General',
            created_by=self.user
        )

        self.inventory = Inventory.objects.create(
            name='Mi Inventario',
            owner=self.user,
            template=self.template
        )

        # Crear producto
        self.product = Product.objects.create(
            name='Producto Test',
            sku='PROD-001',
            quantity=10,
            price=Decimal('10.00'),
            inventory=self.inventory
        )

    def test_delete_product_soft_delete(self):
        """
        Test: Eliminar producto hace soft delete (is_active=False)
        """
        self.client.force_authenticate(user=self.user)

        product_url = reverse('product-detail', kwargs={'pk': self.product.id})

        response = self.client.delete(product_url)

        # Verificar status code
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verificar que el producto sigue en DB pero inactivo
        self.product.refresh_from_db()
        self.assertFalse(self.product.is_active)

    def test_deleted_products_not_in_default_list(self):
        """
        Test: Productos eliminados no aparecen en lista por defecto
        """
        self.client.force_authenticate(user=self.user)

        # Eliminar producto
        self.product.is_active = False
        self.product.save()

        # Listar productos
        products_url = reverse('product-list')
        response = self.client.get(products_url)

        # No debe aparecer en la lista
        self.assertEqual(response.data['count'], 0)


class ProductStockTests(APITestCase):
    """
    Tests para funcionalidades de stock.
    """

    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()

        # Crear usuario
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='User',
            plan='free'
        )

        # Crear plantilla e inventario
        self.template = BusinessTemplate.objects.create(
            name='General',
            created_by=self.user
        )

        self.inventory = Inventory.objects.create(
            name='Mi Inventario',
            owner=self.user,
            template=self.template
        )

        # Crear producto
        self.product = Product.objects.create(
            name='Producto Test',
            sku='PROD-001',
            quantity=10,
            price=Decimal('10.00'),
            inventory=self.inventory,
            low_stock_threshold=15
        )

    def test_product_stock_status(self):
        """
        Test: Verificar que stock_status se calcula correctamente
        """
        self.client.force_authenticate(user=self.user)

        product_url = reverse('product-detail', kwargs={'pk': self.product.id})
        response = self.client.get(product_url)

        # Producto tiene 10 unidades pero threshold es 15
        self.assertEqual(response.data['stock_status'], 'Stock bajo')
        self.assertTrue(response.data['is_low_stock'])
        self.assertFalse(response.data['is_out_of_stock'])

    def test_adjust_stock_endpoint(self):
        """
        Test: Endpoint para ajustar stock
        """
        self.client.force_authenticate(user=self.user)

        adjust_url = reverse('product-adjust-stock', kwargs={'pk': self.product.id})

        # Aumentar stock en 5 unidades
        response = self.client.post(
            adjust_url,
            {'adjustment': 5},
            format='json'
        )

        # Verificar status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que se actualizó
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 15)

    def test_adjust_stock_negative_prevents_negative_quantity(self):
        """
        Test: Ajuste de stock no permite cantidad negativa
        """
        self.client.force_authenticate(user=self.user)

        adjust_url = reverse('product-adjust-stock', kwargs={'pk': self.product.id})

        # Intentar reducir más de lo disponible
        response = self.client.post(
            adjust_url,
            {'adjustment': -20},  # Tiene 10, esto daría -10
            format='json'
        )

        # Debe fallar
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verificar que no cambió
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 10)
