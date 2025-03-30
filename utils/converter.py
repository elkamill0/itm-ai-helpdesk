import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import easyocr


class OCRProcessor:
    def __init__(self, image_path: str):
        self.image_path = image_path
        self.image = self.load_image()

    def load_image(self) -> Image.Image:
        return Image.open(self.image_path).convert("L")

    def sharpen_image(self) -> None:
        self.image = self.image.filter(ImageFilter.SHARPEN)
        self.image = self.image.filter(ImageFilter.EDGE_ENHANCE_MORE)
        enhancer = ImageEnhance.Contrast(self.image)
        self.image = enhancer.enhance(3.0)
        enhancer = ImageEnhance.Brightness(self.image)
        self.image = enhancer.enhance(1.5)

    def convert_to_text(self, lang: str = "pol") -> str:
        return pytesseract.image_to_string(self.image, lang=lang)


class enhancedOCR:
    def __init__(self, image_path: str):
        self.image_path = image_path

    def convert_to_text(self) -> str:
        reader = easyocr.Reader(["pl", "en"])
        result = reader.readtext(self.image_path)
        return " ".join([item[1] for item in result])


if __name__ == "__main__":
    obraz = "../resources/image.png"
    ocr = OCRProcessor(obraz)
    ocr.sharpen_image()
    extracted_text = ocr.convert_to_text()
    print("Recognized text:")
    print(extracted_text)
