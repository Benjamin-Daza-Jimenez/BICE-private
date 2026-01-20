import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()
def limpiar_texto_jira(nodo):
    """Convierte el formato complejo de Jira (ADF) en texto simple."""
    if not nodo:
        return ""
    if isinstance(nodo, str):
        return nodo
    
    if isinstance(nodo, dict):
        texto_acumulado = []
        
        if nodo.get("type") == "text":
            return nodo.get("text", "")
        
        hijos = nodo.get("content", [])
        for hijo in hijos:
            texto_hijo = limpiar_texto_jira(hijo)
            if texto_hijo:
                texto_acumulado.append(texto_hijo)
        
        separador = "\n" if nodo.get("type") == "paragraph" else " "
        return separador.join(texto_acumulado).strip()
    
    return ""

def jira_get():
    auth = HTTPBasicAuth(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))
    url = f"https://{os.getenv('JIRA_DOMAIN')}/rest/api/3/search/jql"

    all_issues = []
    next_token = None 

    print("--- Iniciando descarga por Tokens ---")

    while True:
        params = {
            "jql": "project = GDI",
            "maxResults": 100,
            "fields": "issuetype,key,summary,priority,customfield_10298,customfield_10270,customfield_10271,customfield_10278,customfield_10126,customfield_10323,description,customfield_10446,customfield_10445,customfield_10321"
        }
        
        if next_token:
            params["nextPageToken"] = next_token

        response = requests.get(url, auth=auth, params=params)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            break

        data = response.json()
        issues = data.get("issues", [])
        all_issues.extend(issues)
        
        print(f"Acumulados: {len(all_issues)} registros...")

        next_token = data.get("nextPageToken")
        is_last = data.get("isLast", True)

        if is_last or not next_token:
            print("--- Fin de la descarga ---")
            break

    datos = []
    for item in all_issues:
        f = item.get("fields", {})
        activos_lista = f.get("customfield_10126")
        if isinstance(activos_lista, list):
            activos_unidos = "; ".join([a.get("value") for a in activos_lista if a.get("value")])
        else:
            activos_unidos = None

        datos.append({
                "Resumen": f.get("summary"),
                "Prioridad": f.get("priority", {}).get("name"),
                "Equipo Resolutor": f.get("customfield_10298").get("value") if f.get("customfield_10298") else None,
                "Fecha Real Incidente": f.get("customfield_10270"),
                "Fecha Resolución Real Incidente": f.get("customfield_10271"),
                "Duración Incidente": f.get("customfield_10278"),
                "Activo de SW": activos_unidos,
                "Servicio Reportado": f.get("customfield_10323").get("value") if f.get("customfield_10323") else None,
                "Descripción": limpiar_texto_jira(f.get("description")),
                "Causa Raíz / Origen": limpiar_texto_jira(f.get("customfield_10446")),
                "Descripción de la Solución:": limpiar_texto_jira(f.get("customfield_10445")),
                "Resuelto con:": f.get("customfield_10321").get("value") if f.get("customfield_10321") else None,
            })
        
    df = pd.DataFrame(datos)
    return df
