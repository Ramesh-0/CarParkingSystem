# parking_system/utils/ocr_utils.py
import easyocr

def init_ocr():
    print("[OCR] Initializing EasyOCR...")
    return easyocr.Reader(['en'])

def read_plate_text(reader, image):
    results = reader.readtext(image)
    texts = [res[1] for res in results if len(res[1]) >= 4]
    if texts:
        plate = max(texts, key=len)
        print(f"[OCR] Detected Plate: {plate}")
        return plate
    print("[OCR] No plate detected.")
    return None
