import pytest
from unittest.mock import patch, MagicMock
from src.db_sheets import generate_id, add_piece, use_piece

def test_generate_id():
    # Verifica que el ID empiece con "M-" y tenga 5 caracteres en total
    piece_id = generate_id()
    assert piece_id.startswith("M-")
    assert len(piece_id) == 5
    
    # Verifica que no contenga letras confusas (I, O, 0, 1)
    for char in piece_id[2:]:
        assert char not in ["I", "O", "0", "1"]

@patch("src.db_sheets.Credentials.from_service_account_file")
@patch("src.db_sheets.gspread.authorize")
def test_add_piece(mock_authorize, mock_creds):
    # Mockear la hoja de Sheets
    mock_client = mock_authorize.return_value
    mock_sheet = mock_client.open_by_key.return_value.sheet1
    
    piece_id = add_piece("100x100", "Blanco", "16MM", "no veta", "http://url.com")
    
    assert piece_id.startswith("M-")
    mock_sheet.append_row.assert_called_once()
    
    # Extraer los argumentos con los que se llamó append_row
    args, _ = mock_sheet.append_row.call_args
    row_inserted = args[0]
    
    # ID, Color, Grosor, Medidas, Veta, Foto, Estado, Date
    assert row_inserted[0] == piece_id
    assert row_inserted[1] == "Blanco"
    assert row_inserted[2] == "16MM"
    assert row_inserted[3] == "100x100"
    assert row_inserted[4] == "no veta"
    assert row_inserted[5] == "http://url.com"
    assert row_inserted[6] == "DISPONIBLE"

@patch("src.db_sheets.Credentials.from_service_account_file")
@patch("src.db_sheets.gspread.authorize")
def test_use_piece_success(mock_authorize, mock_creds):
    mock_client = mock_authorize.return_value
    mock_sheet = mock_client.open_by_key.return_value.sheet1
    
    # Simular que find() devuelve una celda en la fila 3
    mock_cell = MagicMock()
    mock_cell.row = 3
    mock_sheet.find.return_value = mock_cell
    
    resultado = use_piece("M-A32")
    
    assert resultado is True
    mock_sheet.update_cell.assert_called_once_with(3, 7, "USADO")

@patch("src.db_sheets.Credentials.from_service_account_file")
@patch("src.db_sheets.gspread.authorize")
def test_use_piece_not_found(mock_authorize, mock_creds):
    mock_client = mock_authorize.return_value
    mock_sheet = mock_client.open_by_key.return_value.sheet1
    
    # Simular que find() no encuentra la celda
    mock_sheet.find.return_value = None
    
    resultado = use_piece("M-INVALID")
    
    assert resultado is False
    mock_sheet.update_cell.assert_not_called()
