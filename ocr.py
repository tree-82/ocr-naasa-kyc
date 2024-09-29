import easyocr

class ExtractText:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=False)
        
    def extract_words(self, image, confidence_threshold=0):
        if image is None:
            raise ValueError("No image found")
        
        # Get the OCR results
        ocr_results = self.reader.readtext(image)

        print(ocr_results)
        
        # Filter the results based on the confidence threshold
        filtered_results = [result[1] for result in ocr_results if result[2] >= confidence_threshold]
        
        # Return a single string containing all the text that passed the confidence filter
        return " ".join(filtered_results) if filtered_results else None