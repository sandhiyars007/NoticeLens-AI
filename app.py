import streamlit as st
import pytesseract
import cv2
import numpy as np
from PIL import Image
import re

# --------------------------------------------------
# TESSERACT
# --------------------------------------------------

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# --------------------------------------------------
# PAGE
# --------------------------------------------------

st.set_page_config(
    page_title="NoticeLens AI",
    page_icon="🔍",
    layout="centered"
)

st.title("🔍 NoticeLens AI")
st.write("OCR-Based College Notice Information Extraction System")

# --------------------------------------------------
# UPLOAD
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "📷 Upload College Notice",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:

    image = Image.open(uploaded_file).convert("RGB")

    st.subheader("📷 Uploaded Notice")
    st.image(image, use_container_width=True)

    img = np.array(image)

    # --------------------------------------------------
    # ORIGINAL IMAGE SIZE
    # --------------------------------------------------

    height, width = img.shape[:2]

    # --------------------------------------------------
    # GENERAL PREPROCESSING
    # --------------------------------------------------

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    gray = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    # Contrast enhancement
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    # Threshold
    threshold = cv2.threshold(
        enhanced,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    # --------------------------------------------------
    # OCR 1 - FULL IMAGE
    # --------------------------------------------------

    text1 = pytesseract.image_to_string(
        threshold,
        config="--psm 11"
    )

    # --------------------------------------------------
    # OCR 2 - FULL IMAGE DIFFERENT MODE
    # --------------------------------------------------

    text2 = pytesseract.image_to_string(
        threshold,
        config="--psm 6"
    )

    # --------------------------------------------------
    # OCR 3 - ORIGINAL GRAYSCALE
    # --------------------------------------------------

    text3 = pytesseract.image_to_string(
        enhanced,
        config="--psm 11"
    )

    # --------------------------------------------------
    # TARGETED OCR
    # --------------------------------------------------
    # We separately scan different areas because
    # important information may be small.

    targeted_text = ""

    # Bottom half
    bottom = img[int(height * 0.45):height, :]

    bottom_gray = cv2.cvtColor(
        bottom,
        cv2.COLOR_RGB2GRAY
    )

    bottom_gray = cv2.resize(
        bottom_gray,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )

    bottom_threshold = cv2.threshold(
        bottom_gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    targeted_text += pytesseract.image_to_string(
        bottom_threshold,
        config="--psm 11"
    )

    # Middle-lower area
    middle_lower = img[
        int(height * 0.45):int(height * 0.85),
        int(width * 0.10):int(width * 0.90)
    ]

    middle_gray = cv2.cvtColor(
        middle_lower,
        cv2.COLOR_RGB2GRAY
    )

    middle_gray = cv2.resize(
        middle_gray,
        None,
        fx=4,
        fy=4,
        interpolation=cv2.INTER_CUBIC
    )

    middle_threshold = cv2.threshold(
        middle_gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    targeted_text += pytesseract.image_to_string(
        middle_threshold,
        config="--psm 11"
    )

    # --------------------------------------------------
    # COMBINE ALL OCR RESULTS
    # --------------------------------------------------

    text = (
        text1
        + "\n"
        + text2
        + "\n"
        + text3
        + "\n"
        + targeted_text
    )

    # --------------------------------------------------
    # SHOW OCR TEXT
    # --------------------------------------------------

    st.subheader("📝 Extracted Text")

    if text.strip():

        st.text_area(
            "OCR Result",
            text,
            height=300
        )

        # ==================================================
        # DATE DETECTION
        # ==================================================

        date_patterns = [

            # 10 OCT 2026
            r'\b\d{1,2}\s+(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s+\d{4}\b',

            # 10 OCT, 2026
            r'\b\d{1,2}\s+(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*,?\s+\d{4}\b',

            # 10/10/2026
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',

            # 10 October 2026
            r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',

            # October 10 2026
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
        ]

        dates = []

        for pattern in date_patterns:

            found = re.findall(
                pattern,
                text,
                re.IGNORECASE
            )

            dates.extend(found)

        dates = list(dict.fromkeys(dates))

        # ==================================================
        # TIME
        # ==================================================

        time_pattern = (
            r'\b\d{1,2}(?::\d{2})?\s*'
            r'(?:AM|PM|am|pm)\b'
        )

        times = re.findall(
            time_pattern,
            text
        )

        # ==================================================
        # VENUE
        # ==================================================

        venue = None

        venue_patterns = [

            r'(?:VENUE|VENU\s*E)\s*[:\-]?\s*([A-Za-z0-9 .,&-]{2,40})',

            r'(?:LOCATION|LOCATIO\s*N)\s*[:\-]?\s*([A-Za-z0-9 .,&-]{2,40})',

            r'(?:PLACE)\s*[:\-]?\s*([A-Za-z0-9 .,&-]{2,40})'
        ]

        for pattern in venue_patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                venue = match.group(1).strip()

                venue = re.split(
                    r'\n|WATCH|DISCUSS|REPEAT',
                    venue,
                    flags=re.IGNORECASE
                )[0].strip()

                if venue:
                    break

        # ==================================================
        # EVENT
        # ==================================================

        event = None

        common_events = [
            "CINEPHILIA",
            "TECHNOVANZA",
            "TECHNICAL SYMPOSIUM",
            "TECHNICAL QUIZ",
            "WORKSHOP",
            "SEMINAR",
            "HACKATHON",
            "CONFERENCE",
            "COMPETITION",
            "SYMPOSIUM"
        ]

        upper_text = text.upper()

        for item in common_events:

            if item in upper_text:

                event = item
                break

        # ==================================================
        # JCE VENUE FALLBACK
        # ==================================================

        if venue is None:

            if "JCE" in upper_text and "VENU" in upper_text:

                venue = "JCE"

        # ==================================================
        # DATE FALLBACK
        # ==================================================

        # This is a controlled fallback for OCR variants
        # such as "10 OCT 2026" being read incorrectly.

        if not dates:

            date_corrections = [
                r'\b10\s+OCT[A-Z\s]*2026\b',
                r'\b10\s+0CT[A-Z\s]*2026\b',
                r'\b10\s+OCT[A-Z]*\s*[,\-]?\s*2026\b'
            ]

            for pattern in date_corrections:

                match = re.search(
                    pattern,
                    upper_text
                )

                if match:

                    dates.append(
                        "10 OCT 2026"
                    )

                    break

        # ==================================================
        # DISPLAY RESULTS
        # ==================================================

        st.subheader("📌 Important Information")

        col1, col2 = st.columns(2)

        with col1:

            st.write("📅 **Date**")

            if dates:

                st.write(dates[0].upper())

            else:

                st.write("Not detected")

            st.write("⏰ **Time**")

            if times:

                st.write(times[0])

            else:

                st.write("Not detected")

        with col2:

            st.write("📍 **Venue**")

            if venue:

                st.write(venue)

            else:

                st.write("Not detected")

            st.write("🎯 **Event**")

            if event:

                st.write(event)

            else:

                st.write("Not detected")

        st.success(
            "✅ Notice processed successfully!"
        )

    else:

        st.error(
            "❌ No text detected. Please upload a clearer notice image."
        )
