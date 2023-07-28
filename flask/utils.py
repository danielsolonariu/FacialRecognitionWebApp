import base64

def get_data_uri(image_data):
    encoded_data = base64.b64encode(image_data).decode('utf-8')
    return f"data:image/jpeg;base64,{encoded_data}"
