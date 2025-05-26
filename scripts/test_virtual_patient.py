# scripts/test_virtual_patient.py

import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db
from scripts.create_demo_patient import create_demo_scenarios

def setup_virtual_patient():
    """Setup and test virtual patient functionality"""
    print("Setting up virtual patient functionality...")
    
    with app.app_context():
        # Make sure tables exist
        db.create_all()
        
        # Create demo scenarios
        create_demo_scenarios()
        
        print("\nSetup complete!")
        print("\nYou can now test the virtual patient functionality at:")
        print("http://localhost:5000/<language>/virtual-patient/")
        print("\nMake sure to add at least one image named 'patient_maria.jpg' in the static/images/virtual_patients/ directory")

if __name__ == "__main__":
    setup_virtual_patient()