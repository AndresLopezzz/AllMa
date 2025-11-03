from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User
from inventory.models import BusinessTemplate, Inventory, Product, Movement
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Crea datos de prueba para el sistema de inventarios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina todos los datos antes de crear nuevos',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Eliminando datos existentes...'))
            Movement.objects.all().delete()
            Product.objects.all().delete()
            Inventory.objects.all().delete()
            BusinessTemplate.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Datos eliminados'))

        self.stdout.write(self.style.MIGRATE_HEADING('Iniciando seed de datos...'))

        with transaction.atomic():
            # Crear usuarios
            self.stdout.write('Creando usuarios...')
            users = self.create_users()
            self.stdout.write(self.style.SUCCESS(f'✓ {len(users)} usuarios creados'))

            # Crear plantillas
            self.stdout.write('Creando plantillas de negocio...')
            templates = self.create_templates(users[0])
            self.stdout.write(self.style.SUCCESS(f'✓ {len(templates)} plantillas creadas'))

            # Crear inventarios
            self.stdout.write('Creando inventarios...')
            inventories = self.create_inventories(users, templates)
            self.stdout.write(self.style.SUCCESS(f'✓ {len(inventories)} inventarios creados'))

            # Crear productos
            self.stdout.write('Creando productos...')
            products = self.create_products(inventories)
            self.stdout.write(self.style.SUCCESS(f'✓ {len(products)} productos creados'))

            # Crear movimientos
            self.stdout.write('Creando movimientos...')
            movements = self.create_movements(products, users)
            self.stdout.write(self.style.SUCCESS(f'✓ {len(movements)} movimientos creados'))

        self.stdout.write(self.style.SUCCESS('\n✨ Seed completado exitosamente!\n'))
        self.print_summary(users, templates, inventories, products, movements)

    def create_users(self):
        """Crea 3 usuarios con diferentes planes"""
        users = []

        # Usuario Free
        try:
            user_free = User.objects.get(email='free@example.com')
        except User.DoesNotExist:
            user_free = User.objects.create_user(
                email='free@example.com',
                name='Usuario Free',
                password='password123',
                plan='free',
                is_active=True
            )
        users.append(user_free)

        # Usuario Pro
        try:
            user_pro = User.objects.get(email='pro@example.com')
        except User.DoesNotExist:
            user_pro = User.objects.create_user(
                email='pro@example.com',
                name='Usuario Pro',
                password='password123',
                plan='pro',
                is_active=True
            )
        users.append(user_pro)

        # Usuario Pro 2
        try:
            user_pro2 = User.objects.get(email='pro2@example.com')
        except User.DoesNotExist:
            user_pro2 = User.objects.create_user(
                email='pro2@example.com',
                name='Usuario Pro 2',
                password='password123',
                plan='pro',
                is_active=True
            )
        users.append(user_pro2)

        return users

    def create_templates(self, creator):
        """Crea 5 plantillas de negocio"""
        templates = []

        templates_data = [
            {
                'name': 'Ferretería',
                'description': 'Plantilla para ferreterías y tiendas de construcción',
                'custom_fields': [
                    {'name': 'marca', 'type': 'text', 'required': True},
                    {'name': 'material', 'type': 'text', 'required': False},
                    {'name': 'medida', 'type': 'text', 'required': False}
                ]
            },
            {
                'name': 'Ropa',
                'description': 'Plantilla para tiendas de ropa y moda',
                'custom_fields': [
                    {'name': 'talla', 'type': 'select', 'required': True, 'options': ['XS', 'S', 'M', 'L', 'XL', 'XXL']},
                    {'name': 'color', 'type': 'text', 'required': True},
                    {'name': 'temporada', 'type': 'select', 'required': False, 'options': ['Verano', 'Otoño', 'Invierno', 'Primavera']}
                ]
            },
            {
                'name': 'Electrónica',
                'description': 'Plantilla para tiendas de electrónica y tecnología',
                'custom_fields': [
                    {'name': 'marca', 'type': 'text', 'required': True},
                    {'name': 'modelo', 'type': 'text', 'required': True},
                    {'name': 'garantia_meses', 'type': 'number', 'required': False}
                ]
            },
            {
                'name': 'Alimentos',
                'description': 'Plantilla para tiendas de alimentos y bebidas',
                'custom_fields': [
                    {'name': 'fecha_vencimiento', 'type': 'date', 'required': True},
                    {'name': 'lote', 'type': 'text', 'required': False},
                    {'name': 'refrigeracion_requerida', 'type': 'checkbox', 'required': False}
                ]
            },
            {
                'name': 'Librería',
                'description': 'Plantilla para librerías y papelerías',
                'custom_fields': [
                    {'name': 'autor', 'type': 'text', 'required': False},
                    {'name': 'editorial', 'type': 'text', 'required': False},
                    {'name': 'isbn', 'type': 'text', 'required': False}
                ]
            }
        ]

        for data in templates_data:
            template, created = BusinessTemplate.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'custom_fields': data['custom_fields'],
                    'created_by': creator,
                    'is_active': True
                }
            )
            templates.append(template)

        return templates

    def create_inventories(self, users, templates):
        """Crea inventarios para cada usuario"""
        inventories = []

        # Usuario Free: 1 inventario
        inv1 = Inventory.objects.create(
            name='Ferretería El Tornillo',
            owner=users[0],
            template=templates[0]
        )
        inventories.append(inv1)

        # Usuario Pro: 3 inventarios
        inv2 = Inventory.objects.create(
            name='Boutique Fashion',
            owner=users[1],
            template=templates[1]
        )
        inventories.append(inv2)

        inv3 = Inventory.objects.create(
            name='Tech Store',
            owner=users[1],
            template=templates[2]
        )
        inventories.append(inv3)

        inv4 = Inventory.objects.create(
            name='Super Mercado',
            owner=users[1],
            template=templates[3]
        )
        inventories.append(inv4)

        # Usuario Pro 2: 6 inventarios
        inv5 = Inventory.objects.create(
            name='Librería Central',
            owner=users[2],
            template=templates[4]
        )
        inventories.append(inv5)

        inv6 = Inventory.objects.create(
            name='Ferretería Norte',
            owner=users[2],
            template=templates[0]
        )
        inventories.append(inv6)

        inv7 = Inventory.objects.create(
            name='Ropa Deportiva',
            owner=users[2],
            template=templates[1]
        )
        inventories.append(inv7)

        inv8 = Inventory.objects.create(
            name='Electrónica Premium',
            owner=users[2],
            template=templates[2]
        )
        inventories.append(inv8)

        inv9 = Inventory.objects.create(
            name='Mini Market 24/7',
            owner=users[2],
            template=templates[3]
        )
        inventories.append(inv9)

        inv10 = Inventory.objects.create(
            name='Papelería Express',
            owner=users[2],
            template=templates[4]
        )
        inventories.append(inv10)

        return inventories

    def create_products(self, inventories):
        """Crea ~100 productos distribuidos en los inventarios"""
        products = []
        categories_map = {
            'Ferretería El Tornillo': ['Herramientas', 'Ferretería', 'Pinturas', 'Electricidad'],
            'Boutique Fashion': ['Ropa Hombre', 'Ropa Mujer', 'Accesorios', 'Calzado'],
            'Tech Store': ['Computadoras', 'Celulares', 'Accesorios', 'Audio'],
            'Super Mercado': ['Lácteos', 'Carnes', 'Frutas', 'Verduras', 'Bebidas'],
            'Librería Central': ['Libros', 'Útiles', 'Arte', 'Papelería'],
            'Ferretería Norte': ['Herramientas', 'Construcción', 'Jardinería'],
            'Ropa Deportiva': ['Ropa Deportiva', 'Calzado Deportivo', 'Accesorios'],
            'Electrónica Premium': ['Laptops', 'Tablets', 'Smart Home', 'Gaming'],
            'Mini Market 24/7': ['Snacks', 'Bebidas', 'Enlatados', 'Higiene'],
            'Papelería Express': ['Oficina', 'Escolar', 'Arte']
        }

        products_per_inventory = {
            inventories[0]: 15,  # Free user
            inventories[1]: 12,
            inventories[2]: 12,
            inventories[3]: 12,  # Pro user inventories
            inventories[4]: 10,
            inventories[5]: 10,
            inventories[6]: 10,
            inventories[7]: 10,
            inventories[8]: 10,
            inventories[9]: 9   # Premium user inventories
        }

        sku_counter = 1

        for inventory, count in products_per_inventory.items():
            categories = categories_map.get(inventory.name, ['General'])

            for i in range(count):
                category = random.choice(categories)
                quantity = random.randint(0, 100)
                threshold = random.randint(5, 20)

                # Generar custom_data según template
                custom_data = {}
                template_fields = inventory.template.custom_fields

                if isinstance(template_fields, list):
                    for field in template_fields:
                        field_name = field.get('name')
                        field_type = field.get('type')

                        if field_type == 'text':
                            custom_data[field_name] = f'Valor {field_name} {i+1}'
                        elif field_type == 'number':
                            custom_data[field_name] = random.randint(1, 12)
                        elif field_type == 'checkbox':
                            custom_data[field_name] = random.choice([True, False])
                        elif field_type == 'select' and 'options' in field:
                            custom_data[field_name] = random.choice(field['options'])
                        elif field_type == 'date':
                            custom_data[field_name] = '2025-12-31'

                product = Product.objects.create(
                    name=f'Producto {category} {i+1}',
                    sku=f'SKU-{sku_counter:04d}',
                    description=f'Descripción detallada del producto {i+1} de {category}',
                    quantity=quantity,
                    price=Decimal(str(round(random.uniform(5.0, 500.0), 2))),
                    low_stock_threshold=threshold,
                    category=category,
                    inventory=inventory,
                    custom_data=custom_data,
                    is_active=True
                )
                products.append(product)
                sku_counter += 1

        return products

    def create_movements(self, products, users):
        """Crea ~50 movimientos de inventario"""
        movements = []
        movement_types = ['entrada', 'salida', 'ajuste']
        reasons = {
            'entrada': ['Compra a proveedor', 'Devolución cliente', 'Transferencia entre bodegas', 'Inventario inicial'],
            'salida': ['Venta', 'Devolución a proveedor', 'Producto dañado', 'Muestra gratis'],
            'ajuste': ['Corrección de inventario', 'Conteo físico', 'Reconciliación', 'Error de sistema']
        }

        # Seleccionar 50 productos aleatorios
        selected_products = random.sample(products, min(50, len(products)))

        for product in selected_products:
            movement_type = random.choice(movement_types)
            reason = random.choice(reasons[movement_type])

            # Obtener usuario owner del inventario
            user = product.inventory.owner

            # Calcular cantidades
            if movement_type == 'entrada':
                quantity = random.randint(5, 50)
                quantity_before = product.quantity - quantity
                quantity_after = product.quantity
            elif movement_type == 'salida':
                quantity = -random.randint(1, min(10, product.quantity)) if product.quantity > 0 else 0
                quantity_before = product.quantity - quantity
                quantity_after = product.quantity
            else:  # ajuste
                quantity_before = random.randint(0, 100)
                quantity_after = product.quantity
                quantity = quantity_after - quantity_before

            movement = Movement.objects.create(
                product=product,
                movement_type=movement_type,
                quantity=quantity,
                quantity_before=quantity_before,
                quantity_after=quantity_after,
                reason=reason,
                performed_by=user
            )
            movements.append(movement)

        return movements

    def print_summary(self, users, templates, inventories, products, movements):
        """Imprime resumen de los datos creados"""
        self.stdout.write(self.style.SUCCESS('═' * 50))
        self.stdout.write(self.style.SUCCESS('RESUMEN DE DATOS CREADOS'))
        self.stdout.write(self.style.SUCCESS('═' * 50))

        self.stdout.write(f'\n👥 USUARIOS: {len(users)}')
        for user in users:
            self.stdout.write(f'  • {user.email} (Plan: {user.plan})')

        self.stdout.write(f'\n PLANTILLAS: {len(templates)}')
        for template in templates:
            self.stdout.write(f'  • {template.name}')

        self.stdout.write(f'\n INVENTARIOS: {len(inventories)}')
        for inventory in inventories:
            product_count = Product.objects.filter(inventory=inventory).count()
            self.stdout.write(f'  • {inventory.name} ({inventory.owner.name}) - {product_count} productos')

        self.stdout.write(f'\n  PRODUCTOS: {len(products)}')
        low_stock = sum(1 for p in products if p.is_low_stock)
        out_of_stock = sum(1 for p in products if p.is_out_of_stock)
        self.stdout.write(f'  • En stock: {len(products) - low_stock - out_of_stock}')
        self.stdout.write(f'  • Stock bajo: {low_stock}')
        self.stdout.write(f'  • Sin stock: {out_of_stock}')

        self.stdout.write(f'\n MOVIMIENTOS: {len(movements)}')
        entrada = sum(1 for m in movements if m.movement_type == 'entrada')
        salida = sum(1 for m in movements if m.movement_type == 'salida')
        ajuste = sum(1 for m in movements if m.movement_type == 'ajuste')
        self.stdout.write(f'  • Entradas: {entrada}')
        self.stdout.write(f'  • Salidas: {salida}')
        self.stdout.write(f'  • Ajustes: {ajuste}')

        self.stdout.write(self.style.SUCCESS('\n' + '═' * 50))
        self.stdout.write(self.style.SUCCESS('CREDENCIALES DE ACCESO'))
        self.stdout.write(self.style.SUCCESS('═' * 50))
        self.stdout.write('\nTodos los usuarios tienen la contraseña: password123\n')
        self.stdout.write('  • free@example.com (Plan Free)')
        self.stdout.write('  • pro@example.com (Plan Pro)')
        self.stdout.write('  • pro2@example.com (Plan Pro)')
        self.stdout.write('')
