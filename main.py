# from fastapi import FastAPI, Request, Form
# from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# import requests
# import json

# app = FastAPI()

# # Configurar la carpeta de plantillas
# templates = Jinja2Templates(directory="templates")

# def connect_to_api(url, token):
#     headers = {
#         "Authorization": f"Bearer {token}"
#     }
#     try:
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
#         try:
#             return response.json()
#         except json.JSONDecodeError as e:
#             print(f"Failed to decode JSON: {e}")
#             return None
#     except requests.exceptions.RequestException as e:
#         print(f"Request failed: {e}")
#         return None

# # Ruta para el login
# @app.get("/", response_class=HTMLResponse)
# async def login_page(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

# @app.post("/login", response_class=RedirectResponse)
# async def login(username: str = Form(...), password: str = Form(...)):
#     # Validar credenciales (usuario: user, contraseña: user)
#     if username == "user" and password == "user":
#         return RedirectResponse(url="/dashboard", status_code=303)
#     else:
#         # Mostrar mensaje de error si las credenciales son incorrectas
#         return templates.TemplateResponse("login.html", {"request": {}, "error": "Credenciales incorrectas"})

# @app.get("/dashboard", response_class=HTMLResponse)
# async def dashboard(request: Request):
#     # Datos dinámicos para el dashboard
#     areas = [
#         {"name": "Lobby", "completed": 24, "pending": 3, "rating": 92, "frequency": 5},
#         {"name": "Piso 1", "completed": 18, "pending": 6, "rating": 87, "frequency": 4},
#         {"name": "Baños", "completed": 35, "pending": 2, "rating": 95, "frequency": 7},
#         {"name": "Áreas comunes", "completed": 40, "pending": 5, "rating": 90, "frequency": 6},
#     ]

#     # Renderizar la plantilla del dashboard
#     return templates.TemplateResponse("dashboard.html", {"request": request, "areas": areas})

# @app.get("/process", response_class=JSONResponse)
# async def process_data():
#     api_url = "https://api.safetyculture.io/audits/audit_7c70c888a4e04babb8f0a1a623af3fee"
#     bearer_token = "d7c73830bece5d65ccd55ed048439ecb38f483ee84c82dc61d5ee8594effb5cb"

#     data = connect_to_api(api_url, bearer_token)
#     accountable_response = "Si"

#     if data:
#         # Extraer datos relevantes
#         header_items = data.get("header_items", [])
#         items = data.get("items", [])

#         # Combinar header_items e items
#         combined_items = header_items + items

#         # Crear un diccionario para acceso rápido
#         combined_items_dict = {item["item_id"]: item for item in combined_items}

#         # Procesar cada sección
#         for item in combined_items:
#             if item.get("type") == "section":
#                 item["frecuencias"] = []
#                 item["servicios_total_area"] = 0
#                 item["servicios_terminados_area"] = 0

#                 # Buscar preguntas asociadas
#                 for data_item in items:
#                     if data_item.get("parent_id") == item["item_id"] and data_item.get("type") == "question":
#                         frecuencia = {
#                             "item_id": data_item["item_id"],
#                             "label": data_item["label"],
#                             "servicios_frecuencia_total": 0,
#                             "servicios_frecuencia_terminada": 0,
#                             "grand_children_data": []
#                         }

#                         # Procesar hijos de la pregunta
#                         children = data_item.get("children", [])
#                         for child_id in children:
#                             grand_child = combined_items_dict.get(child_id, {})
#                             if grand_child.get("type") == "question":
#                                 grand_child_data = {
#                                     "item_id": grand_child.get("item_id"),
#                                     "label": grand_child.get("label"),
#                                     "type": grand_child.get("type")
#                                 }
#                                 # Verificar respuestas seleccionadas
#                                 responses = grand_child.get("responses", {}).get("selected", [])
#                                 if responses:
#                                     grand_child_data["response"] = responses[0].get("label")
#                                     if grand_child_data["response"] == accountable_response:
#                                         frecuencia["servicios_frecuencia_terminada"] += 1
#                                 frecuencia["grand_children_data"].append(grand_child_data)
#                                 frecuencia["servicios_frecuencia_total"] += 1

#                         # Actualizar totales de la sección
#                         item["frecuencias"].append(frecuencia)
#                         item["servicios_total_area"] += frecuencia["servicios_frecuencia_total"]
#                         item["servicios_terminados_area"] += frecuencia["servicios_frecuencia_terminada"]

#         # Guardar los datos procesados en un archivo JSON
#         with open("output.json", "w") as outfile:
#             json.dump(combined_items, outfile, indent=4)
#         return {"message": "Datos procesados y guardados en output.json", "data": combined_items}
#     else:
#         return {"error": "Failed to retrieve data from the API"}

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import requests
import json
from typing import List, Dict, Optional

app = FastAPI()

# Configurar la carpeta de plantillas
templates = Jinja2Templates(directory="templates")

def connect_to_api(url: str, token: str) -> Optional[dict]:
    """
    Realiza una petición GET a la API con el token de autenticación.

    Args:
        url: La URL de la API.
        token: El token de autenticación Bearer.

    Returns:
        El JSON de la respuesta de la API como un diccionario, o None si hay un error.
    """
    headers = {
        "Authorization": f"Bearer {token}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP 4xx o 5xx
        try:
            return response.json()
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}, texto de la respuesta: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición: {e}")
        return None

def calculate_completion_data(items: List[dict]) -> Dict[str, int]:
    """
    Calcula la cantidad de tareas completadas y pendientes a partir de la lista de items.

    Args:
        items: Una lista de diccionarios, donde cada diccionario representa un item del audit.

    Returns:
        Un diccionario con las claves "completed" y "pending", y sus respectivos valores enteros.
    """
    completed = 0
    pending = 0
    for item in items:
        # Aquí habría que refinar la lógica según como se indica que una tarea está completa
        # Esto es un ejemplo, y puede variar mucho dependiendo de la estructura real del JSON
        if item.get("type") == "question":
            responses = item.get("responses", {})
            if responses: # Si hay alguna respuesta
                if responses.get("selected"): # Si la pregunta fue respondida
                  completed += 1
                else:
                    pending += 1
            else:
                pending += 1 # Si no hay respuestas se asume pendiente
    return {"completed": completed, "pending": pending}

def calculate_rating(items: List[dict]) -> Optional[float]:
    """
    Calcula el rating o calidad del servicio basado en los scores de las preguntas.

    Args:
        items: Una lista de diccionarios, donde cada diccionario representa un item del audit.

    Returns:
        El rating promedio como un float, o None si no hay datos de score disponibles.
    """
    total_score = 0
    max_total_score = 0
    score_items_count = 0 # Cantidad de items que tienen score
    
    for item in items:
        if item.get("type") == "question" and item.get("scoring"):
            score = item["scoring"].get("score", None)
            max_score = item["scoring"].get("max_score", None)
            if score is not None and max_score is not None:
                total_score += score
                max_total_score += max_score
                score_items_count += 1

    if score_items_count > 0:
        return (total_score / max_total_score) * 100 if max_total_score else 0
    else:
        return None
    
def calculate_frequency(items: List[dict]) -> int:
    """
    Calcula la frecuencia del servicio, contando el número de items de tipo pregunta.
    Args:
        items: lista de items
    Return:
        Cantidad de preguntas
    """
    frequency = 0
    for item in items:
        if item.get("type") == "question":
            frequency+=1
    return frequency

def process_audit_data(audit_data: dict) -> List[dict]:
    """
    Procesa los datos del audit para extraer la información necesaria para el dashboard.

    Args:
        audit_data: El diccionario con los datos del audit obtenidos de la API.

    Returns:
        Una lista de diccionarios, donde cada diccionario representa un área con su información resumida.
    """
    areas_data = []
    items = audit_data.get("items", [])
    
    # Crear un diccionario para acceder a los items por ID de forma eficiente
    item_dict = {item["item_id"]: item for item in items}

    # Procesar las secciones principales
    for item in items:
        if item.get("type") == "section" and item.get("parent_id") is None: #Secciones de nivel superior
            area_name = item.get("label", "Sin nombre")
            # Recolectar todos los items que pertenecen a esta sección, incluyendo nietos
            section_items = []
            
            def collect_section_items(item_id, visited_ids=set()):
                """
                Función recursiva para recolectar items de la sección, evitando la recursión infinita.
                """
                if item_id in visited_ids:
                    return  # Ya hemos visitado este item, evitar bucles
                visited_ids.add(item_id) # Agregar el item actual a visitados
                
                direct_children_ids = item.get("children", [])
                for child_id in direct_children_ids:
                    child_item = item_dict.get(child_id)
                    if child_item:
                        section_items.append(child_item)
                        if child_item.get("children"):
                            collect_section_items(child_item["item_id"], visited_ids) # Recursión para nietos
            
            collect_section_items(item["item_id"])
            
            completion_data = calculate_completion_data(section_items)
            rating = calculate_rating(section_items)
            frequency = calculate_frequency(section_items)
            
            areas_data.append({
                "name": area_name,
                "completed": completion_data["completed"],
                "pending": completion_data["pending"],
                "rating": rating if rating is not None else 0,  # Usar 0 si no hay rating
                "frequency": frequency
            })
            
    return areas_data

# Ruta para el login
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=RedirectResponse)
async def login(username: str = Form(...), password: str = Form(...)):
    # Validar credenciales (usuario: user, contraseña: user)
    if username == "user" and password == "user":
        return RedirectResponse(url="/dashboard", status_code=303)
    else:
        # Mostrar mensaje de error si las credenciales son incorrectas
        return templates.TemplateResponse("login.html", {"request": {}, "error": "Credenciales incorrectas"})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    # Datos dinámicos para el dashboard
    api_url = "https://api.safetyculture.io/audits/audit_7c70c888a4e04babb8f0a1a623af3fee"
    bearer_token = "d7c73830bece5d65ccd55ed048439ecb38f483ee84c82dc61d5ee8594effb5cb"

    audit_data = connect_to_api(api_url, bearer_token)
    if audit_data:
        areas_data = process_audit_data(audit_data)
        # Renderizar la plantilla del dashboard
        return templates.TemplateResponse("dashboard.html", {"request": request, "areas": areas_data})
    else:
        return templates.TemplateResponse("dashboard.html", {"request": request, "error": "No se pudieron obtener los datos del auditorio"})

@app.get("/process", response_class=JSONResponse)
async def process_data():
    api_url = "https://api.safetyculture.io/audits/audit_7c70c888a4e04babb8f0a1a623af3fee"
    bearer_token = "d7c73830bece5d65ccd55ed048439ecb38f483ee84c82dc61d5ee8594effb5cb"

    data = connect_to_api(api_url, bearer_token)

    if data:
        processed_data = process_audit_data(data)
        # Guardar los datos procesados en un archivo JSON
        with open("output.json", "w") as outfile:
            json.dump(processed_data, outfile, indent=4)
        return {"message": "Datos procesados y guardados en output.json", "data": processed_data}
    else:
        return {"error": "Failed to retrieve data from the API"}


