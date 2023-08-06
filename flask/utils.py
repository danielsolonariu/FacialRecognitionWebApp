import base64
from datetime import datetime

import cv2
import face_recognition
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

def change_date_format(input_date_str):
    # Parse the input date string into a datetime object
    input_date = datetime.strptime(input_date_str, "%Y-%m-%d %H:%M:%S.%f")

    # Format the datetime object into the desired format
    formatted_date_str = input_date.strftime("%d/%m/%Y %H:%M")

    return formatted_date_str

# def return_all_faces_from_an_image():
