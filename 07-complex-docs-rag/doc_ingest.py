
from io import StringIO
from pdfminer.high_level import extract_text_to_fp
from typing import Tuple

def pdf_to_text(path: str) -> str:
    output = StringIO()
    with open(path, "rb") as f:
        extract_text_to_fp(f, output)
    return output.getvalue()
