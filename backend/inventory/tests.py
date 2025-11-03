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


class MovementTrackingTests(APITestCase):
    """
    Tests para el seguimiento automático de movimientos de inventario.
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
            quantity=50,
            price=Decimal('10.00'),
            inventory=self.inventory
        )

    def test_movement_created_on_quantity_increase(self):
        """
        Test: Se crea un movimiento de entrada cuando aumenta la cantidad
        """
        from inventory.models import Movement

        initial_movements_count = Movement.objects.filter(product=self.product).count()

        # Aumentar cantidad
        self.product._performed_by = self.user
        self.product.quantity = 100
        self.product.save()

        # Verificar que se creó un movimiento
        movements = Movement.objects.filter(product=self.product)
        self.assertEqual(movements.count(), initial_movements_count + 1)

        # Verificar datos del movimiento
        movement = movements.latest('timestamp')
        self.assertEqual(movement.movement_type, 'entrada')
        self.assertEqual(movement.quantity, 50)
        self.assertEqual(movement.quantity_before, 50)
        self.assertEqual(movement.quantity_after, 100)
        self.assertEqual(movement.performed_by, self.user)

    def test_movement_created_on_quantity_decrease(self):
        """
        Test: Se crea un movimiento de salida cuando disminuye la cantidad
        """
        from inventory.models import Movement

        initial_movements_count = Movement.objects.filter(product=self.product).count()

        # Disminuir cantidad
        self.product._performed_by = self.user
        self.product.quantity = 30
        self.product.save()

        # Verificar que se creó un movimiento
        movements = Movement.objects.filter(product=self.product)
        self.assertEqual(movements.count(), initial_movements_count + 1)

        # Verificar datos del movimiento
        movement = movements.latest('timestamp')
        self.assertEqual(movement.movement_type, 'salida')
        self.assertEqual(movement.quantity, -20)
        self.assertEqual(movement.quantity_before, 50)
        self.assertEqual(movement.quantity_after, 30)
        self.assertEqual(movement.performed_by, self.user)

    def test_no_movement_created_when_quantity_unchanged(self):
        """
        Test: No se crea movimiento si la cantidad no cambia
        """
        from inventory.models import Movement

        initial_movements_count = Movement.objects.filter(product=self.product).count()

        # Guardar sin cambiar cantidad
        self.product._performed_by = self.user
        self.product.name = 'Nuevo Nombre'
        self.product.save()

        # Verificar que NO se creó movimiento
        movements_count = Movement.objects.filter(product=self.product).count()
        self.assertEqual(movements_count, initial_movements_count)

    def test_movement_via_api_update(self):
        """
        Test: Movimiento se crea cuando se actualiza producto via API
        """
        from inventory.models import Movement

        self.client.force_authenticate(user=self.user)

        product_url = reverse('product-detail', kwargs={'pk': self.product.id})

        # Actualizar cantidad via API
        update_data = {
            'quantity': 75
        }

        response = self.client.patch(
            product_url,
            update_data,
            format='json'
        )

        # Verificar que se actualizó
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que se creó un movimiento
        movement = Movement.objects.filter(product=self.product).latest('timestamp')
        self.assertEqual(movement.movement_type, 'entrada')
        self.assertEqual(movement.quantity, 25)
        self.assertEqual(movement.quantity_before, 50)
        self.assertEqual(movement.quantity_after, 75)
        self.assertEqual(movement.performed_by, self.user)

    def test_movement_via_adjust_stock_endpoint(self):
        """
        Test: Movimiento se crea al usar el endpoint adjust_stock
        """
        from inventory.models import Movement

        self.client.force_authenticate(user=self.user)

        adjust_url = reverse('product-adjust-stock', kwargs={'pk': self.product.id})

        # Ajustar stock
        response = self.client.post(
            adjust_url,
            {'adjustment': -10},
            format='json'
        )

        # Verificar respuesta exitosa
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que se creó un movimiento
        movement = Movement.objects.filter(product=self.product).latest('timestamp')
        self.assertEqual(movement.movement_type, 'salida')
        self.assertEqual(movement.quantity, -10)
        self.assertEqual(movement.quantity_before, 50)
        self.assertEqual(movement.quantity_after, 40)
        self.assertEqual(movement.performed_by, self.user)

    def test_movement_reason_is_descriptive(self):
        """
        Test: El reason del movimiento es descriptivo
        """
        from inventory.models import Movement

        # Aumentar cantidad
        self.product._performed_by = self.user
        self.product.quantity = 60
        self.product.save()

        movement = Movement.objects.filter(product=self.product).latest('timestamp')
        self.assertIn('10', movement.reason)
        self.assertIn('unidades', movement.reason.lower())

    def test_multiple_movements_create_history(self):
        """
        Test: Múltiples cambios crean historial completo
        """
        from inventory.models import Movement

        # Contar movimientos iniciales (puede haber uno de la creación del producto)
        initial_count = Movement.objects.filter(product=self.product).count()

        # Cambio 1: Entrada
        self.product._performed_by = self.user
        self.product.quantity = 100
        self.product.save()

        # Cambio 2: Salida
        self.product._performed_by = self.user
        self.product.quantity = 80
        self.product.save()

        # Cambio 3: Entrada
        self.product._performed_by = self.user
        self.product.quantity = 120
        self.product.save()

        # Verificar que hay 3 movimientos nuevos
        movements = Movement.objects.filter(product=self.product).order_by('timestamp')
        self.assertEqual(movements.count(), initial_count + 3)

        # Verificar secuencia de los últimos 3 movimientos
        recent_movements = movements[initial_count:]

        self.assertEqual(recent_movements[0].movement_type, 'entrada')
        self.assertEqual(recent_movements[0].quantity_after, 100)

        self.assertEqual(recent_movements[1].movement_type, 'salida')
        self.assertEqual(recent_movements[1].quantity_after, 80)

        self.assertEqual(recent_movements[2].movement_type, 'entrada')
        self.assertEqual(recent_movements[2].quantity_after, 120)


class DashboardAPITests(APITestCase):
    """
    Tests para el endpoint del dashboard con métricas.
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

        # Crear inventarios para user1
        self.inventory1 = Inventory.objects.create(
            name='Inventario 1',
            owner=self.user1,
            template=self.template
        )

        self.inventory2 = Inventory.objects.create(
            name='Inventario 2',
            owner=self.user1,
            template=self.template
        )

        # Crear inventario para user2
        self.inventory3 = Inventory.objects.create(
            name='Inventario 3',
            owner=self.user2,
            template=self.template
        )

        # Crear productos para user1 - inventory1
        self.product1 = Product.objects.create(
            name='Producto 1',
            sku='PROD-001',
            quantity=100,
            price=Decimal('10.00'),
            low_stock_threshold=20,
            inventory=self.inventory1
        )

        self.product2 = Product.objects.create(
            name='Producto 2',
            sku='PROD-002',
            quantity=15,  # Stock bajo
            price=Decimal('20.00'),
            low_stock_threshold=20,
            inventory=self.inventory1
        )

        self.product3 = Product.objects.create(
            name='Producto 3',
            sku='PROD-003',
            quantity=0,  # Sin stock
            price=Decimal('30.00'),
            inventory=self.inventory1
        )

        # Crear producto para user1 - inventory2
        self.product4 = Product.objects.create(
            name='Producto 4',
            sku='PROD-004',
            quantity=50,
            price=Decimal('15.00'),
            inventory=self.inventory2
        )

        # Crear producto para user2
        self.product5 = Product.objects.create(
            name='Producto 5',
            sku='PROD-005',
            quantity=30,
            price=Decimal('25.00'),
            inventory=self.inventory3
        )

        self.dashboard_url = reverse('dashboard')

    def test_dashboard_requires_authentication(self):
        """
        Test: Dashboard requiere autenticación
        """
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dashboard_returns_correct_metrics(self):
        """
        Test: Dashboard devuelve métricas correctas para el usuario
        """
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar estructura de la respuesta
        self.assertIn('total_products', response.data)
        self.assertIn('total_inventory_value', response.data)
        self.assertIn('low_stock_count', response.data)
        self.assertIn('out_of_stock_count', response.data)
        self.assertIn('total_inventories', response.data)

        # Verificar valores
        self.assertEqual(response.data['total_products'], 4)  # 4 productos del user1
        self.assertEqual(response.data['total_inventories'], 2)  # 2 inventarios

        # Valor total: (100*10) + (15*20) + (0*30) + (50*15) = 1000 + 300 + 0 + 750 = 2050
        self.assertEqual(float(response.data['total_inventory_value']), 2050.0)

        # Stock bajo: product2 (15 <= 20) y product3 (0 <= 10)
        self.assertEqual(response.data['low_stock_count'], 2)

        # Sin stock: product3
        self.assertEqual(response.data['out_of_stock_count'], 1)

    def test_dashboard_user_only_sees_own_data(self):
        """
        Test: Usuario solo ve sus propios datos
        """
        self.client.force_authenticate(user=self.user2)

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # User2 solo tiene 1 producto y 1 inventario
        self.assertEqual(response.data['total_products'], 1)
        self.assertEqual(response.data['total_inventories'], 1)

        # Valor: 30 * 25 = 750
        self.assertEqual(float(response.data['total_inventory_value']), 750.0)

    def test_dashboard_filter_by_inventory(self):
        """
        Test: Dashboard filtra correctamente por inventario
        """
        self.client.force_authenticate(user=self.user1)

        # Filtrar solo inventory1
        response = self.client.get(f'{self.dashboard_url}?inventory={self.inventory1.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Solo 3 productos del inventory1
        self.assertEqual(response.data['total_products'], 3)

        # Valor: (100*10) + (15*20) + (0*30) = 1300
        self.assertEqual(float(response.data['total_inventory_value']), 1300.0)

        # Stock bajo en inventory1: 2 productos
        self.assertEqual(response.data['low_stock_count'], 2)

        # Verificar que incluye info del inventario
        self.assertIn('inventory', response.data)
        self.assertEqual(response.data['inventory']['id'], self.inventory1.id)
        self.assertEqual(response.data['inventory']['name'], 'Inventario 1')

    def test_dashboard_filter_by_inventory_validates_ownership(self):
        """
        Test: Usuario no puede ver dashboard de inventario de otro usuario
        """
        self.client.force_authenticate(user=self.user1)

        # Intentar acceder al inventario del user2
        response = self.client.get(f'{self.dashboard_url}?inventory={self.inventory3.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # No debería ver productos (0 productos porque no le pertenece)
        self.assertEqual(response.data['total_products'], 0)
        self.assertEqual(float(response.data['total_inventory_value']), 0.0)

    def test_dashboard_excludes_inactive_products(self):
        """
        Test: Dashboard excluye productos inactivos
        """
        self.client.force_authenticate(user=self.user1)

        # Marcar un producto como inactivo
        self.product1.is_active = False
        self.product1.save()

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ahora solo 3 productos activos (product1 está inactivo)
        self.assertEqual(response.data['total_products'], 3)

        # Valor sin product1: (15*20) + (0*30) + (50*15) = 300 + 0 + 750 = 1050
        self.assertEqual(float(response.data['total_inventory_value']), 1050.0)

    def test_dashboard_calculates_inventory_value_correctly(self):
        """
        Test: Cálculo correcto del valor total del inventario
        """
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.dashboard_url)

        # Calcular manualmente
        expected_value = (
            (self.product1.quantity * self.product1.price) +
            (self.product2.quantity * self.product2.price) +
            (self.product3.quantity * self.product3.price) +
            (self.product4.quantity * self.product4.price)
        )

        self.assertEqual(
            float(response.data['total_inventory_value']),
            float(expected_value)
        )

    def test_dashboard_low_stock_threshold_logic(self):
        """
        Test: Lógica de detección de stock bajo es correcta
        """
        self.client.force_authenticate(user=self.user1)

        # product2: quantity=15, threshold=20 -> stock bajo
        # product3: quantity=0, threshold=10 -> stock bajo
        # product1: quantity=100, threshold=20 -> OK
        # product4: quantity=50, threshold=10 -> OK

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.data['low_stock_count'], 2)
        self.assertEqual(response.data['out_of_stock_count'], 1)


class DashboardPerformanceTests(APITestCase):
    """
    Tests para verificar la performance del dashboard.
    """

    def setUp(self):
        """Configuración inicial con más datos"""
        self.client = APIClient()

        # Crear usuario
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='User',
            plan='free'
        )

        # Crear plantilla
        self.template = BusinessTemplate.objects.create(
            name='General',
            created_by=self.user
        )

        # Crear inventario
        self.inventory = Inventory.objects.create(
            name='Test Inventory',
            owner=self.user,
            template=self.template
        )

        # Crear 100 productos
        products = []
        for i in range(100):
            products.append(Product(
                name=f'Producto {i}',
                sku=f'PROD-{i:04d}',
                quantity=10 + (i % 50),
                price=Decimal('10.00') + Decimal(i % 100),
                low_stock_threshold=15,
                inventory=self.inventory
            ))
        Product.objects.bulk_create(products)

        self.dashboard_url = reverse('dashboard')

    def test_dashboard_query_count_is_optimized(self):
        """
        Test: Dashboard usa un número mínimo de queries
        """
        from django.test import override_settings
        from django.db import connection
        from django.test.utils import override_settings

        self.client.force_authenticate(user=self.user)

        # Contar queries
        # 9 queries: count products, sum value, count low stock, count out of stock, count inventories,
        # products by category, list inventories, value per inventory, recent movements
        with self.assertNumQueries(9):  # Máximo 9 queries (optimizado con datos de gráficas)
            response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dashboard_response_time_with_100_products(self):
        """
        Test: Dashboard responde en menos de 500ms con 100 productos
        """
        import time

        self.client.force_authenticate(user=self.user)

        start_time = time.time()
        response = self.client.get(self.dashboard_url)
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # Convertir a ms

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_products'], 100)

        # Verificar que responde en menos de 500ms
        self.assertLess(response_time, 500,
            f"Dashboard tomó {response_time:.2f}ms, debe ser < 500ms")

    def test_dashboard_with_filter_is_also_fast(self):
        """
        Test: Dashboard con filtro también es rápido
        """
        import time

        self.client.force_authenticate(user=self.user)

        start_time = time.time()
        response = self.client.get(f'{self.dashboard_url}?inventory={self.inventory.id}')
        end_time = time.time()

        response_time = (end_time - start_time) * 1000

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(response_time, 500,
            f"Dashboard con filtro tomó {response_time:.2f}ms, debe ser < 500ms")


class DashboardChartDataTests(APITestCase):
    """
    Tests para datos de gráficas en el dashboard.
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

        # Crear plantilla
        self.template = BusinessTemplate.objects.create(
            name='General',
            created_by=self.user
        )

        # Crear inventarios
        self.inventory1 = Inventory.objects.create(
            name='Inventario 1',
            owner=self.user,
            template=self.template
        )

        self.inventory2 = Inventory.objects.create(
            name='Inventario 2',
            owner=self.user,
            template=self.template
        )

        # Crear productos con diferentes categorías
        self.product1 = Product.objects.create(
            name='Producto 1',
            sku='PROD-001',
            quantity=100,
            price=Decimal('10.00'),
            category='Electrónica',
            inventory=self.inventory1
        )

        self.product2 = Product.objects.create(
            name='Producto 2',
            sku='PROD-002',
            quantity=50,
            price=Decimal('20.00'),
            category='Electrónica',
            inventory=self.inventory1
        )

        self.product3 = Product.objects.create(
            name='Producto 3',
            sku='PROD-003',
            quantity=30,
            price=Decimal('15.00'),
            category='Herramientas',
            inventory=self.inventory1
        )

        self.product4 = Product.objects.create(
            name='Producto 4',
            sku='PROD-004',
            quantity=25,
            price=Decimal('30.00'),
            category='',  # Sin categoría
            inventory=self.inventory2
        )

        # Crear algunos movimientos
        from inventory.models import Movement
        Movement.objects.create(
            product=self.product1,
            movement_type='entrada',
            quantity=50,
            quantity_before=50,
            quantity_after=100,
            reason='Entrada inicial',
            performed_by=self.user
        )

        Movement.objects.create(
            product=self.product2,
            movement_type='salida',
            quantity=-10,
            quantity_before=60,
            quantity_after=50,
            reason='Venta',
            performed_by=self.user
        )

        self.dashboard_url = reverse('dashboard')

    def test_dashboard_includes_products_by_category(self):
        """
        Test: Dashboard incluye productos agrupados por categoría
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('products_by_category', response.data)

        products_by_category = response.data['products_by_category']

        # Verificar que es una lista
        self.assertIsInstance(products_by_category, list)

        # Debe haber 3 categorías: Electrónica (2), Herramientas (1), Sin categoría (1)
        self.assertEqual(len(products_by_category), 3)

        # Verificar estructura
        for item in products_by_category:
            self.assertIn('category', item)
            self.assertIn('count', item)

        # Verificar datos específicos
        categories_dict = {item['category']: item['count'] for item in products_by_category}
        self.assertEqual(categories_dict['Electrónica'], 2)
        self.assertEqual(categories_dict['Herramientas'], 1)
        self.assertEqual(categories_dict['Sin categoría'], 1)

    def test_dashboard_includes_value_by_inventory(self):
        """
        Test: Dashboard incluye valor total por inventario
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('value_by_inventory', response.data)

        value_by_inventory = response.data['value_by_inventory']

        # Verificar que es una lista
        self.assertIsInstance(value_by_inventory, list)

        # Debe haber 2 inventarios
        self.assertEqual(len(value_by_inventory), 2)

        # Verificar estructura
        for item in value_by_inventory:
            self.assertIn('inventory_id', item)
            self.assertIn('inventory_name', item)
            self.assertIn('value', item)

        # Verificar cálculos
        # Inventory 1: (100*10) + (50*20) + (30*15) = 1000 + 1000 + 450 = 2450
        # Inventory 2: (25*30) = 750
        inventories_dict = {item['inventory_name']: item['value'] for item in value_by_inventory}
        self.assertEqual(inventories_dict['Inventario 1'], 2450.0)
        self.assertEqual(inventories_dict['Inventario 2'], 750.0)

        # Verificar que está ordenado por valor descendente
        self.assertEqual(value_by_inventory[0]['inventory_name'], 'Inventario 1')
        self.assertEqual(value_by_inventory[1]['inventory_name'], 'Inventario 2')

    def test_dashboard_includes_recent_movements(self):
        """
        Test: Dashboard incluye movimientos recientes
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recent_movements', response.data)

        recent_movements = response.data['recent_movements']

        # Verificar que es una lista
        self.assertIsInstance(recent_movements, list)

        # Debe haber al menos 2 movimientos (pueden haber más por la creación de productos)
        self.assertGreaterEqual(len(recent_movements), 2)

        # Verificar estructura - buscar uno de los movimientos que creamos explícitamente
        movement = None
        for m in recent_movements:
            if m['reason'] in ['Entrada inicial', 'Venta']:
                movement = m
                break

        self.assertIsNotNone(movement, "Debe existir al menos un movimiento creado explícitamente")
        self.assertIn('id', movement)
        self.assertIn('product_id', movement)
        self.assertIn('product_name', movement)
        self.assertIn('product_sku', movement)
        self.assertIn('inventory_name', movement)
        self.assertIn('movement_type', movement)
        self.assertIn('movement_type_display', movement)
        self.assertIn('quantity', movement)
        self.assertIn('quantity_before', movement)
        self.assertIn('quantity_after', movement)
        self.assertIn('reason', movement)
        self.assertIn('performed_by', movement)
        self.assertIn('timestamp', movement)

        # Verificar datos específicos
        self.assertEqual(movement['performed_by'], 'user@example.com')

    def test_dashboard_chart_data_with_inventory_filter(self):
        """
        Test: Datos de gráficas se filtran correctamente por inventario
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'{self.dashboard_url}?inventory={self.inventory1.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Solo debe incluir categorías del inventory1
        products_by_category = response.data['products_by_category']
        categories = [item['category'] for item in products_by_category]
        self.assertIn('Electrónica', categories)
        self.assertIn('Herramientas', categories)

        # Solo debe incluir inventory1 en value_by_inventory
        value_by_inventory = response.data['value_by_inventory']
        self.assertEqual(len(value_by_inventory), 1)
        self.assertEqual(value_by_inventory[0]['inventory_name'], 'Inventario 1')

    def test_dashboard_recent_movements_ordered_by_timestamp(self):
        """
        Test: Movimientos recientes están ordenados por fecha descendente
        """
        from inventory.models import Movement
        import time

        self.client.force_authenticate(user=self.user)

        # Crear movimiento adicional con pequeño delay
        time.sleep(0.01)
        Movement.objects.create(
            product=self.product3,
            movement_type='entrada',
            quantity=10,
            quantity_before=20,
            quantity_after=30,
            reason='Nuevo ingreso',
            performed_by=self.user
        )

        response = self.client.get(self.dashboard_url)

        recent_movements = response.data['recent_movements']

        # El movimiento más reciente debe estar primero
        self.assertEqual(recent_movements[0]['product_name'], 'Producto 3')
        self.assertEqual(recent_movements[0]['reason'], 'Nuevo ingreso')

    def test_dashboard_handles_empty_category(self):
        """
        Test: Dashboard maneja correctamente productos sin categoría
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.dashboard_url)

        products_by_category = response.data['products_by_category']
        categories = [item['category'] for item in products_by_category]

        # Debe aparecer como "Sin categoría"
        self.assertIn('Sin categoría', categories)

    def test_dashboard_limits_recent_movements_to_10(self):
        """
        Test: Dashboard limita movimientos recientes a 10
        """
        from inventory.models import Movement

        # Crear 15 movimientos
        for i in range(13):  # Ya hay 2, sumamos 13 más = 15 total
            Movement.objects.create(
                product=self.product1,
                movement_type='ajuste',
                quantity=1,
                quantity_before=100 + i,
                quantity_after=101 + i,
                reason=f'Ajuste {i}',
                performed_by=self.user
            )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.dashboard_url)

        recent_movements = response.data['recent_movements']

        # Debe retornar máximo 10 movimientos
        self.assertLessEqual(len(recent_movements), 10)


class AlertAPITests(APITestCase):
    """
    Tests para el endpoint de alertas de stock bajo.
    """

    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()

        # Crear usuarios
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123',
            name='User 1',
            plan='free'
        )

        self.user2 = User.objects.create_user(
            email='user2@test.com',
            password='testpass123',
            name='User 2',
            plan='free'
        )

        # Crear plantilla
        self.template = BusinessTemplate.objects.create(
            name='Test Template',
            description='Test',
            custom_fields=[],
            created_by=self.user1,
            is_active=True
        )

        # Crear inventarios
        self.inventory1 = Inventory.objects.create(
            name='Inventory 1',
            owner=self.user1,
            template=self.template
        )

        self.inventory2 = Inventory.objects.create(
            name='Inventory 2',
            owner=self.user2,
            template=self.template
        )

        # Crear productos con diferentes niveles de stock
        # Producto 1: Stock crítico (0/10 = 0.0 ratio)
        self.product1 = Product.objects.create(
            name='Producto Crítico',
            sku='CRIT-001',
            quantity=0,
            price=Decimal('100.00'),
            low_stock_threshold=10,
            inventory=self.inventory1,
            category='Categoría A'
        )

        # Producto 2: Stock muy bajo (2/10 = 0.2 ratio)
        self.product2 = Product.objects.create(
            name='Producto Muy Bajo',
            sku='LOW-001',
            quantity=2,
            price=Decimal('50.00'),
            low_stock_threshold=10,
            inventory=self.inventory1,
            category='Categoría A'
        )

        # Producto 3: Stock bajo (5/10 = 0.5 ratio)
        self.product3 = Product.objects.create(
            name='Producto Bajo',
            sku='LOW-002',
            quantity=5,
            price=Decimal('75.00'),
            low_stock_threshold=10,
            inventory=self.inventory1,
            category='Categoría B'
        )

        # Producto 4: Stock normal (15/10 = 1.5 ratio) - NO debe aparecer
        self.product4 = Product.objects.create(
            name='Producto Normal',
            sku='NORM-001',
            quantity=15,
            price=Decimal('80.00'),
            low_stock_threshold=10,
            inventory=self.inventory1,
            category='Categoría A'
        )

        # Producto 5: Stock bajo de otro usuario
        self.product5 = Product.objects.create(
            name='Producto Otro Usuario',
            sku='OTHER-001',
            quantity=3,
            price=Decimal('60.00'),
            low_stock_threshold=10,
            inventory=self.inventory2,
            category='Categoría C'
        )

        # Producto 6: Inactivo con stock bajo - NO debe aparecer
        self.product6 = Product.objects.create(
            name='Producto Inactivo',
            sku='INACT-001',
            quantity=2,
            price=Decimal('40.00'),
            low_stock_threshold=10,
            inventory=self.inventory1,
            category='Categoría A',
            is_active=False
        )

        self.alerts_url = reverse('alerts')

    def test_alerts_requires_authentication(self):
        """
        Test: Endpoint requiere autenticación
        """
        response = self.client.get(self.alerts_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_alerts_returns_low_stock_products_only(self):
        """
        Test: Solo retorna productos con stock bajo
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.alerts_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Debe retornar 3 productos (product1, product2, product3)
        # product4 tiene stock normal, no debe aparecer
        # product6 está inactivo, no debe aparecer
        self.assertEqual(response.data['count'], 3)

        # Verificar que los SKUs correctos están presentes
        skus = [item['sku'] for item in response.data['results']]
        self.assertIn('CRIT-001', skus)
        self.assertIn('LOW-001', skus)
        self.assertIn('LOW-002', skus)
        self.assertNotIn('NORM-001', skus)
        self.assertNotIn('INACT-001', skus)

    def test_alerts_ordered_by_criticality(self):
        """
        Test: Productos ordenados por criticidad (ratio más bajo primero)
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.alerts_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data['results']

        # Verificar orden: CRIT-001 (0.0), LOW-001 (0.2), LOW-002 (0.5)
        self.assertEqual(results[0]['sku'], 'CRIT-001')
        self.assertEqual(results[1]['sku'], 'LOW-001')
        self.assertEqual(results[2]['sku'], 'LOW-002')

        # Verificar ratios de criticidad
        self.assertEqual(results[0]['criticality_ratio'], 0.0)
        self.assertEqual(results[1]['criticality_ratio'], 0.2)
        self.assertEqual(results[2]['criticality_ratio'], 0.5)

    def test_alerts_includes_required_fields(self):
        """
        Test: Respuesta incluye todos los campos necesarios
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.alerts_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product = response.data['results'][0]

        # Verificar campos requeridos
        required_fields = [
            'id', 'name', 'sku', 'quantity', 'low_stock_threshold',
            'price', 'category', 'inventory_id', 'inventory_name',
            'owner_email', 'owner_name', 'criticality_ratio',
            'alert_sent', 'stock_status', 'is_out_of_stock'
        ]

        for field in required_fields:
            self.assertIn(field, product)

    def test_alerts_includes_inventory_info(self):
        """
        Test: Incluye información del inventario y propietario
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.alerts_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product = response.data['results'][0]

        self.assertEqual(product['inventory_name'], 'Inventory 1')
        self.assertEqual(product['owner_email'], 'user1@test.com')
        self.assertEqual(product['owner_name'], 'User 1')

    def test_alerts_user_sees_only_own_products(self):
        """
        Test: Usuario solo ve alertas de sus propios inventarios
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.alerts_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # user1 debe ver solo sus 3 productos, no el de user2
        self.assertEqual(response.data['count'], 3)

        skus = [item['sku'] for item in response.data['results']]
        self.assertNotIn('OTHER-001', skus)

    def test_alerts_filter_by_inventory(self):
        """
        Test: Filtrar alertas por inventario específico
        """
        self.client.force_authenticate(user=self.user1)

        url = f"{self.alerts_url}?inventory={self.inventory1.id}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Todos los productos deben ser del inventory1
        for item in response.data['results']:
            self.assertEqual(item['inventory_id'], self.inventory1.id)

    def test_alerts_filter_new_only(self):
        """
        Test: Filtrar solo alertas nuevas (no enviadas)
        """
        # Marcar product2 como alerta enviada
        self.product2.alert_sent = True
        self.product2.save()

        self.client.force_authenticate(user=self.user1)

        # Sin filtro: debe ver 3 productos
        response = self.client.get(self.alerts_url)
        self.assertEqual(response.data['count'], 3)

        # Con filtro new_only=true: debe ver solo 2 (sin product2)
        url = f"{self.alerts_url}?new_only=true"
        response = self.client.get(url)

        self.assertEqual(response.data['count'], 2)

        skus = [item['sku'] for item in response.data['results']]
        self.assertNotIn('LOW-001', skus)  # product2 tiene alert_sent=True
        self.assertIn('CRIT-001', skus)
        self.assertIn('LOW-002', skus)

    def test_alerts_pagination(self):
        """
        Test: Paginación funciona correctamente
        """
        # Crear 12 productos con stock bajo
        for i in range(12):
            Product.objects.create(
                name=f'Producto {i}',
                sku=f'PROD-{i:03d}',
                quantity=1,
                price=Decimal('10.00'),
                low_stock_threshold=10,
                inventory=self.inventory1,
                category='Test'
            )

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.alerts_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Total debe ser 15 (3 originales + 12 nuevos)
        self.assertEqual(response.data['count'], 15)

        # Primera página debe tener 10 items (page_size por defecto)
        self.assertEqual(len(response.data['results']), 10)

        # Debe tener link a siguiente página
        self.assertIsNotNone(response.data['next'])

    def test_alerts_custom_page_size(self):
        """
        Test: Se puede personalizar el tamaño de página
        """
        self.client.force_authenticate(user=self.user1)

        url = f"{self.alerts_url}?page_size=2"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_alerts_stock_status_field(self):
        """
        Test: Campo stock_status muestra estado correcto
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.alerts_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data['results']

        # product1 (quantity=0) debe estar "Sin stock"
        critical = next(p for p in results if p['sku'] == 'CRIT-001')
        self.assertEqual(critical['stock_status'], 'Sin stock')
        self.assertTrue(critical['is_out_of_stock'])

        # product2 y product3 deben estar "Stock bajo"
        low = next(p for p in results if p['sku'] == 'LOW-001')
        self.assertEqual(low['stock_status'], 'Stock bajo')
        self.assertFalse(low['is_out_of_stock'])

    def test_alerts_image_url_optimization(self):
        """
        Test: URL de imagen incluye transformaciones de Cloudinary
        """
        # Este test verifica que el serializer incluya el campo,
        # pero sin imagen real retorna None
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.alerts_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product = response.data['results'][0]
        self.assertIn('image_url', product)
        # Sin imagen real, debe ser None
        self.assertIsNone(product['image_url'])

    def test_alerts_empty_when_all_stock_ok(self):
        """
        Test: Retorna lista vacía cuando no hay alertas
        """
        # Actualizar todos los productos a stock normal
        Product.objects.filter(inventory=self.inventory1).update(quantity=50)

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.alerts_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)

    def test_alerts_category_included(self):
        """
        Test: Categoría del producto está incluida en respuesta
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.alerts_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product = response.data['results'][0]
        self.assertIn('category', product)
        self.assertIsNotNone(product['category'])


class InventoryExportCSVTests(APITestCase):
    """
    Tests para la exportación de inventarios a CSV.
    """

    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()

        # Crear usuarios
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123',
            name='User 1',
            plan='free'
        )

        self.user2 = User.objects.create_user(
            email='user2@test.com',
            password='testpass123',
            name='User 2',
            plan='free'
        )

        # Crear plantilla con custom_fields
        self.template = BusinessTemplate.objects.create(
            name='Ferretería',
            description='Plantilla para ferretería',
            custom_fields=[
                {'name': 'marca', 'type': 'text', 'required': True},
                {'name': 'material', 'type': 'text', 'required': False}
            ],
            created_by=self.user1,
            is_active=True
        )

        # Crear inventarios
        self.inventory1 = Inventory.objects.create(
            name='Mi Ferretería',
            owner=self.user1,
            template=self.template
        )

        self.inventory2 = Inventory.objects.create(
            name='Otra Ferretería',
            owner=self.user2,
            template=self.template
        )

        # Crear productos con custom_data
        self.product1 = Product.objects.create(
            name='Martillo',
            sku='MART-001',
            description='Martillo de acero',
            quantity=50,
            price=Decimal('25.99'),
            low_stock_threshold=10,
            category='Herramientas',
            inventory=self.inventory1,
            custom_data={'marca': 'Stanley', 'material': 'Acero'}
        )

        self.product2 = Product.objects.create(
            name='Tornillo',
            sku='TORN-001',
            description='Tornillo para madera',
            quantity=100,
            price=Decimal('0.50'),
            low_stock_threshold=20,
            category='Ferretería',
            inventory=self.inventory1,
            custom_data={'marca': 'Truper', 'material': 'Hierro'}
        )

        self.product3 = Product.objects.create(
            name='Pintura',
            sku='PINT-001',
            description='',
            quantity=15,
            price=Decimal('35.00'),
            low_stock_threshold=5,
            category='',
            inventory=self.inventory1,
            custom_data={'marca': 'Comex'}
        )

        # Producto inactivo - no debe aparecer
        self.product4 = Product.objects.create(
            name='Producto Inactivo',
            sku='INACT-001',
            quantity=10,
            price=Decimal('10.00'),
            low_stock_threshold=5,
            inventory=self.inventory1,
            is_active=False
        )

        # Producto de otro usuario
        self.product5 = Product.objects.create(
            name='Producto Otro Usuario',
            sku='OTHER-001',
            quantity=20,
            price=Decimal('15.00'),
            low_stock_threshold=5,
            inventory=self.inventory2
        )

    def test_export_requires_authentication(self):
        """
        Test: Endpoint requiere autenticación
        """
        url = reverse('inventory-export', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_export_returns_csv_file(self):
        """
        Test: Retorna archivo CSV con content-type correcto
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-export', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('inventario_', response['Content-Disposition'])

    def test_export_includes_correct_headers(self):
        """
        Test: CSV incluye encabezados correctos
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-export', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Decodificar contenido
        content = response.content.decode('utf-8-sig')
        lines = content.strip().split('\r\n')

        # Primera línea son los headers
        headers = lines[0]

        # Verificar columnas estándar
        self.assertIn('SKU', headers)
        self.assertIn('Nombre', headers)
        self.assertIn('Descripción', headers)
        self.assertIn('Cantidad', headers)
        self.assertIn('Precio', headers)
        self.assertIn('Categoría', headers)
        self.assertIn('Estado Stock', headers)

        # Verificar columnas personalizadas
        self.assertIn('Custom: marca', headers)
        self.assertIn('Custom: material', headers)

    def test_export_includes_all_active_products(self):
        """
        Test: CSV incluye todos los productos activos
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-export', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.content.decode('utf-8-sig')
        lines = content.strip().split('\r\n')

        # Primera línea = headers, resto = datos
        # Debe tener 4 líneas (1 header + 3 productos activos)
        self.assertEqual(len(lines), 4)

        # Verificar que los SKUs estén presentes
        full_content = '\n'.join(lines)
        self.assertIn('MART-001', full_content)
        self.assertIn('TORN-001', full_content)
        self.assertIn('PINT-001', full_content)

        # Producto inactivo NO debe aparecer
        self.assertNotIn('INACT-001', full_content)

    def test_export_custom_data_flattened(self):
        """
        Test: custom_data se aplana correctamente en columnas
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-export', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.content.decode('utf-8-sig')
        lines = content.strip().split('\r\n')

        # Verificar que los valores custom estén presentes
        full_content = '\n'.join(lines)
        self.assertIn('Stanley', full_content)
        self.assertIn('Truper', full_content)
        self.assertIn('Comex', full_content)
        self.assertIn('Acero', full_content)
        self.assertIn('Hierro', full_content)

    def test_export_handles_empty_fields(self):
        """
        Test: Maneja correctamente campos vacíos
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-export', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.content.decode('utf-8-sig')

        # El producto3 tiene descripción vacía y categoría vacía
        # Debe aparecer en el CSV sin causar errores
        self.assertIn('PINT-001', content)

    def test_export_permission_denied_other_user(self):
        """
        Test: Usuario no puede exportar inventario de otro usuario
        """
        self.client.force_authenticate(user=self.user2)
        url = reverse('inventory-export', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        # Retorna 404 porque get_queryset() filtra por usuario
        # Esto es correcto: no revelamos si el inventario existe
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_export_products_ordered_by_sku(self):
        """
        Test: Productos ordenados por SKU
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-export', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.content.decode('utf-8-sig')
        lines = content.strip().split('\r\n')

        # Verificar orden: MART-001, PINT-001, TORN-001 (alfabético)
        data_lines = lines[1:]  # Sin header
        self.assertIn('MART-001', data_lines[0])
        self.assertIn('PINT-001', data_lines[1])
        self.assertIn('TORN-001', data_lines[2])

    def test_export_includes_stock_status(self):
        """
        Test: Incluye el estado del stock calculado
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-export', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.content.decode('utf-8-sig')

        # Debe incluir estados de stock
        self.assertIn('En stock', content)

    def test_export_empty_inventory(self):
        """
        Test: Exportar inventario vacío genera CSV solo con headers
        """
        # Crear inventario vacío
        empty_inventory = Inventory.objects.create(
            name='Inventario Vacío',
            owner=self.user1,
            template=self.template
        )

        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-export', kwargs={'pk': empty_inventory.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.content.decode('utf-8-sig')
        lines = content.strip().split('\r\n')

        # Solo debe tener 1 línea (headers)
        self.assertEqual(len(lines), 1)

    def test_export_filename_includes_inventory_info(self):
        """
        Test: Nombre del archivo incluye ID y nombre del inventario
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-export', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        filename = response['Content-Disposition']
        self.assertIn(f'inventario_{self.inventory1.id}', filename)
        self.assertIn('Mi Ferretería', filename)
        self.assertIn('.csv', filename)


class InventoryStatsTests(APITestCase):
    """
    Tests para las estadísticas detalladas de inventario.
    """

    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()

        # Crear usuarios
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123',
            name='User 1',
            plan='free'
        )

        self.user2 = User.objects.create_user(
            email='user2@test.com',
            password='testpass123',
            name='User 2',
            plan='free'
        )

        # Crear plantilla
        self.template = BusinessTemplate.objects.create(
            name='Test Template',
            description='Test',
            custom_fields=[],
            created_by=self.user1,
            is_active=True
        )

        # Crear inventarios
        self.inventory1 = Inventory.objects.create(
            name='Bodega Principal',
            owner=self.user1,
            template=self.template
        )

        self.inventory2 = Inventory.objects.create(
            name='Bodega Secundaria',
            owner=self.user2,
            template=self.template
        )

        # Crear productos con diferentes estados
        # Productos en stock (cantidad > threshold)
        self.product1 = Product.objects.create(
            name='Producto 1',
            sku='PROD-001',
            quantity=100,
            price=Decimal('50.00'),
            low_stock_threshold=10,
            category='Electrónica',
            inventory=self.inventory1
        )

        self.product2 = Product.objects.create(
            name='Producto 2',
            sku='PROD-002',
            quantity=50,
            price=Decimal('30.00'),
            low_stock_threshold=10,
            category='Electrónica',
            inventory=self.inventory1
        )

        # Productos con stock bajo (cantidad <= threshold pero > 0)
        self.product3 = Product.objects.create(
            name='Producto 3',
            sku='PROD-003',
            quantity=5,
            price=Decimal('20.00'),
            low_stock_threshold=10,
            category='Herramientas',
            inventory=self.inventory1
        )

        self.product4 = Product.objects.create(
            name='Producto 4',
            sku='PROD-004',
            quantity=8,
            price=Decimal('15.00'),
            low_stock_threshold=10,
            category='Herramientas',
            inventory=self.inventory1
        )

        # Productos sin stock (cantidad = 0)
        self.product5 = Product.objects.create(
            name='Producto 5',
            sku='PROD-005',
            quantity=0,
            price=Decimal('10.00'),
            low_stock_threshold=10,
            category='Ferretería',
            inventory=self.inventory1
        )

        # Producto inactivo (no debe contar)
        self.product6 = Product.objects.create(
            name='Producto Inactivo',
            sku='PROD-006',
            quantity=100,
            price=Decimal('100.00'),
            low_stock_threshold=10,
            category='Electrónica',
            inventory=self.inventory1,
            is_active=False
        )

        # Producto sin categoría
        self.product7 = Product.objects.create(
            name='Producto 7',
            sku='PROD-007',
            quantity=20,
            price=Decimal('25.00'),
            low_stock_threshold=10,
            category='',
            inventory=self.inventory1
        )

        # Crear algunos movimientos
        from inventory.models import Movement
        Movement.objects.create(
            product=self.product1,
            movement_type='entrada',
            quantity=50,
            quantity_before=50,
            quantity_after=100,
            reason='Entrada inicial',
            performed_by=self.user1
        )

        Movement.objects.create(
            product=self.product3,
            movement_type='salida',
            quantity=-5,
            quantity_before=10,
            quantity_after=5,
            reason='Venta',
            performed_by=self.user1
        )

    def test_stats_requires_authentication(self):
        """
        Test: Endpoint requiere autenticación
        """
        url = reverse('inventory-stats', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_stats_returns_correct_structure(self):
        """
        Test: Respuesta tiene la estructura correcta
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-stats', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar campos requeridos
        required_fields = [
            'inventory_id',
            'inventory_name',
            'total_products',
            'total_value',
            'low_stock_products',
            'out_of_stock_products',
            'stock_distribution',
            'categories',
            'top_products_by_value',
            'recent_movements'
        ]

        for field in required_fields:
            self.assertIn(field, response.data)

    def test_stats_correct_product_count(self):
        """
        Test: Cuenta correcta de productos (solo activos)
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-stats', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 6 productos activos (product6 está inactivo)
        self.assertEqual(response.data['total_products'], 6)

    def test_stats_correct_total_value(self):
        """
        Test: Valor total calculado correctamente
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-stats', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Calcular valor esperado:
        # product1: 100 * 50 = 5000
        # product2: 50 * 30 = 1500
        # product3: 5 * 20 = 100
        # product4: 8 * 15 = 120
        # product5: 0 * 10 = 0
        # product7: 20 * 25 = 500
        # Total: 7220
        expected_value = 7220.0
        self.assertEqual(response.data['total_value'], expected_value)

    def test_stats_stock_distribution(self):
        """
        Test: Distribución de stock correcta
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-stats', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        distribution = response.data['stock_distribution']

        # in_stock: product1, product2, product7 (quantity > threshold)
        self.assertEqual(distribution['in_stock'], 3)

        # low_stock: product3, product4 (0 < quantity <= threshold)
        self.assertEqual(distribution['low_stock'], 2)

        # out_of_stock: product5 (quantity = 0)
        self.assertEqual(distribution['out_of_stock'], 1)

    def test_stats_categories_aggregation(self):
        """
        Test: Agregación por categorías correcta
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-stats', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        categories = response.data['categories']

        # Debe tener 4 categorías (Electrónica, Herramientas, Ferretería, Sin categoría)
        self.assertEqual(len(categories), 4)

        # Verificar que incluye nombres de categoría
        category_names = [cat['name'] for cat in categories]
        self.assertIn('Electrónica', category_names)
        self.assertIn('Herramientas', category_names)
        self.assertIn('Ferretería', category_names)
        self.assertIn('Sin categoría', category_names)

        # Verificar estructura de cada categoría
        for cat in categories:
            self.assertIn('name', cat)
            self.assertIn('count', cat)
            self.assertIn('total_value', cat)

    def test_stats_top_products_by_value(self):
        """
        Test: Top productos ordenados por valor total
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-stats', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        top_products = response.data['top_products_by_value']

        # Debe tener productos
        self.assertGreater(len(top_products), 0)

        # El primer producto debe ser el de mayor valor (product1: 100*50 = 5000)
        self.assertEqual(top_products[0]['sku'], 'PROD-001')
        self.assertEqual(top_products[0]['total_value'], 5000.0)

        # Verificar estructura
        for product in top_products:
            self.assertIn('id', product)
            self.assertIn('name', product)
            self.assertIn('sku', product)
            self.assertIn('quantity', product)
            self.assertIn('price', product)
            self.assertIn('total_value', product)
            self.assertIn('category', product)

    def test_stats_recent_movements(self):
        """
        Test: Movimientos recientes incluidos
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-stats', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        movements = response.data['recent_movements']

        # Debe tener al menos los 2 movimientos creados
        self.assertGreaterEqual(len(movements), 2)

        # Verificar estructura
        for movement in movements:
            self.assertIn('id', movement)
            self.assertIn('product_name', movement)
            self.assertIn('product_sku', movement)
            self.assertIn('movement_type', movement)
            self.assertIn('quantity', movement)
            self.assertIn('quantity_before', movement)
            self.assertIn('quantity_after', movement)
            self.assertIn('reason', movement)
            self.assertIn('performed_by', movement)
            self.assertIn('timestamp', movement)

    def test_stats_permission_denied_other_user(self):
        """
        Test: Usuario no puede ver stats de inventario ajeno
        """
        self.client.force_authenticate(user=self.user2)
        url = reverse('inventory-stats', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        # Retorna 404 porque get_queryset() filtra por usuario
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_stats_empty_inventory(self):
        """
        Test: Stats de inventario vacío retorna ceros
        """
        empty_inventory = Inventory.objects.create(
            name='Inventario Vacío',
            owner=self.user1,
            template=self.template
        )

        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-stats', kwargs={'pk': empty_inventory.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['total_products'], 0)
        self.assertEqual(response.data['total_value'], 0.0)
        self.assertEqual(response.data['low_stock_products'], 0)
        self.assertEqual(response.data['out_of_stock_products'], 0)
        self.assertEqual(len(response.data['categories']), 0)
        self.assertEqual(len(response.data['top_products_by_value']), 0)
        self.assertEqual(len(response.data['recent_movements']), 0)

    def test_stats_inventory_name_included(self):
        """
        Test: Nombre del inventario incluido en respuesta
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-stats', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['inventory_name'], 'Bodega Principal')
        self.assertEqual(response.data['inventory_id'], self.inventory1.id)

    def test_stats_excludes_inactive_products(self):
        """
        Test: Productos inactivos no se incluyen en estadísticas
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse('inventory-stats', kwargs={'pk': self.inventory1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # product6 está inactivo y vale 10000 (100*100)
        # Si se incluyera, el total_value sería 17220
        # Como no se incluye, debe ser 7220
        self.assertEqual(response.data['total_value'], 7220.0)

        # Top products no debe incluir PROD-006
        top_skus = [p['sku'] for p in response.data['top_products_by_value']]
        self.assertNotIn('PROD-006', top_skus)
