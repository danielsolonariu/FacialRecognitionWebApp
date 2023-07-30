import base64
import face_recognition
import cv2
import numpy as np

def get_data_uri(image_data):
    encoded_data = base64.b64encode(image_data).decode('utf-8')
    return f"data:image/jpeg;base64,{encoded_data}"

def image_convert_BGR_to_RGB(raw_image_data):
    # Decode the image data into a NumPy array
    nparr_img = np.frombuffer(raw_image_data, np.uint8)
    # Decode the image array using cv2
    bgr_img = cv2.imdecode(nparr_img, cv2.IMREAD_COLOR)
    # Convert BGR to RGB
    rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
    return rgb_img

def compare_2_faces(rgb_img1, rgb_img2):
    encoding_img1 = face_recognition.face_encodings(rgb_img1)[0]
    encoding_img2 = face_recognition.face_encodings(rgb_img2)[0]
    result = face_recognition.compare_faces([encoding_img1], encoding_img2)
    return result

# def return_all_faces_from_an_image():
