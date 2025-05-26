# scripts/setup_virtual_patient_images.py

import os
import sys
import shutil
from pathlib import Path
import urllib.request

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def setup_virtual_patient_images():
    """Set up the virtual patient images directory and download a placeholder image"""
    try:
        # Get the static folder path
        static_folder = app.static_folder if hasattr(app, 'static_folder') else 'static'
        
        # Create the virtual_patients directory in the static/images folder
        vp_dir = os.path.join(static_folder, 'images', 'virtual_patients')
        os.makedirs(vp_dir, exist_ok=True)
        
        # Check if we already have the patient image
        patient_image_path = os.path.join(vp_dir, 'patient_maria.jpg')
        
        if os.path.exists(patient_image_path):
            print(f"Image already exists at {patient_image_path}")
            return True
            
        # Download a placeholder image (using a royalty-free image URL)
        image_url = "https://st3.depositphotos.com/12982378/17855/i/450/depositphotos_178557924-stock-photo-adult-dentist-and-patient-sitting.jpg"
        
        print(f"Downloading placeholder image from {image_url}...")
        urllib.request.urlretrieve(image_url, patient_image_path)
        
        print(f"✅ Image downloaded to {patient_image_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up virtual patient images: {e}")
        return False

if __name__ == "__main__":
    setup_virtual_patient_images()