from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from process_pdf import add_stamps_and_signature
import fitz  
from PIL import Image
import json
import os
import uuid


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
STAMPS_DIR = "./stamps/"
SIGNATURES_DIR = "./uploads/signatures/"
OUTPUT_DIR = "./uploads/output/"

# Ensure directories exist
os.makedirs(STAMPS_DIR, exist_ok=True)
os.makedirs(SIGNATURES_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open("placement_config.json", "r") as config_file:
    placement_config = json.load(config_file)
with open("form21_config.json", "r") as config_file:
    form21_config = json.load(config_file)
with open("invoice_config.json","r") as config_file:
    invoice_config = json.load(config_file)


@app.post("/process_pdf/invoice")
async def process_pdf(pdf: UploadFile = File(...), signature: UploadFile = File(...)):
    if pdf.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Uploaded file is not a PDF.")
    if signature.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(status_code=400, detail="Signature must be an image (PNG or JPEG).")
    
    # Save uploaded files temporarily
    pdf_id = str(uuid.uuid4())
    pdf_path = os.path.join(OUTPUT_DIR, f"{pdf_id}_{pdf.filename}")
    signature_path = os.path.join(SIGNATURES_DIR, f"{pdf_id}_{signature.filename}")
    finance_company = ''
    with open(pdf_path, "wb") as pdf_file:
        pdf_file.write(await pdf.read())
    
    with open(signature_path, "wb") as sig_file:
        sig_file.write(await signature.read())
    
    # Process the PDF
    output_pdf_path = os.path.join(OUTPUT_DIR, f"processed_{pdf_id}_{pdf.filename}")
    try:
        add_stamps_and_signature(pdf_path, signature_path, output_pdf_path, invoice_config, finance_company)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {e}")
    finally:
        # Clean up temporary files
        os.remove(pdf_path)
        os.remove(signature_path)
    
    return FileResponse(output_pdf_path, filename=f"processed_{pdf.filename}", media_type='application/pdf')





@app.post("/process_pdf/form21")
async def process_pdf(pdf: UploadFile = File(...)):
    if pdf.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Uploaded file is not a PDF.")
   
    # Save uploaded files temporarily
    pdf_id = str(uuid.uuid4())
    pdf_path = os.path.join(OUTPUT_DIR, f"{pdf_id}_{pdf.filename}")
    
    with open(pdf_path, "wb") as pdf_file:
        pdf_file.write(await pdf.read())
    

    signature_path=''
    finance_company = ''
    # Process the PDF
    output_pdf_path = os.path.join(OUTPUT_DIR, f"processed_{pdf_id}_{pdf.filename}")
    try:
        add_stamps_and_signature(pdf_path, signature_path, output_pdf_path, form21_config, finance_company)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {e}")
    finally:
        # Clean up temporary files
        os.remove(pdf_path)
     
    
    return FileResponse(output_pdf_path, filename=f"processed_{pdf.filename}", media_type='application/pdf')



@app.post("/process_pdf/form20")
async def process_pdf(pdf: UploadFile = File(...), signature: UploadFile = File(...),finance_company: str = Form(...)):
    if pdf.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Uploaded file is not a PDF.")
    if signature.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(status_code=400, detail="Signature must be an image (PNG or JPEG).")
    
    # Save uploaded files temporarily
    pdf_id = str(uuid.uuid4())
    pdf_path = os.path.join(OUTPUT_DIR, f"{pdf_id}_{pdf.filename}")
    signature_path = os.path.join(SIGNATURES_DIR, f"{pdf_id}_{signature.filename}")
    
    with open(pdf_path, "wb") as pdf_file:
        pdf_file.write(await pdf.read())
    
    with open(signature_path, "wb") as sig_file:
        sig_file.write(await signature.read())
    
    # Process the PDF
    output_pdf_path = os.path.join(OUTPUT_DIR, f"processed_{pdf_id}_{pdf.filename}")
    try:
        add_stamps_and_signature(pdf_path, signature_path, output_pdf_path, placement_config, finance_company)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {e}")
    finally:
        # Clean up temporary files
        os.remove(pdf_path)
        os.remove(signature_path)
    
    return FileResponse(output_pdf_path, filename=f"processed_{pdf.filename}", media_type='application/pdf')


