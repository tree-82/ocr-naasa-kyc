import easyocr
import numpy as np
import difflib
import json
import cv2
import matplotlib.pyplot as plt

class DynamicMasks:
    def __init__(self, image):
        self.reader = easyocr.Reader(['en'], gpu=False)
        self.image = image
        self.extracted_data = {}
        
    def select_key_distance(document_type):
        if document_type == 'citizenship_back':
            key_distances = {
                'CITIZENSHIP CERTIFICATE NO.': (305, 300),
                'SEX': (48, 100),
                'FULL NAME': (300, 300),
                'YEAR': (54, 56),
                'MONTH': (72, 56),
                'DAY': (49, 56),
                'DISTRICT': (86, 150),
                'MUNICIPALITY': (135, 270),
                'VDC': (76, 200),
                'WARD NO': (105, 50),
                'R.M': (76, 200),
            }
        elif document_type == 'passport':
            key_distances = {}
            
        return key_distances
    
    def get_closest_match(self,input_string, valid_options,cutoff=0.5):
        closest_match = difflib.get_close_matches(input_string.upper(), valid_options, n=1, cutoff=cutoff)
        return closest_match[0] if closest_match else input_string

    def get_matching_field(self,input_string, valid_options,cutoff=0.5):
        closest_match = difflib.get_close_matches(input_string.upper(), valid_options, n=1, cutoff=cutoff)
        return closest_match[0] if closest_match else None
    
    def refine_extracted_values(self):
        print("here")
        # Valid options for the 'Sex' and 'Month' fields
        valid_sexes = ['Male', 'Female', 'Others']
        valid_months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

        # valid options for districts and municipalities
        with open ('data/district_municipality.json') as file:
            district_municipality = json.load(file)
        valid_districts = list(district_municipality.keys())

        data = {}
        if self.extracted_data.keys().__contains__('CITIZENSHIP CERTIFICATE NO.'):
            data['CITIZENSHIP CERTIFICATE NO.'] = self.extracted_data['CITIZENSHIP CERTIFICATE NO.']
        else:
            data['CITIZENSHIP CERTIFICATE NO.'] = ''

        if self.extracted_data.keys().__contains__('SEX'):
            data['SEX'] = self.get_closest_match(self.extracted_data['SEX'], valid_sexes,0.1)
        else:
            data['SEX'] = ''
        
        if self.extracted_data.keys().__contains__('FULL NAME'):
            data['FULL NAME'] = self.extracted_data['FULL NAME']
        else:
            data['FULL NAME'] = ''

        if self.extracted_data.keys().__contains__('YEAR'):
            try:
                self.extracted_data['YEAR'] = self.extracted_data['YEAR'].upper().replace('I','1').replace('L','1').replace('O','0').replace('S','5').replace('[','1').replace(']','1')
            except:
                self.extracted_data['YEAR'] = ''
        else:
            self.extracted_data['YEAR'] = ''

        if self.extracted_data.keys().__contains__('MONTH'):
            self.extracted_data['MONTH'] = self.get_closest_match(self.extracted_data['MONTH'], valid_months,0.1)
        else:
            self.extracted_data['MONTH'] = ''

        if self.extracted_data.keys().__contains__('DAY'):
            try:
                self.extracted_data['DAY'] = self.extracted_data['DAY'].upper().replace('I','1').replace('L','1').replace('O','0').replace('S','5').replace('[','1').replace(']','1')
            except:
                self.extracted_data["DAY"] = ''
        else:
            self.extracted_data['DAY'] = ''

        data['DATE OF BIRTH'] = {
            'YEAR': self.extracted_data['YEAR'],
            'MONTH': self.extracted_data['MONTH'],
            'DAY': self.extracted_data['DAY']
        }

        address = {}
        if self.extracted_data.keys().__contains__('DISTRICT'):
            address['DISTRICT'] = self.get_closest_match(self.extracted_data['DISTRICT'], valid_districts, 0.3)
            valid_municipalities = district_municipality[address['DISTRICT']]

            if self.extracted_data.keys().__contains__('MUNICIPALITY'):
                address['MUNICIPALITY'] = self.get_closest_match(self.extracted_data['MUNICIPALITY'], valid_municipalities, 0.4)
            elif self.extracted_data.keys().__contains__('VDC'):
                address['VDC'] = self.get_closest_match(self.extracted_data['VDC'], valid_municipalities, 0.4)
            elif self.extracted_data.keys().__contains__('R.M'):
                address['R.M'] = self.get_closest_match(self.extracted_data['R.M'], valid_municipalities, 0.4)
            
            if self.extracted_data.keys().__contains__('WARD NO'):
                address['WARD NO'] = self.extracted_data['WARD NO'].upper().replace('I','1').replace('L','1').replace('O','0').replace('S','5').replace('[','1').replace(']','1')
            else:
                address['WARD NO'] = ''

        data['BIRTH PLACE'] = address

        address = {}
        if self.extracted_data.keys().__contains__('DISTRICT2'):
            address['DISTRICT'] = self.get_closest_match(self.extracted_data['DISTRICT2'], valid_districts, 0.3)
            valid_municipalities = district_municipality[address['DISTRICT']]
            if self.extracted_data.keys().__contains__('MUNICIPALITY2'):
                address['MUNICIPALITY'] = self.get_closest_match(self.extracted_data['MUNICIPALITY2'], valid_municipalities, 0.4)
            elif self.extracted_data.keys().__contains__('VDC2'):
                address['VDC'] = self.get_closest_match(self.extracted_data['VDC2'], valid_municipalities, 0.4)
            elif self.extracted_data.keys().__contains__('R.M2'):
                address['R.M'] = self.get_closest_match(self.extracted_data['R.M2'], valid_municipalities, 0.4)
            
            if self.extracted_data.keys().__contains__('WARD NO2'):
                address['WARD NO'] = self.extracted_data['WARD NO2'].upper().replace('I','1').replace('L','1').replace('O','0').replace('S','5').replace('[','1').replace(']','1')
            else:
                address['WARD NO'] = ''
                
        data['PERMANENT ADDRESS'] = address

        self.extracted_data = data    

    def extract_text(self, document_type):
        # gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        # thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        results = self.reader.readtext(self.image)
        key_distances = DynamicMasks.select_key_distance(document_type)
        
        for result in results:
            text = str(result[1])
            (x1, y1), (_, _), (_, _), (_, y4) = result[0]
            
            for _ in range(len(results)):
                best_match = self.get_matching_field(text,list(key_distances.keys()),0.5)
                if best_match:
                    mask =np.zeros_like(self.image, dtype=np.uint8)
                    (distance1, distance2) = key_distances[best_match]
                    # Calculate the coordinates for the mask
                    x_start = int(x1 + distance1)
                    x_end = int(x_start + distance2)
                    y_start = int(y1-4)
                    y_end = int(y4+4)
                    
                    # Ensure that the slicing does not go out of bounds
                    x_start = max(x_start, 0)
                    x_end = min(x_end, mask.shape[1])
                    y_start = max(y_start, 0)
                    y_end = min(y_end, mask.shape[0])
                    
                    # Apply the mask to the relevant portion
                    image = self.image[y_start:y_end, x_start:x_end]

                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

                    # Read the text from the masked area
                    value = self.reader.readtext(thresh)
                    if value:
                        data = value[0][1]
                        print(best_match,": ",data)
                        extracted_text = data
                        address = ['DISTRICT','MUNICIPALITY','VDC','WARD NO','R.M']
                        if self.extracted_data.keys().__contains__(best_match):
                            if best_match in address:
                                self.extracted_data[best_match + '2'] = extracted_text.strip()
                            else:
                                self.extracted_data[best_match] = extracted_text.strip()
                        else:
                            self.extracted_data[best_match] = extracted_text.strip()
                    break 
        self.refine_extracted_values()
        return self.extracted_data