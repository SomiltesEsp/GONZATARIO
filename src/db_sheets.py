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

def get_sheet():
    """Autentica y devuelve el objeto de la hoja de cálculo principal."""
    if not SPREADSHEET_ID:
        raise ValueError("No se encontró SPREADSHEET_ID en el archivo .env")
        
    creds = Credentials.from_service_account_file(
        'credentials.json', scopes=SCOPES
    )
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).sheet1

def generate_id():
    """Genera un código corto y único para la pieza, ej: M-A32"""
    chars = string.ascii_uppercase + string.digits
    return "M-" + ''.join(random.choices(chars, k=3))

def add_piece(medidas, color, foto_url):
    """
    Añade una nueva pieza al inventario de Google Sheets.
    Devuelve el ID corto generado para que el operario lo anote.
    """
    sheet = get_sheet()
    piece_id = generate_id()
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Orden de las columnas: ID, Fecha, Medidas, Color, Foto, Estado
    row = [piece_id, fecha, medidas, color, foto_url, "DISPONIBLE"]
    sheet.append_row(row)
    
    return piece_id

def use_piece(piece_id):
    """
    Busca la pieza por su ID corto y la marca como 'USADA'.
    Retorna True si fue exitoso, False si no existe el ID.
    """
    sheet = get_sheet()
    piece_id = piece_id.upper() # Para evitar errores de mayúsculas/minúsculas
    try:
        # Buscar el piece_id en la columna 1 (A)
        cell = sheet.find(piece_id, in_column=1)
        # Actualizar el estado en la columna 6 (F) a "USADO"
        sheet.update_cell(cell.row, 6, "USADO")
        return True
    except gspread.exceptions.CellNotFound:
        return False

