# 🎓 College Notice Reader

An OCR-based application that extracts text and important information from college notice images.

## Features

- Upload college notice image
- Extract text using OCR
- Image preprocessing using OpenCV
- Detect date and time
- Detect venue
- Detect event information
- Display information in an organized format

## Technologies Used

- Python
- Streamlit
- Tesseract OCR
- OpenCV
- NumPy
- Pillow

## Project Flow

Notice Image
↓
Image Preprocessing
↓
Tesseract OCR
↓
Text Extraction
↓
Information Extraction
↓
Date / Time / Venue / Event
↓
Final Output

## How to Run

Install the required packages:

pip install -r requirements.txt

Run the application:

streamlit run app.py

## Use Case

This project helps students quickly understand important information from college notices without manually reading the entire notice.
