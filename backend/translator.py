import os
import requests

# Try to import PyMuPDF - it's optional, we have a fallback
try:
    import fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("WARNING: PyMuPDF not available. PDF layout preservation will be limited.")


# Free translation API - no key needed
LIBRE_TRANSLATE_URLS = [
    "https://libretranslate.com/translate",
    "https://translate.terraprint.co/translate",
    "https://lt.vern.cc/translate",
]


class DiagramTranslator:
    def __init__(self, api_key=None, target_lang="es"):
        self.api_key = api_key
        self.target_lang = target_lang.lower()

    def translate_text(self, text):
        """Translate text using LibreTranslate (free, no API key needed)."""
        if not text.strip() or len(text.strip()) < 2:
            return text

        payload = {
            "q": text,
            "source": "auto",
            "target": self.target_lang,
            "format": "text"
        }
        headers = {"Content-Type": "application/json"}

        for url in LIBRE_TRANSLATE_URLS:
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("translatedText", text)
            except Exception:
                continue

        # If all APIs fail, return original text
        return text

    def process_pdf(self, input_path, output_path):
        """Process PDF preserving layout. Uses PyMuPDF if available."""
        if PYMUPDF_AVAILABLE:
            return self._process_with_pymupdf(input_path, output_path)
        else:
            return self._process_simple(input_path, output_path)

    def _process_with_pymupdf(self, input_path, output_path):
        """Full layout-aware translation using PyMuPDF."""
        doc = fitz.open(input_path)

        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if b["type"] == 0:
                    for l in b["lines"]:
                        for s in l["spans"]:
                            original_text = s["text"]
                            if not original_text.strip():
                                continue

                            translated_text = self.translate_text(original_text)
                            if translated_text == original_text:
                                continue

                            rect = fitz.Rect(s["bbox"])
                            page.add_redact_annot(rect, fill=(1, 1, 1))
                            page.apply_redactions()

                            font_size = s["size"]
                            color = s["color"]
                            r = (color >> 16) & 0xFF
                            g = (color >> 8) & 0xFF
                            b_val = color & 0xFF
                            rgb = (r / 255, g / 255, b_val / 255)

                            page.insert_text(
                                s["origin"],
                                translated_text,
                                fontsize=font_size,
                                color=rgb,
                            )

        doc.save(output_path)
        doc.close()
        return output_path

    def _process_simple(self, input_path, output_path):
        """
        Fallback when PyMuPDF is not available.
        Copies the file and adds a note about limited translation.
        """
        import shutil
        shutil.copy(input_path, output_path)
        print("WARNING: PyMuPDF not available. File copied without translation.")
        return output_path


if __name__ == "__main__":
    translator = DiagramTranslator(target_lang="es")
    print(f"Translator ready. PyMuPDF available: {PYMUPDF_AVAILABLE}")
