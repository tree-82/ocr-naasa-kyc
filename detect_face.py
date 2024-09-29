import cv2
import numpy as np

class FaceDetector:
    def __init__(self):
        self.model_file = "model/res10_300x300_ssd_iter_140000.caffemodel"
        self.config_file = "model/deploy.prototxt.txt"
        self.face_net = cv2.dnn.readNetFromCaffe(self.config_file, self.model_file)
    
    def change_orientation(self, image, rotation_interval):
        """
        It takes the image and sends it to the face detection model 
        by rotating it at rotation_interval degree intervals and returning the original image 
        according to that angle which has the highest probability of faces in the image.
        """
        face_conf = []
        if image is None:
            raise ValueError("Image is None. Ensure the image is properly loaded.")
        
        for angle in range(0, 360, rotation_interval):
            img_rotated = self.rotate(image, angle)
            face_conf.append((self.detect_face(img_rotated), angle))

        face_confidence = np.array(face_conf)
        face_arg_max = np.argmax(face_confidence, axis=0)
        angle_max = face_confidence[face_arg_max[0]][1]

        rotated_img = self.rotate(image, angle_max)
        return rotated_img
    
    def detect_face(self, img):
        blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)), 1.0,
                                    (300, 300), (104.0, 117.0, 123.0))
        
        self.face_net.setInput(blob)
        faces = self.face_net.forward()
        
        for i in range(faces.shape[2]):
            confidence = faces[0, 0, i, 2]
            if confidence > 0.6:
                return confidence
        return 0
    
    def rotate(self, image, angle):
        if image is None:
            raise ValueError("Image is None. Ensure the image is properly loaded.")
        # grab the dimensions of the image and then determine the center
        (h, w) = image.shape[:2]
        (c_x, c_y) = (w // 2, h // 2)

        # grab the rotation matrix (applying the negative of the
        # angle to rotate clockwise), then grab the sine and cosine
        # (i.e., the rotation components of the matrix)
        M = cv2.getRotationMatrix2D((c_x, c_y), angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])

        # compute the new bounding dimensions of the image
        n_w = int((h * sin) + (w * cos))
        n_h = int((h * cos) + (w * sin))

        # adjust the rotation matrix to take into account translation
        M[0, 2] += (n_w / 2) - c_x
        M[1, 2] += (n_h / 2) - c_y

        # perform the actual rotation and return the image
        return cv2.warpAffine(image, M, (n_w, n_h))
