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

def get_worksheet(sheet_name="Melaminas"):
    """Autentica y devuelve el objeto de la hoja de cálculo específica por nombre."""
    if not SPREADSHEET_ID:
        raise ValueError("No se encontró SPREADSHEET_ID en el archivo .env")
        
    creds_json_str = os.getenv("GOOGLE_CREDS_JSON")
    if creds_json_str:
        creds_info = json.loads(creds_json_str)
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
        
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)

def get_sheet():
    """Para retrocompatibilidad, devuelve por defecto la hoja de Melaminas."""
    return get_worksheet("Melaminas")

def generate_id(prefix="M-"):
    """Genera un código corto y único para la pieza, ej: M-A32 o C-A32"""
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" # Sin I, O, 1, 0
    return prefix + ''.join(random.choices(chars, k=3))

def add_piece(medidas, color, grosor, veta, foto_url):
    """
    Añade una nueva pieza al inventario de Google Sheets (Melaminas).
    Devuelve el ID corto generado para que el operario lo anote.
    """
    sheet = get_worksheet("Melaminas")
    piece_id = generate_id("M-")
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Columnas Melaminas: ID, Color, Grosor, Medidas, Veta, Foto, Estado, Date
    row = [piece_id, color, grosor, medidas, veta, foto_url, "DISPONIBLE", fecha]
    sheet.append_row(row)
    
    return piece_id

import math

def add_canto(nombre, diametro_ext, diametro_int, grosor, ancho, foto_url):
    """
    Calcula los metros lineales de un canto e inserta el registro en Google Sheets.
    """
    sheet = get_worksheet("CANTOS")
    piece_id = generate_id("C-")
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Cálculo matemático de metros lineales (ML)
    # Fórmula: L(m) = [π * ((De/2)² - (Di/2)²)] / grosor / 1000
    R = diametro_ext / 2.0
    r = diametro_int / 2.0
    longitud_mm = (math.pi * ((R**2) - (r**2))) / grosor
    ml_total = round(longitud_mm / 1000.0, 2)
    
    # Formatear números a string con coma para visualización si es necesario
    ml_str = str(ml_total).replace('.', ',')
    grosor_str = str(grosor).replace('.', ',')
    
    # Columnas CANTOS: ID, NOMBRE, ML, GRS, ANCHO, FOTO REF, ESTADO, DATE
    row = [piece_id, nombre, ml_str, grosor_str, ancho, foto_url, "DISPONIBLE", fecha]
    sheet.append_row(row)
    
    return piece_id, ml_total

def use_piece(piece_id):
    """
    Busca la pieza por su ID corto y la marca como 'USADA'.
    Retorna True si fue exitoso, False si no existe el ID.
    Determina la hoja automáticamente según el prefijo (M- o C-).
    """
    piece_id = piece_id.strip().upper() 
    
    # Detectar en qué hoja buscar
    if piece_id.startswith("C-"):
        sheet_name = "CANTOS"
        estado_col = 7 # G
    else:
        sheet_name = "Melaminas"
        estado_col = 7 # G
        
    sheet = get_worksheet(sheet_name)
    
    try:
        # Buscar el piece_id en la columna 1 (A)
        cell = sheet.find(piece_id, in_column=1)
        if cell is None:
            return False
            
        # Actualizar el estado en la columna a "USADO"
        sheet.update_cell(cell.row, estado_col, "USADO")
        return True
    except Exception as e:
        if "CellNotFound" in str(type(e)):
            return False
        raise

