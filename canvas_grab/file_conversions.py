import pypdfium2 as pdfium

def pdf_to_page_dict(path):
    pdf = pdfium.PdfDocument(path)
    text = []
    for i, page in enumerate(pdf, start=1):
        text.append({
            "page_number": str(i),
            "text": page.get_textpage().get_text_bounded()
        })
    return text