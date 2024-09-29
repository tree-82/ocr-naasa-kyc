from fastapi import FastAPI, HTTPException, UploadFile
import os
from pydantic import BaseModel
from dotenv import load_dotenv
import time
import cv2
from detect_face import FaceDetector
from perspective_corrector import PerspectiveCorrector
from dynamic_masks import DynamicMasks
from detect_line import LineDetector
import numpy as np
from PIL import Image
import io
from create_mask import ImageMasker
from ocr import ExtractText
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExtractRequest(BaseModel):
    data: str

class ExtractResponse(BaseModel):
    success: bool
    extracted_text: list

@app.get('/')
def home():
    return "The server is running."

async def get_image_data(img,document_type):
    corrector = PerspectiveCorrector(img)
    # warp the image
    img = corrector.correct_perspective()

    #create mask based on document
    if document_type =="passport":
        masker = ImageMasker(img)
        masker.add_roi(document_type)
        
        extract_text = ExtractText()
        extracted_data = {}
        #iterate over each roi and extract text
        for roi in masker.rois:
            masked_image = masker.apply_single_roi(roi)
            field_name = roi[1]
            text = extract_text.extract_words(masked_image)
            extracted_data[field_name]=text
            
    elif document_type == "citizenship_back":
        h, _ = img.shape[:2]
        top_40 = int(h *0.4)
        img = img[:top_40, :]
        dynamic_reader = DynamicMasks(img)
        extracted_data = dynamic_reader.extract_text(document_type)
    else:
        raise Exception("invalid document type selected")
    return extracted_data

@app.post("/passport")
async def extract_passport(file: UploadFile):
    try:
        start = time.time()
        file_content = await file.read()
        image = Image.open(io.BytesIO(file_content))
        image = np.array(image)
        print(image.shape)
        if image.shape[2] == 4:
            # Convert RGBA to RGB
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        detector = FaceDetector()

        # Use FaceDetector to process the image
        image = detector.change_orientation(image, 30)
        extracted_data = await get_image_data(image, "passport")
            
        end = time.time()

        print("Time taken: ", end-start)
        return extracted_data
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/citizenship/back")
async def extract_citizenship_back(file:UploadFile):
    try:
        start = time.time()
        file_content = await file.read()
        image = Image.open(io.BytesIO(file_content))
        image_np = np.array(image)
        if image_np.shape[2] == 4:
            # Convert RGBA to RGB
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        else:
            image = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)  

        '''
        TO-DO: Correct orientation of citizenship through Longest line detection
        # detector = LineDetector(image)
        # img = detector.change_orientation_by_line()
        '''

        extracted_data = await get_image_data(image, "citizenship_back")
            
        end = time.time()

        print("Time taken: ", end-start)
        return extracted_data
    except Exception as e:
        print("error: ", e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    host = os.environ.get('HOST')
    port = int(os.environ.get('PORT'))
    uvicorn.run(app, host=host, port=port)