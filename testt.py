import easyocr
import cv2
from matplotlib import pyplot as plt
from perspective_corrector import PerspectiveCorrector
import pandas as pd
import numpy as np
import time


start_time = time.time()
reader = easyocr.Reader(['en'], gpu=False)

image = cv2.imread('images/citize.jpg')

corrector = PerspectiveCorrector(image)
img = corrector.correct_perspective()

# h, w = img.shape[:2]
# top_40 = int(h*0.4)
# img = img[:top_40, :]

key_distances = {
    "Citizenship Certificate No.": (300, 300),
    "Sex":(48, 100),
    "Full Name": (300, 300),
    "Year": (50, 56),  
    "Month": (66, 56),  
    "Day": (47,56),  
    "District": (86, 150), 
    "Municipality": (135, 300),  
    "Ward No": (100, 50)
}
mask = np.zeros_like(img, dtype=np.uint8)

results = reader.readtext(img)

extracted_data = {}
for result in results:
    text = result[1]
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = result[0]
    
    for key, (distance1, distance2) in key_distances.items():
        if (key in text)|(text in key):
            x_start = int(x1 + distance1)
            x_end = int(x_start + distance2)
            y_start = int(y1)
            y_end = int(y4)
            
            mask[y_start:y_end, x_start:x_end] = img[y_start:y_end, x_start:x_end]
            value = reader.readtext(mask)
            if value:
                # print(value)
                data = value[0][1]
                extracted_text = data
                extracted_data[key] = extracted_text.strip()
                mask = np.zeros_like(img, dtype=np.uint8)
            break  # Stop after processing the first matching key
end_time = time.time()
print(extracted_data) 
print(end_time-start_time)  