"""
Script de pruebas para la API de Inventarios
Ejecutar: python test_api.py

Este script prueba todos los endpoints creados:
- Autenticación (registro, login, refresh token)
- BusinessTemplates (listar, detalle)
- Inventories (crear, listar, detalle)
- Products (crear, listar, ajustar stock, filtros)
"""

import requests
import json
from pprint import pprint
import sys
import io

# Fix encoding issues on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuración
BASE_URL = 'http://localhost:8000/api'
TEST_USER = {
    'email': 'test_api@test.com',
    'name': 'Test API User',
    'password': 'testpassword123',
    'password2': 'testpassword123'
}

# Variable global para guardar tokens
tokens = {}


def print_section(title):
    """Imprime un título de sección"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_response(response, show_full=False):
    """Imprime la respuesta de una petición"""
    print(f"Status Code: {response.status_code}")

    try:
        data = response.json()
        if show_full:
            print("Response:")
            pprint(data)
        else:
            # Mostrar solo algunos campos clave
            if isinstance(data, dict):
                if 'count' in data and 'results' in data:
                    print(f"Count: {data['count']}")
                    print(f"Results: {len(data['results'])} items")
                    if data['results']:
                        print("First item:")
                        pprint(data['results'][0])
                else:
                    print("Response:")
                    pprint(data)
            elif isinstance(data, list):
                print(f"List with {len(data)} items")
                if data:
                    print("First item:")
                    pprint(data[0])
    except:
        print("Response (raw):", response.text)
    print()


# =============================================================================
# AUTENTICACIÓN
# =============================================================================

def test_register():
    """Prueba el registro de usuario"""
    print_section("1. REGISTRO DE USUARIO")

    url = f"{BASE_URL}/register/"
    response = requests.post(url, json=TEST_USER)
    print_response(response, show_full=True)

    if response.status_code == 201:
        data = response.json()
        tokens['access'] = data['access']
        tokens['refresh'] = data['refresh']
        tokens['token'] = data['token']
        print("[OK] Tokens guardados exitosamente")
        return True
    else:
        print("[WARNING] El usuario puede ya existir, intentando login...")
        return False


def test_login():
    """Prueba el login"""
    print_section("2. LOGIN")

    url = f"{BASE_URL}/login/"
    response = requests.post(url, json={
        'username': TEST_USER['email'],
        'password': TEST_USER['password']
    })
    print_response(response, show_full=True)

    if response.status_code == 200:
        data = response.json()
        tokens['access'] = data['access']
        tokens['refresh'] = data['refresh']
        tokens['token'] = data['token']
        print("[OK] Tokens guardados exitosamente")
        return True
    return False


def test_profile():
    """Prueba obtener el perfil del usuario"""
    print_section("3. PERFIL DE USUARIO")

    url = f"{BASE_URL}/profile/"
    headers = {'Authorization': f"Bearer {tokens['access']}"}
    response = requests.get(url, headers=headers)
    print_response(response, show_full=True)

    return response.status_code == 200


def test_refresh_token():
    """Prueba renovar el access token"""
    print_section("4. RENOVAR ACCESS TOKEN")

    url = f"{BASE_URL}/token/refresh/"
    response = requests.post(url, json={'refresh': tokens['refresh']})
    print_response(response, show_full=True)

    if response.status_code == 200:
        data = response.json()
        tokens['access'] = data['access']
        print("[OK] Access token renovado")
        return True
    return False


# =============================================================================
# BUSINESS TEMPLATES
# =============================================================================

def test_list_templates():
    """Prueba listar plantillas"""
    print_section("5. LISTAR PLANTILLAS DE NEGOCIO")

    url = f"{BASE_URL}/templates/"
    headers = {'Authorization': f"Bearer {tokens['access']}"}
    response = requests.get(url, headers=headers)
    print_response(response)

    return response.status_code == 200


def test_get_template_detail():
    """Prueba obtener detalle de una plantilla"""
    print_section("6. DETALLE DE PLANTILLA")

    # Primero obtenemos la lista para tener un ID
    url = f"{BASE_URL}/templates/"
    headers = {'Authorization': f"Bearer {tokens['access']}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data['results']:
            template_id = data['results'][0]['id']

            # Ahora obtenemos el detalle
            url = f"{BASE_URL}/templates/{template_id}/"
            response = requests.get(url, headers=headers)
            print_response(response, show_full=True)

            # Guardar el ID para usar después
            tokens['template_id'] = template_id
            return response.status_code == 200

    print("[WARNING] No hay plantillas disponibles")
    return False


def test_search_templates():
    """Prueba búsqueda de plantillas"""
    print_section("7. BUSCAR PLANTILLAS")

    url = f"{BASE_URL}/templates/?search=ferretería"
    headers = {'Authorization': f"Bearer {tokens['access']}"}
    response = requests.get(url, headers=headers)
    print_response(response)

    return response.status_code == 200


# =============================================================================
# INVENTARIOS
# =============================================================================

def test_create_inventory():
    """Prueba crear un inventario"""
    print_section("8. CREAR INVENTARIO")

    if 'template_id' not in tokens:
        print("[WARNING] No hay template_id disponible, saltando...")
        return False

    url = f"{BASE_URL}/inventories/"
    headers = {'Authorization': f"Bearer {tokens['access']}"}
    data = {
        'name': 'Inventario de Prueba API',
        'template': tokens['template_id']
    }
    response = requests.post(url, json=data, headers=headers)
    print_response(response, show_full=True)

    if response.status_code == 201:
        inventory_id = response.json()['id']
        tokens['inventory_id'] = inventory_id
        print(f"[OK] Inventario creado con ID: {inventory_id}")
        return True
    return False


def test_list_inventories():
    """Prueba listar inventarios"""
    print_section("9. LISTAR INVENTARIOS")

    url = f"{BASE_URL}/inventories/"
    headers = {'Authorization': f"Bearer {tokens['access']}"}
    response = requests.get(url, headers=headers)
    print_response(response)

    return response.status_code == 200


def test_get_inventory_detail():
    """Prueba obtener detalle de inventario"""
    print_section("10. DETALLE DE INVENTARIO")

    if 'inventory_id' not in tokens:
        print("[WARNING] No hay inventory_id disponible, saltando...")
        return False

    url = f"{BASE_URL}/inventories/{tokens['inventory_id']}/"
    headers = {'Authorization': f"Bearer {tokens['access']}"}
    response = requests.get(url, headers=headers)
    print_response(response, show_full=True)

    return response.status_code == 200


def test_filter_inventories_by_template():
    """Prueba filtrar inventarios por plantilla"""
    print_section("11. FILTRAR INVENTARIOS POR PLANTILLA")

    if 'template_id' not in tokens:
        print("[WARNING] No hay template_id disponible, saltando...")
        return False

    url = f"{BASE_URL}/inventories/?template={tokens['template_id']}"
    headers = {'Authorization': f"Bearer {tokens['access']}"}
    response = requests.get(url, headers=headers)
    print_response(response)

    return response.status_code == 200


# =============================================================================
# PRODUCTOS
# =============================================================================

def test_create_product():
    """Prueba crear un producto"""
    print_section("12. CREAR PRODUCTO")

    if 'inventory_id' not in tokens:
        print("[WARNING] No hay inventory_id disponible, saltando...")
        return False

    url = f"{BASE_URL}/products/"
    headers = {'Authorization': f"Bearer {tokens['access']}"}
    data = {
        'name': 'Producto de Prueba API',
        'sku': 'TEST-API-001',
        'description': 'Este es un producto creado por el script de prueba',
        'quantity': 100,
        'price': 49.99,
        'category': 'Pruebas',
        'inventory': tokens['inventory_id'],
        'custom_data': {
            'marca': 'Test Brand',
            'material': 'Test Material'
        },
        'low_stock_threshold': 20
    }
    response = requests.post(url, json=data, headers=headers)
    print_response(response, show_full=True)

    if response.status_code == 201:
        product_id = response.json()['id']
        tokens['product_id'] = product_id
        print(f"[OK] Producto creado con ID: {product_id}")
        return True
    return False


def test_list_products():
    """Prueba listar productos"""
    print_section("13. LISTAR PRODUCTOS")

    url = f"{BASE_URL}/products/"
    headers = {'Authorization': f"Bearer {tokens['access']}"}
    response = requests.get(url, headers=headers)
    print_response(response)

    return response.status_code == 200


def test_get_product_detail():
    """Prueba obtener detalle de producto"""
    print_section("14. DETALLE DE PRODUCTO")

    if 'product_id' not in tokens:
        print("[WARNING] No hay product_id disponible, saltando...")
        return False

    url = f"{BASE_URL}/products/{tokens['product_id']}/"
    headers = {'Authorization': f"Bearer {tokens['access']}"}
    response = requests.get(url, headers=headers)
    print_response(response, show_full=True)

    return response.status_code == 200


def test_search_products():
    """Prueba búsqueda de productos"""
    print_section("15. BUSCAR PRODUCTOS")

    url = f"{BASE_URL}/products/?search=prueba"
    headers = {'Authorization': f"Bearer {tokens['access']}"}
    response = requests.get(url, headers=headers)
    print_response(response)

    return response.status_code == 200


def test_filter_products_by_inventory():
    """Prueba filtrar productos por inventario"""
    print_section("16. FILTRAR PRODUCTOS POR INVENTARIO")

    if 'inventory_id' not in tokens:
        print("[WARNING] No hay inventory_id disponible, saltando...")
        return False

    url = f"{BASE_URL}/products/?inventory={tokens['inventory_id']}"
    headers = {'Authorization': f"Bearer {tokens['access']}"}
    response = requests.get(url, headers=headers)
    print_response(response)

    return response.status_code == 200


def test_adjust_stock():
    """Prueba ajustar stock de un producto"""
    print_section("17. AJUSTAR STOCK DE PRODUCTO")

    if 'product_id' not in tokens:
        print("[WARNING] No hay product_id disponible, saltando...")
        return False

    # Primero, restamos 10 unidades
    url = f"{BASE_URL}/products/{tokens['product_id']}/adjust_stock/"
    headers = {'Authorization': f"Bearer {tokens['access']}"}
    data = {'adjustment': -10}

    print("Restando 10 unidades...")
    response = requests.post(url, json=data, headers=headers)
    print_response(response, show_full=True)

    if response.status_code != 200:
        return False

    # Luego, sumamos 5 unidades
    data = {'adjustment': 5}
    print("Sumando 5 unidades...")
    response = requests.post(url, json=data, headers=headers)
    print_response(response, show_full=True)

    return response.status_code == 200


def test_filter_low_stock():
    """Prueba filtrar productos con stock bajo"""
    print_section("18. FILTRAR PRODUCTOS CON STOCK BAJO")

    url = f"{BASE_URL}/products/?low_stock=true"
    headers = {'Authorization': f"Bearer {tokens['access']}"}
    response = requests.get(url, headers=headers)
    print_response(response)

    return response.status_code == 200


def test_update_product():
    """Prueba actualizar un producto"""
    print_section("19. ACTUALIZAR PRODUCTO (PATCH)")

    if 'product_id' not in tokens:
        print("[WARNING] No hay product_id disponible, saltando...")
        return False

    url = f"{BASE_URL}/products/{tokens['product_id']}/"
    headers = {'Authorization': f"Bearer {tokens['access']}"}
    data = {
        'description': 'Descripción actualizada por el script de prueba',
        'price': 59.99
    }
    response = requests.patch(url, json=data, headers=headers)
    print_response(response, show_full=True)

    return response.status_code == 200


def test_ordering():
    """Prueba ordenamiento de productos"""
    print_section("20. ORDENAR PRODUCTOS")

    print("Ordenando por precio (ascendente):")
    url = f"{BASE_URL}/products/?ordering=price"
    headers = {'Authorization': f"Bearer {tokens['access']}"}
    response = requests.get(url, headers=headers)
    print_response(response)

    print("\nOrdenando por cantidad (descendente):")
    url = f"{BASE_URL}/products/?ordering=-quantity"
    response = requests.get(url, headers=headers)
    print_response(response)

    return response.status_code == 200


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*80)
    print("  INICIANDO PRUEBAS DE LA API")
    print("="*80)

    results = []

    # Autenticación
    if not test_register():
        if not test_login():
            print("\n[ERROR] No se pudo autenticar. Verifica que el servidor este corriendo.")
            return

    results.append(("Profile", test_profile()))
    results.append(("Refresh Token", test_refresh_token()))

    # Business Templates
    results.append(("List Templates", test_list_templates()))
    results.append(("Template Detail", test_get_template_detail()))
    results.append(("Search Templates", test_search_templates()))

    # Inventarios
    results.append(("Create Inventory", test_create_inventory()))
    results.append(("List Inventories", test_list_inventories()))
    results.append(("Inventory Detail", test_get_inventory_detail()))
    results.append(("Filter Inventories", test_filter_inventories_by_template()))

    # Productos
    results.append(("Create Product", test_create_product()))
    results.append(("List Products", test_list_products()))
    results.append(("Product Detail", test_get_product_detail()))
    results.append(("Search Products", test_search_products()))
    results.append(("Filter Products", test_filter_products_by_inventory()))
    results.append(("Adjust Stock", test_adjust_stock()))
    results.append(("Filter Low Stock", test_filter_low_stock()))
    results.append(("Update Product", test_update_product()))
    results.append(("Ordering", test_ordering()))

    # Resumen
    print_section("RESUMEN DE PRUEBAS")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print("Resultados:\n")
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} - {test_name}")

    print(f"\n{'='*80}")
    print(f"  Total: {passed}/{total} pruebas pasaron")
    print(f"{'='*80}\n")

    if passed == total:
        print("EXITO: Todas las pruebas pasaron exitosamente!")
    else:
        print(f"ADVERTENCIA: {total - passed} prueba(s) fallaron")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n\nError inesperado: {e}")
        import traceback
        traceback.print_exc()
