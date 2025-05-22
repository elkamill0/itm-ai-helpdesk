import pytest
from unittest.mock import patch, MagicMock
from utils.converter import OCRProcessor, enhancedOCR
from PIL import Image, ImageChops


@pytest.fixture
def dummy_image():
    img = Image.new("L", (100, 100))
    for x in range(100):
        for y in range(100):
            img.putpixel((x, y), (x + y) % 256)
    return img


@patch("utils.converter.Image.open")
def test_load_image(mock_open, dummy_image):
    mock_open.return_value = dummy_image

    processor = OCRProcessor("fake_path.png")
    assert isinstance(processor.image, Image.Image)


@patch("utils.converter.Image.open")
def test_sharpen_image(mock_open, dummy_image):
    mock_open.return_value = dummy_image
    processor = OCRProcessor("fake_path.png")
    original_image = processor.image.copy()

    processor.sharpen_image()

    diff = ImageChops.difference(processor.image, original_image)
    assert diff.getbbox() is not None


@patch("utils.converter.pytesseract.image_to_string", return_value="Testowy tekst")
@patch("utils.converter.Image.open")
def test_convert_to_text(mock_open, mock_ocr, dummy_image):
    mock_open.return_value = dummy_image
    processor = OCRProcessor("fake_path.png")

    processor.sharpen_image()
    text = processor.convert_to_text(lang="pol")
    assert text == "Testowy tekst"
    mock_ocr.assert_called_once()


@patch("utils.converter.easyocr.Reader")
def test_enhanced_ocr(mock_reader):
    mock_instance = MagicMock()
    mock_instance.readtext.return_value = [
        (None, "Pierwszy"),
        (None, "Drugi"),
        (None, "Trzeci"),
    ]
    mock_reader.return_value = mock_instance

    enhanced = enhancedOCR("fake_image.png")
    text = enhanced.convert_to_text()

    assert text == "Pierwszy Drugi Trzeci"
    mock_reader.assert_called_once_with(["pl", "en"])
