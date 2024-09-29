import numpy as np

class ImageMasker:
    def __init__(self, image_array):
        self.image = image_array
        self.rois = []

    def add_roi(self, image_type):
        if image_type == "passport":
            self.rois = [
                ((670, 96, 855, 130), "passport_number"),  
                ((335, 150, 530, 180), "last_name"),
                ((335, 204, 530, 238), "first_name"),
                ((335, 256, 530, 292), "nationality"),
                ((335, 313, 530, 350), "date_of_birth"),
                ((335, 367, 530, 400), "gender"),
                ((335, 422, 530, 458), "date_of_issue"),
                ((335, 473, 530, 513), "date_of_expiry"),
                ((645, 315, 860, 351), "citizenship_number"),
                ((645, 369, 860, 404), "place_of_birth")
            ]
        elif image_type == "pan":
            self.rois = []
        
        elif image_type == "citizenship_front":
            self.rois = []
        else:
            raise ValueError(f"Unknown image type: {image_type}")

    def apply_single_roi(self, roi):
        coordinates, _= roi
        mask = np.zeros_like(self.image, dtype=np.uint8)  # Black mask
        start_x, start_y, end_x, end_y = coordinates
        mask[start_y:end_y, start_x:end_x] = self.image[start_y:end_y, start_x:end_x]
        return mask