"""
Script de pruebas para validar el Día 7 - CRUD de Inventarios
Ejecutar: python test_day7_inventories.py

Este script valida:
- ✅ GET /api/inventories/ (lista inventarios del usuario actual)
- ✅ POST /api/inventories/ (crear nuevo, requiere name + template_id)
- ✅ GET /api/inventories/{id}/ (detalle)
- ✅ PUT /api/inventories/{id}/ (editar nombre)
- ✅ DELETE /api/inventories/{id}/ (eliminar)
- ✅ Filtrado por usuario: solo ve sus propios inventarios
- ✅ Validaciones: template debe existir, errores apropiados
"""

import requests
import json
import sys
import io

# Fix encoding issues on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = 'http://localhost:8000/api'

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.YELLOW}→ {text}{Colors.RESET}")

def print_test(text):
    print(f"\n{Colors.BOLD}TEST: {text}{Colors.RESET}")

# Variables globales
user1_token = None
user2_token = None
template_id = None
inventory_id = None

def create_test_user(email, name, password):
    """Crea un usuario de prueba"""
    response = requests.post(f"{BASE_URL}/register/", json={
        'email': email,
        'name': name,
        'password': password,
        'password2': password
    })

    if response.status_code == 201:
        data = response.json()
        return data['access']
    elif response.status_code == 400:
        # Usuario ya existe, hacer login
        response = requests.post(f"{BASE_URL}/login/", json={
            'username': email,
            'password': password
        })
        if response.status_code == 200:
            return response.json()['access']
    return None

def get_first_template(token):
    """Obtiene el ID de la primera plantilla disponible"""
    response = requests.get(f"{BASE_URL}/templates/",
                           headers={'Authorization': f'Bearer {token}'})
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results'][0]['id']
    return None

# =============================================================================
# TESTS
# =============================================================================

def test_01_setup():
    """Setup: Crear usuarios y obtener tokens"""
    global user1_token, user2_token, template_id

    print_test("Setup - Crear usuarios de prueba")

    user1_token = create_test_user('user1_day7@test.com', 'User 1', 'password123')
    if user1_token:
        print_success("Usuario 1 creado/autenticado")
    else:
        print_error("No se pudo crear Usuario 1")
        return False

    user2_token = create_test_user('user2_day7@test.com', 'User 2', 'password123')
    if user2_token:
        print_success("Usuario 2 creado/autenticado")
    else:
        print_error("No se pudo crear Usuario 2")
        return False

    template_id = get_first_template(user1_token)
    if template_id:
        print_success(f"Template ID obtenido: {template_id}")
    else:
        print_error("No hay templates disponibles. Crea uno desde el admin.")
        return False

    return True

def test_02_create_inventory():
    """POST /api/inventories/ - Crear inventario"""
    global inventory_id

    print_test("Crear un nuevo inventario")

    data = {
        'name': 'Inventario de Prueba Día 7',
        'template': template_id
    }

    response = requests.post(f"{BASE_URL}/inventories/",
                            json=data,
                            headers={'Authorization': f'Bearer {user1_token}'})

    print_info(f"Status Code: {response.status_code}")

    if response.status_code == 201:
        result = response.json()
        inventory_id = result['id']
        print_success(f"Inventario creado exitosamente (ID: {inventory_id})")
        print_info(f"Nombre: {result['name']}")
        print_info(f"Owner: {result['owner_name']}")
        # En DetailSerializer viene template_data completo, en ListSerializer viene template_name
        if 'template_data' in result:
            print_info(f"Template: {result['template_data']['name']}")
        elif 'template_name' in result:
            print_info(f"Template: {result['template_name']}")
        return True
    else:
        print_error(f"Error al crear inventario: {response.text}")
        return False

def test_03_list_inventories_user1():
    """GET /api/inventories/ - Listar inventarios del Usuario 1"""
    print_test("Listar inventarios del Usuario 1")

    response = requests.get(f"{BASE_URL}/inventories/",
                           headers={'Authorization': f'Bearer {user1_token}'})

    print_info(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_success(f"Inventarios obtenidos: {data['count']}")

        if data['count'] > 0:
            for inv in data['results']:
                print_info(f"  - ID: {inv['id']}, Nombre: {inv['name']}, Owner: {inv['owner_name']}")
        return True
    else:
        print_error(f"Error al listar inventarios: {response.text}")
        return False

def test_04_get_inventory_detail():
    """GET /api/inventories/{id}/ - Obtener detalle de inventario"""
    print_test("Obtener detalle del inventario creado")

    response = requests.get(f"{BASE_URL}/inventories/{inventory_id}/",
                           headers={'Authorization': f'Bearer {user1_token}'})

    print_info(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_success("Detalle obtenido exitosamente")
        print_info(f"ID: {data['id']}")
        print_info(f"Nombre: {data['name']}")
        print_info(f"Template: {data['template_data']['name']}")
        print_info(f"Custom Fields: {len(data['template_data']['custom_fields'])} campos")
        return True
    else:
        print_error(f"Error al obtener detalle: {response.text}")
        return False

def test_05_update_inventory_put():
    """PUT /api/inventories/{id}/ - Actualizar inventario completo"""
    print_test("Actualizar inventario (PUT - actualización completa)")

    data = {
        'name': 'Inventario Actualizado PUT',
        'template': template_id
    }

    response = requests.put(f"{BASE_URL}/inventories/{inventory_id}/",
                           json=data,
                           headers={'Authorization': f'Bearer {user1_token}'})

    print_info(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print_success("Inventario actualizado exitosamente")
        print_info(f"Nombre anterior: 'Inventario de Prueba Día 7'")
        print_info(f"Nombre nuevo: '{result['name']}'")
        return True
    else:
        print_error(f"Error al actualizar: {response.text}")
        return False

def test_06_update_inventory_patch():
    """PATCH /api/inventories/{id}/ - Actualizar parcialmente"""
    print_test("Actualizar inventario (PATCH - actualización parcial)")

    data = {
        'name': 'Inventario Actualizado PATCH'
    }

    response = requests.patch(f"{BASE_URL}/inventories/{inventory_id}/",
                             json=data,
                             headers={'Authorization': f'Bearer {user1_token}'})

    print_info(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print_success("Inventario actualizado exitosamente")
        print_info(f"Nuevo nombre: '{result['name']}'")
        return True
    else:
        print_error(f"Error al actualizar: {response.text}")
        return False

def test_07_user2_cannot_see_user1_inventory():
    """Validar que Usuario 2 NO puede ver inventarios de Usuario 1"""
    print_test("Validar aislamiento: Usuario 2 no debe ver inventario de Usuario 1")

    # Usuario 2 intenta listar inventarios
    response = requests.get(f"{BASE_URL}/inventories/",
                           headers={'Authorization': f'Bearer {user2_token}'})

    print_info(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        # Buscar si el inventario de User1 está en la lista de User2
        found = False
        for inv in data['results']:
            if inv['id'] == inventory_id:
                found = True
                break

        if not found:
            print_success(f"✓ Usuario 2 NO ve el inventario de Usuario 1 (correcto)")
            print_info(f"Usuario 2 tiene {data['count']} inventario(s) propio(s)")
            return True
        else:
            print_error("✗ Usuario 2 puede ver inventario de Usuario 1 (ERROR)")
            return False
    else:
        print_error(f"Error al listar: {response.text}")
        return False

def test_08_user2_cannot_access_user1_inventory():
    """Validar que Usuario 2 NO puede acceder al detalle del inventario de Usuario 1"""
    print_test("Validar que Usuario 2 no puede acceder directamente al inventario")

    response = requests.get(f"{BASE_URL}/inventories/{inventory_id}/",
                           headers={'Authorization': f'Bearer {user2_token}'})

    print_info(f"Status Code: {response.status_code}")

    if response.status_code == 404:
        print_success("✓ Usuario 2 recibe 404 al intentar acceder (correcto)")
        return True
    elif response.status_code == 403:
        print_success("✓ Usuario 2 recibe 403 Forbidden (correcto)")
        return True
    else:
        print_error(f"✗ Usuario 2 recibió código inesperado: {response.status_code}")
        return False

def test_09_user2_cannot_edit_user1_inventory():
    """Validar que Usuario 2 NO puede editar inventario de Usuario 1"""
    print_test("Validar que Usuario 2 no puede editar inventario de Usuario 1")

    data = {'name': 'Intento de Hackeo'}

    response = requests.patch(f"{BASE_URL}/inventories/{inventory_id}/",
                             json=data,
                             headers={'Authorization': f'Bearer {user2_token}'})

    print_info(f"Status Code: {response.status_code}")

    if response.status_code in [404, 403]:
        print_success(f"✓ Usuario 2 recibe {response.status_code} al intentar editar (correcto)")
        return True
    else:
        print_error(f"✗ Usuario 2 pudo editar el inventario (ERROR GRAVE)")
        return False

def test_10_create_inventory_invalid_template():
    """Validar error al crear inventario con template inexistente"""
    print_test("Validar error con template_id inexistente")

    data = {
        'name': 'Inventario con Template Inválido',
        'template': 99999  # ID que no existe
    }

    response = requests.post(f"{BASE_URL}/inventories/",
                            json=data,
                            headers={'Authorization': f'Bearer {user1_token}'})

    print_info(f"Status Code: {response.status_code}")

    if response.status_code == 400:
        print_success("✓ Recibe 400 Bad Request al usar template inválido (correcto)")
        print_info(f"Error: {response.json()}")
        return True
    else:
        print_error(f"✗ Debería recibir 400, pero recibió {response.status_code}")
        return False

def test_11_create_inventory_without_auth():
    """Validar que se requiere autenticación"""
    print_test("Validar que se requiere autenticación")

    data = {
        'name': 'Inventario sin Auth',
        'template': template_id
    }

    response = requests.post(f"{BASE_URL}/inventories/", json=data)

    print_info(f"Status Code: {response.status_code}")

    if response.status_code == 401:
        print_success("✓ Recibe 401 Unauthorized sin token (correcto)")
        return True
    else:
        print_error(f"✗ Debería recibir 401, pero recibió {response.status_code}")
        return False

def test_12_delete_inventory():
    """DELETE /api/inventories/{id}/ - Eliminar inventario"""
    print_test("Eliminar inventario")

    response = requests.delete(f"{BASE_URL}/inventories/{inventory_id}/",
                              headers={'Authorization': f'Bearer {user1_token}'})

    print_info(f"Status Code: {response.status_code}")

    if response.status_code == 204:
        print_success("✓ Inventario eliminado exitosamente")

        # Verificar que ya no existe
        response = requests.get(f"{BASE_URL}/inventories/{inventory_id}/",
                               headers={'Authorization': f'Bearer {user1_token}'})

        if response.status_code == 404:
            print_success("✓ Confirmado: inventario ya no existe")
            return True
        else:
            print_error("✗ El inventario aún existe después de eliminarlo")
            return False
    else:
        print_error(f"Error al eliminar: {response.text}")
        return False

# =============================================================================
# MAIN
# =============================================================================

def main():
    print_header("PRUEBAS DÍA 7 - CRUD DE INVENTARIOS")

    tests = [
        ("01. Setup inicial", test_01_setup),
        ("02. Crear inventario", test_02_create_inventory),
        ("03. Listar inventarios", test_03_list_inventories_user1),
        ("04. Detalle de inventario", test_04_get_inventory_detail),
        ("05. Actualizar (PUT)", test_05_update_inventory_put),
        ("06. Actualizar (PATCH)", test_06_update_inventory_patch),
        ("07. Aislamiento: User2 no lista inv User1", test_07_user2_cannot_see_user1_inventory),
        ("08. Aislamiento: User2 no accede a detalle", test_08_user2_cannot_access_user1_inventory),
        ("09. Aislamiento: User2 no puede editar", test_09_user2_cannot_edit_user1_inventory),
        ("10. Validar template inválido", test_10_create_inventory_invalid_template),
        ("11. Validar autenticación requerida", test_11_create_inventory_without_auth),
        ("12. Eliminar inventario", test_12_delete_inventory),
    ]

    results = []

    print_info("Asegúrate de que el servidor Django esté corriendo en localhost:8000\n")

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Excepción en {name}: {str(e)}")
            results.append((name, False))

    # Resumen
    print_header("RESUMEN DE RESULTADOS")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{Colors.GREEN}[PASS]{Colors.RESET}" if result else f"{Colors.RED}[FAIL]{Colors.RESET}"
        print(f"{status} {name}")

    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    percentage = (passed / total * 100) if total > 0 else 0
    print(f"{Colors.BOLD}Total: {passed}/{total} pruebas pasaron ({percentage:.1f}%){Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")

    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}¡ÉXITO! Día 7 completado correctamente{Colors.RESET}")
        print(f"{Colors.GREEN}✓ Todos los criterios de aceptación cumplidos{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}HAY ERRORES: {total - passed} prueba(s) fallaron{Colors.RESET}\n")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Pruebas interrumpidas por el usuario{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}Error inesperado: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
