import fitz  # This is the actual import name for PyMuPDF

def extract_text_from_pdf(uploaded_file):
    """
    Takes an uploaded PDF file and returns all the text inside it as a string.
    Raises a ValueError with a friendly message if the PDF can't be opened
    or contains no extractable text (e.g., a scanned image with no text layer).
    """
    try:
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    except Exception:
        raise ValueError("This file could not be opened as a valid PDF. Please upload a proper PDF resume.")

    full_text = ""
    for page in pdf_document:
        full_text += page.get_text()

    pdf_document.close()

    if not full_text.strip():
        raise ValueError("No readable text was found in this PDF. It might be a scanned image "
                          "without selectable text. Please upload a text-based PDF resume.")

    return full_text