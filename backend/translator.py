import os
import requests

# Language code mapping
LANG_MAP = {
    "es": "es-ES",
    "en": "en-GB",
    "de": "de-DE",
    "fr": "fr-FR",
    "zh": "zh-CN",
    "pt": "pt-BR",
    "it": "it-IT",
}


class DiagramTranslator:
    def __init__(self, api_key=None, target_lang="es"):
        self.api_key = api_key
        self.target_lang = target_lang.lower()

    def translate_text(self, text):
        """Translate using MyMemory API — free, no key needed."""
        if not text or not text.strip() or len(text.strip()) < 2:
            return text

        # Chunk if too long
        if len(text) > 480:
            return self._translate_in_chunks(text)

        target = LANG_MAP.get(self.target_lang, f"{self.target_lang}-{self.target_lang.upper()}")

        try:
            url = "https://api.mymemory.translated.net/get"
            params = {
                "q": text.strip(),
                "langpair": f"auto|{target}",
            }
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                translated = data.get("responseData", {}).get("translatedText", "")
                if translated and translated.upper() != text.strip().upper():
                    return translated
        except Exception as e:
            print(f"Translation error: {e}")

        return text

    def _translate_in_chunks(self, text, chunk_size=450):
        """Split long text into chunks and translate each."""
        words = text.split()
        chunks, current_chunk, current_len = [], [], 0

        for word in words:
            if current_len + len(word) + 1 > chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_len = len(word)
            else:
                current_chunk.append(word)
                current_len += len(word) + 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return " ".join(self.translate_text(c) for c in chunks)

    def process_pdf(self, input_path, output_path):
        """
        Layout-preserving PDF translation using PyMuPDF.
        Replaces each text span in-place while keeping all graphics intact.
        """
        import fitz  # PyMuPDF

        doc = fitz.open(input_path)

        for page in doc:
            blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]

            for b in blocks:
                if b.get("type") != 0:
                    continue  # Skip images and other non-text blocks

                for line in b.get("lines", []):
                    for span in line.get("spans", []):
                        original = span.get("text", "")
                        if not original.strip():
                            continue

                        translated = self.translate_text(original)
                        if translated == original:
                            continue

                        # Redact (erase) original text bbox
                        bbox = fitz.Rect(span["bbox"])
                        page.add_redact_annot(bbox, fill=(1, 1, 1))
                        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

                        # Write translated text in same position, font size and color
                        size = span.get("size", 10)
                        color_int = span.get("color", 0)
                        r = ((color_int >> 16) & 0xFF) / 255
                        g = ((color_int >> 8) & 0xFF) / 255
                        b = (color_int & 0xFF) / 255

                        # Auto-shrink font if translated text is longer
                        text_width = bbox.width
                        estimated_char_width = size * 0.6
                        max_chars = max(1, int(text_width / estimated_char_width))
                        if len(translated) > max_chars:
                            size = max(5, size * (max_chars / len(translated)))

                        page.insert_text(
                            fitz.Point(bbox.x0, bbox.y1 - 1),
                            translated,
                            fontsize=size,
                            color=(r, g, b),
                        )

        doc.save(output_path, garbage=4, deflate=True)
        doc.close()
        return output_path

    def process_image_pdf(self, input_path, output_path):
        """
        Fallback for scanned/image PDFs using OCR would go here.
        For now, copies the file.
        """
        import shutil
        shutil.copy(input_path, output_path)
        return output_path


if __name__ == "__main__":
    print("DiagramTranslator ready — PyMuPDF layout-preserving mode.")
