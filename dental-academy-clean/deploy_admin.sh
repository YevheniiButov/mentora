#!/bin/bash
# Script to create admin on production server
# Run this on your production server

echo "🚀 Creating production admin user..."

# Navigate to your app directory (adjust path as needed)
cd /opt/render/project/src

# Run the admin creation script
python3 create_production_admin.py

echo "✅ Admin creation completed!"
