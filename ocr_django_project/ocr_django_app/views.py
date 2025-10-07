import os
from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from PIL import Image
import pytesseract
from reportlab.pdfgen import canvas
from io import BytesIO

# Path to your local tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def index(request):
    extracted_text = ""
    image_url = None

    if request.method == "POST" and request.FILES.get("image"):
        uploaded_file = request.FILES["image"]
        upload_dir = os.path.join("ocr_django_app", "static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        image_path = os.path.join(upload_dir, uploaded_file.name)

        # Save the uploaded file
        with open(image_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Extract text using Tesseract
        img = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(img)
        image_url = f"/static/uploads/{uploaded_file.name}"

        # Save extracted text in session for download
        request.session["extracted_text"] = extracted_text

    return render(request, "index.html", {
        "extracted_text": extracted_text,
        "image_url": image_url
    })


def download_pdf(request):
    """Generate and download extracted text as PDF"""
    text = request.session.get("extracted_text", "")
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica", 12)
    y = 800

    for line in text.split("\n"):
        p.drawString(50, y, line)
        y -= 15
        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 12)
            y = 800

    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="Extracted_Text.pdf")
