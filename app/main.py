from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image

import os

app = FastAPI()

UPLOAD_DIR = "./uploads/"

@app.post("/upload/")
async def upload_pdf_and_seal(pdf: UploadFile = File(...), seal: UploadFile = File(...)):
    # Save uploaded files
    pdf_path = os.path.join(UPLOAD_DIR, pdf.filename)
    seal_path = os.path.join(UPLOAD_DIR, "seals", seal.filename)

    with open(pdf_path, "wb") as pdf_file:
        pdf_file.write(await pdf.read())

    with open(seal_path, "wb") as seal_file:
        seal_file.write(await seal.read())

    output_pdf_path = os.path.join(UPLOAD_DIR, "outputs", "stamped_" + pdf.filename)
    add_seal_to_pdf(pdf_path, seal_path, output_pdf_path)

    return FileResponse(output_pdf_path, filename="stamped_" + pdf.filename)

def add_seal_to_pdf(pdf_path, seal_path, output_pdf_path):
    # Open the existing PDF
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    # Load the seal image
    seal_img = Image.open(seal_path)
    seal_width, seal_height = seal_img.size

    # Set seal position (example position, you can adjust this)
    seal_position = (500, 100)  # (x, y) coordinates

    for i in range(len(reader.pages)):
        page = reader.pages[i]

        # Create a new PDF with the seal
        packet = create_seal_pdf(seal_path, seal_position, page.mediabox.upper_right)

        # Merge the seal PDF with the original page
        page.merge_page(PdfReader(packet).pages[0])

        writer.add_page(page)

    # Write the output PDF
    with open(output_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)

def create_seal_pdf(seal_path, seal_position, page_size):
    packet = os.path.join(UPLOAD_DIR, "temp_seal.pdf")

    c = canvas.Canvas(packet, pagesize=page_size)
    c.drawImage(seal_path, *seal_position, width=100, height=100, mask='auto')
    c.save()

    return packet

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
