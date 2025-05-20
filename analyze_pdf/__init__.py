import logging
import fitz
import requests
import tempfile
import azure.functions as func

DEI_TERMS = ["DIVERSITY", "INCLUSION", "EQUITY"]  # Use full list here

def find_dei_terms(text):
    return list({term for term in DEI_TERMS if term.lower() in text.lower()})

def analyze_pdf_from_url(pdf_url):
    response = requests.get(pdf_url)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name

    doc = fitz.open(tmp_path)
    all_text = "".join([page.get_text() for page in doc])
    doc.close()

    return find_dei_terms(all_text)

def main(req: func.HttpRequest) -> func.HttpResponse:
    pdf_url = req.params.get("url")
    if not pdf_url:
        return func.HttpResponse("Missing 'url' parameter", status_code=400)
    
    try:
        terms = analyze_pdf_from_url(pdf_url)
        return func.HttpResponse(str(terms), status_code=200)
    except Exception as e:
        logging.exception("Error analyzing PDF")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
