import pytest
from unittest.mock import patch, MagicMock
from src.storage_drive import upload_photo

@patch("src.storage_drive.storage.Client")
def test_upload_photo(mock_client_class):
    # Configurar el mock
    mock_client = mock_client_class.return_value
    mock_bucket = mock_client.bucket.return_value
    mock_blob = mock_bucket.blob.return_value
    mock_blob.public_url = "http://fake.url/foto.jpg"

    # Llamar a la función
    url = upload_photo("ruta/local/test.jpg", "test.jpg")

    # Verificar que el cliente de GCS fue inicializado
    mock_client_class.assert_called_once()
    
    # Verificar que se intentó obtener el bucket
    mock_client.bucket.assert_called_once()
    
    # Verificar que se creó el blob y se subió el archivo
    mock_bucket.blob.assert_called_once_with("test.jpg")
    mock_blob.upload_from_filename.assert_called_once_with("ruta/local/test.jpg", content_type='image/jpeg')
    


    # Verificar URL de retorno
    assert url == "http://fake.url/foto.jpg"
