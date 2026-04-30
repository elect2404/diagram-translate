import os
import requests
from pypdf import PdfReader
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors

# Free translation APIs - no key needed
LIBRE_TRANSLATE_URLS = [
    "https://translate.terraprint.co/translate",
    "https://lt.vern.cc/translate",
    "https://libretranslate.com/translate",
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
                resp = requests.post(url, json=payload, headers=headers, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    translated = data.get("translatedText", "")
                    if translated:
                        return translated
            except Exception:
                continue

        return text  # Return original if all APIs fail

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
