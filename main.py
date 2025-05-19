
# from fastapi import FastAPI, Request, Form
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
# from typing import Annotated
# import plotly.express as px
# import pandas as pd
# import requests

# app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")

# # Usuario y contraseña por defecto
# DEFAULT_USER = "usuario_demo"
# DEFAULT_PASSWORD = "contrasena_demo_segura"

# # Token de autorización (¡Mantén esto seguro!)
# API_TOKEN = "d7c73830bece5d65ccd55ed048439ecb38f483ee84c82dc61d5ee8594effb5cb"  # Reemplaza con tu token real
# API_URL = "https://api.safetyculture.io/audits/audit_7c70c888a4e04babb8f0a1a623af3fee"

# # Función para obtener los datos del endpoint
# def fetch_audit_data():
#     headers = {
#         "Authorization": f"Bearer {API_TOKEN}",
#         "Content-Type": "application/json"
#     }
#     try:
#         response = requests.get(API_URL, headers=headers)
#         response.raise_for_status()  # Lanza una excepción si la respuesta tiene un código de error
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         print(f"Error al obtener datos de la API: {e}")
#         return []

# @app.get("/", response_class=HTMLResponse)
# async def read_root(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

# @app.post("/login", response_class=HTMLResponse)
# async def login(request: Request, username: Annotated[str, Form()], password: Annotated[str, Form()]):
#     if username == DEFAULT_USER and password == DEFAULT_PASSWORD:
#         audit_data = fetch_audit_data()
#         return templates.TemplateResponse("dashboard.html", {"request": request, "audit_data": audit_data})
#     else:
#         return templates.TemplateResponse("login.html", {"request": request, "error": "Credenciales incorrectas"})

# @app.get("/dashboard", response_class=HTMLResponse)
# async def dashboard(request: Request):
#     audit_data = fetch_audit_data()
#     return templates.TemplateResponse("dashboard.html", {"request": request, "audit_data": audit_data})

# @app.get("/reportes")
# async def reportes():
#     # Conectar a la API para obtener los datos
#     data = fetch_audit_data()

#     if not data:
#         return {"error": "No se pudieron obtener los datos de la API"}

#     # Procesar los datos obtenidos de la API para secciones y sus scores
#     section_labels = []
#     section_scores = []

#     for item in data.get("items", []):
#         if item.get("type") == "section" and item.get("scoring"):
#             section_labels.append(item.get("label", "Sin etiqueta"))
#             section_scores.append(item.get("scoring").get("combined_score_percentage", 0))

#     # Devolver los datos procesados para graficar
#     return {
#         "section_labels": section_labels,
#         "section_scores": section_scores
#     }

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Annotated
import plotly.express as px
import pandas as pd
import requests

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Usuario y contraseña por defecto
DEFAULT_USER = "user"
DEFAULT_PASSWORD = "user"

# Token de autorización (¡Mantén esto seguro!)
API_TOKEN = "d7c73830bece5d65ccd55ed048439ecb38f483ee84c82dc61d5ee8594effb5cb"  # Reemplaza con tu token real
API_URL = "https://api.safetyculture.io/audits/audit_7c70c888a4e04babb8f0a1a623af3fee"

# Función para obtener los datos del endpoint
def fetch_audit_data():
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()  # Lanza una excepción si la respuesta tiene un código de error
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener datos de la API: {e}")
        return []

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: Annotated[str, Form()], password: Annotated[str, Form()]):
    if username == DEFAULT_USER and password == DEFAULT_PASSWORD:
        return templates.TemplateResponse("dashboard.html", {"request": request})  # No necesitamos pasar audit_data aquí
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Credenciales incorrectas"})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})  # No necesitamos pasar audit_data aquí, se obtiene en /reportes

@app.get("/reportes")
async def reportes():
    # Conectar a la API para obtener los datos
    data = fetch_audit_data()

    if not data:
        return {"error": "No se pudieron obtener los datos de la API"}

    # Procesar los datos obtenidos de la API para secciones y sus scores
    section_labels = []
    section_scores = []

    for item in data.get("items", []):
        if item.get("type") == "section" and item.get("scoring"):
            section_labels.append(item.get("label", "Sin etiqueta"))
            section_scores.append(item.get("scoring").get("combined_score_percentage", 0))

    # Devolver los datos procesados para graficar
    return {
        "section_labels": section_labels,
        "section_scores": section_scores
    }