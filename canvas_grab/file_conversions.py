import pypdfium2 as pdfium
import json
from bs4 import BeautifulSoup
from termcolor import colored

def convert_file_to_json(path):
    print("Converting file to json: ", path)
    if path.endswith('.pdf'):
        return pdf_to_json(path)
    elif path.endswith('.html'):
        return html_to_json(path)
    else:
        # Log a warning, use color
        print(colored(f'  Unsupported file type: {path}', 'yellow'))
        return None 

def pdf_to_json(path):
    pdf = pdfium.PdfDocument(path)
    document = {"document_name": path.split('/')[-1], "content": []}
    for i, page in enumerate(pdf, start=1):
        document["content"].append({"page_number": i, "text": page.get_textpage().get_text_bounded()})
    return json.dumps(document, indent=4)

def html_to_json(path):
    with open(path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    document = {"document_name": path.split('/')[-1], "content": {}}
    
    # Check if the page contains a meta refresh (redirect)
    meta_refresh = soup.find('meta', attrs={"http-equiv": "refresh"})
    if meta_refresh:
        document["content"] = {
            "type": "redirect",
            "redirect_url": meta_refresh["content"].split("URL=")[-1]
        }
    else:
        # Extract the title, headings, and paragraphs if the page contains actual content
        document["content"] = {
            "title": soup.title.string if soup.title else None,
            "paragraphs": [p.get_text(strip=True) for p in soup.find_all('p')]
        }
    
    return json.dumps(document, indent=4)
