from PIL import Image
from flask import current_app
import os
import secrets

def save_profile_image(image):
    # Generate unique string for each file
    random_hex = secrets.token_hex(16)
    # Get the file extension
    _, f_ext = os.path.splitext(image.filename)
    # New filename
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/dashboard/profile_pics', picture_fn)
    # Resize Image
    output_size = (300, 300)
    i = Image.open(image)
    i.thumbnail(output_size)
    # Save image
    i.save(picture_path)
    
    return picture_fn
    
    