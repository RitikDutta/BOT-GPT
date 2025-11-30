import io

import pandas as pd
from PyPDF2 import PdfReader


def extract_text_from_pdf(file_storage) -> str:
    """
    simple pdf to text
    """
    pdf_bytes = file_storage.read()
    if not pdf_bytes:
        return ""

    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages_text = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages_text.append(text)

    df = pd.DataFrame({"page": range(1, len(pages_text) + 1), "text": pages_text})
    df["text"] = df["text"].fillna("").str.strip()

    full_text = "\n\n".join(df["text"].tolist())
    return full_text
