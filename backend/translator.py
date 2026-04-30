import os
import requests
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors

# Language code mapping (UI value -> MyMemory format)
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
        """Translate using MyMemory API — free, no key needed, very reliable."""
        if not text or not text.strip() or len(text.strip()) < 2:
            return text

        # MyMemory has a 500 char limit per request, so chunk if needed
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
                # MyMemory returns the original text if it can't translate
                if translated and translated.upper() != text.upper():
                    return translated
        except Exception as e:
            print(f"MyMemory error: {e}")

        return text  # Return original if translation fails

    def _translate_in_chunks(self, text, chunk_size=450):
        """Split long text into chunks and translate each one."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_len = 0

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

        translated_chunks = [self.translate_text(chunk) for chunk in chunks]
        return " ".join(translated_chunks)

    def process_pdf(self, input_path, output_path):
        """
        Extract text from PDF, translate it, and generate a new clean PDF.
        Uses pypdf (lightweight) + reportlab for output.
        """
        try:
            # 1. Extract text from each page
            reader = PdfReader(input_path)
            pages_text = []
            for page in reader.pages:
                text = page.extract_text() or ""
                pages_text.append(text)

            # 2. Translate all text
            translated_pages = []
            for page_text in pages_text:
                if page_text.strip():
                    translated = self.translate_text(page_text)
                    translated_pages.append(translated)
                else:
                    translated_pages.append("")

            # 3. Build a new PDF with the translated content
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )

            styles = getSampleStyleSheet()
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                spaceAfter=6,
            )
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading2'],
                fontSize=11,
                textColor=colors.HexColor('#1e3a5f'),
                spaceAfter=4,
            )

            story = []
            for i, text in enumerate(translated_pages):
                if i > 0:
                    story.append(Spacer(1, 0.5*cm))
                    # Page separator
                    story.append(Paragraph(f"— Page {i+1} —", title_style))

                if text.strip():
                    # Split by lines and add paragraphs
                    for line in text.split('\n'):
                        if line.strip():
                            try:
                                story.append(Paragraph(line.strip(), normal_style))
                            except Exception:
                                # Skip lines with problematic characters
                                pass

            if not story:
                story.append(Paragraph("No text could be extracted from this PDF.", normal_style))

            doc.build(story)
            return output_path

        except Exception as e:
            print(f"Error processing PDF: {e}")
            raise


if __name__ == "__main__":
    translator = DiagramTranslator(target_lang="es")
    print("Translator ready. Using pypdf + reportlab (lightweight mode).")
