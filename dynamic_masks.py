import easyocr
import cv2
import numpy as np

class DynamicMasks:
    def __init__(self, image):
        self.reader = easyocr.Reader(['en'], gpu=False)
        self.image = image
        self.mask = np.zeros_like(self.image, dtype=np.uint8)
        self.extracted_data = {}
        
    def select_key_distance(image_has):
        if (image_has=="Municipality"):
            key_distances = {
                "Citizenship Certificate No.": (300, 300),
                "Sex": (48, 100),
                "Full Name": (300, 300),
                "Year": (50, 56),  
                "Month": (66, 56),  
                "Day": (47, 56),  
                "District": (86, 150), 
                "Municipality": (135, 290),  
                "Ward No": (100, 50)
            }
        elif (image_has == "VDC"):
            {
                "Citizenship Certificate No.": (300, 300),
                "Sex": (48, 100),
                "Full Name": (300, 300),
                "Year": (50, 56),  
                "Month": (66, 56),  
                "Day": (47, 56),  
                "District": (86, 150), 
                "VDC": (76, 200),  
                "Ward No": (100, 50)
            }
        elif (image_has.lower() == "sub-metropolitan"):
            {
                "Citizenship Certificate No.": (300, 300),
                "Sex": (48, 100),
                "Full Name": (300, 300),
                "Year": (50, 56),  
                "Month": (66, 56),  
                "Day": (47, 56),  
                "District": (86, 150), 
                "Sub-Metropolitan": (210, 200),  
                "Ward No": (100, 50)
            }
        else:
            raise Exception("Invalid document type selected")
        return key_distances
    
    def extract_text(self, image_has):
        results = self.reader.readtext(self.image)
        key_distances = DynamicMasks.select_key_distance(image_has)
        
        for result in results:
            text = result[1]
            (x1, y1), (x2, y2), (x3, y3), (x4,y4) = result[0]

            for key, (distance1, distance2) in key_distances.items():
                if (key in text) or (text in key):
                    x_start = int(x1 + distance1)
                    x_end = int(x_start + distance2)
                    y_start = int(y1)
                    y_end = int(y4)
                    self.mask[y_start:y_end, x_start:x_end] = self.image[y_start:y_end, x_start:x_end]
                    value = self.reader.readtext(self.mask)
                    if value:
                        data = value[0][1]
                        self.extracted_data[key] = data.strip()
                        self.mask = np.zeros_like(self.image, dtype=np.uint8)
                    break
        return self.extracted_data