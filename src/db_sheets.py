import os
import datetime
import random
import string
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Cargar variables de entorno (como el SPREADSHEET_ID)
load_dotenv()
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

import json

def get_sheet():
    """Autentica y devuelve el objeto de la hoja de cálculo principal."""
    if not SPREADSHEET_ID:
        raise ValueError("No se encontró SPREADSHEET_ID en el archivo .env")
        
    creds_json_str = os.getenv("GOOGLE_CREDS_JSON")
    if creds_json_str:
        creds_info = json.loads(creds_json_str)
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
        
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).sheet1

def generate_id():
    """Genera un código corto y único para la pieza, ej: M-A32"""
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" # Sin I, O, 1, 0
    return "M-" + ''.join(random.choices(chars, k=3))

def add_piece(medidas, color, grosor, veta, foto_url):
    """
    Añade una nueva pieza al inventario de Google Sheets.
    Devuelve el ID corto generado para que el operario lo anote.
    """
    sheet = get_sheet()
    piece_id = generate_id()
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Nuevo orden de las columnas: ID, Color, Grosor, Medidas, Veta, Foto, Estado, Date
    row = [piece_id, color, grosor, medidas, veta, foto_url, "DISPONIBLE", fecha]
    sheet.append_row(row)
    
    return piece_id

def use_piece(piece_id):
    """
    Busca la pieza por su ID corto y la marca como 'USADA'.
    Retorna True si fue exitoso, False si no existe el ID.
    """
    sheet = get_sheet()
    piece_id = piece_id.upper() 
    try:
        # Buscar el piece_id en la columna 1 (A)
        cell = sheet.find(piece_id, in_column=1)
        if cell is None:
            return False
            
        # Actualizar el estado en la columna 7 (G) a "USADO"
        sheet.update_cell(cell.row, 7, "USADO")
        return True
    except Exception as e:
        if "CellNotFound" in str(type(e)):
            return False
        raise
