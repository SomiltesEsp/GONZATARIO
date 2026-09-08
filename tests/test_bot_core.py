import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, Message, User, Chat, PhotoSize, File
from telegram.ext import ContextTypes
from src.bot_core import (
    start, handle_menu_choice, baja_id_recibido,
    medidas_recibidas, grosor_recibido, grosor_custom_recibido,
    color_recibido, veta_recibida, foto_recibida,
    CHOOSING_ACTION, MEDIDAS, GROSOR, GROSOR_CUSTOM, COLOR, VETA, FOTO, BAJA_ID
)

@pytest.fixture
def mock_update():
    update = MagicMock(spec=Update)
    message = MagicMock(spec=Message)
    
    user = User(id=123, first_name="Test", is_bot=False)
    chat = Chat(id=456, type="private")
    
    message.from_user = user
    message.chat = chat
    message.text = ""
    message.reply_text = AsyncMock()
    update.message = message
    
    return update

@pytest.fixture
def mock_context():
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    context.args = []
    return context

@pytest.mark.asyncio
async def test_start(mock_update, mock_context):
    estado = await start(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    assert estado == CHOOSING_ACTION

@pytest.mark.asyncio
async def test_handle_menu_registrar(mock_update, mock_context):
    mock_update.message.text = "➕ Registrar Pieza"
    estado = await handle_menu_choice(mock_update, mock_context)
    assert estado == MEDIDAS

@pytest.mark.asyncio
async def test_handle_menu_baja(mock_update, mock_context):
    mock_update.message.text = "➖ Dar de Baja"
    estado = await handle_menu_choice(mock_update, mock_context)
    assert estado == BAJA_ID

@pytest.mark.asyncio
async def test_flujo_medidas_recibidas(mock_update, mock_context):
    mock_update.message.text = "500x500"
    estado = await medidas_recibidas(mock_update, mock_context)
    assert mock_context.user_data['medidas'] == "500x500"
    assert estado == GROSOR

@pytest.mark.asyncio
async def test_flujo_grosor_recibido_normal(mock_update, mock_context):
    mock_update.message.text = "18mm"
    estado = await grosor_recibido(mock_update, mock_context)
    assert mock_context.user_data['grosor'] == "18mm"
    assert estado == COLOR

@pytest.mark.asyncio
async def test_flujo_grosor_recibido_otro(mock_update, mock_context):
    mock_update.message.text = "Otro..."
    estado = await grosor_recibido(mock_update, mock_context)
    assert estado == GROSOR_CUSTOM

@pytest.mark.asyncio
async def test_flujo_grosor_custom(mock_update, mock_context):
    mock_update.message.text = "22mm"
    estado = await grosor_custom_recibido(mock_update, mock_context)
    assert mock_context.user_data['grosor'] == "22mm"
    assert estado == COLOR

@pytest.mark.asyncio
async def test_flujo_color_recibido(mock_update, mock_context):
    mock_update.message.text = "Blanco"
    estado = await color_recibido(mock_update, mock_context)
    assert mock_context.user_data['color'] == "Blanco"
    assert estado == VETA

@pytest.mark.asyncio
async def test_flujo_veta_recibida(mock_update, mock_context):
    mock_update.message.text = "A lo largo"
    estado = await veta_recibida(mock_update, mock_context)
    assert mock_context.user_data['veta'] == "A lo largo"
    assert estado == FOTO

@pytest.mark.asyncio
@patch("src.bot_core.upload_photo")
@patch("src.bot_core.add_piece")
@patch("src.bot_core.os.path.exists")
@patch("src.bot_core.os.remove")
async def test_flujo_foto_recibida(mock_remove, mock_exists, mock_add_piece, mock_upload_photo, mock_update, mock_context):
    mock_context.user_data = {
        'medidas': '500x500',
        'grosor': '18mm',
        'color': 'Blanco',
        'veta': 'Sin veta'
    }
    
    mock_photo = MagicMock(spec=PhotoSize)
    mock_file = AsyncMock(spec=File)
    mock_photo.get_file = AsyncMock(return_value=mock_file)
    mock_update.message.photo = [mock_photo]
    mock_update.message.message_id = 999
    
    mock_upload_photo.return_value = "http://fake.url"
    mock_add_piece.return_value = "M-A32"
    mock_exists.return_value = True
    
    estado = await foto_recibida(mock_update, mock_context)
    
    mock_file.download_to_drive.assert_called_once()
    mock_upload_photo.assert_called_once()
    mock_add_piece.assert_called_once_with("500x500", "Blanco", "18mm", "Sin veta", "http://fake.url")
    assert estado == CHOOSING_ACTION # Vuelve al menú

@pytest.mark.asyncio
@patch("src.bot_core.use_piece")
async def test_baja_pieza_exito(mock_use_piece, mock_update, mock_context):
    mock_update.message.text = "M-A32"
    mock_use_piece.return_value = True
    
    estado = await baja_id_recibido(mock_update, mock_context)
    
    mock_use_piece.assert_called_once_with("M-A32")
    assert "USADA" in mock_update.message.reply_text.call_args_list[0][0][0]
    assert estado == CHOOSING_ACTION
