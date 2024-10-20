import cv2
import pytesseract
from datetime import datetime
import re

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Adjust for your OS


def preprocess_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresholded = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY)
    return thresholded


def extract_text_from_image(image_path):
    processed_image = preprocess_image(image_path)
    extracted_text = pytesseract.image_to_string(processed_image)
    return extracted_text


def extract_all_detected_words(image_path):
    text = extract_text_from_image(image_path)
    words = text.split()
    return words


def find_valid_dates(words):
    date_patterns = [
        r'\b(\d{2}-\d{2}-\d{4})\b',  # DD-MM-YYYY
        r'\b(\d{2}/\d{2}/\d{4})\b',  # DD/MM/YYYY
        r'\b(\d{2}-\d{2})\b',  # MM-YY
        r'\b(\d{2}/\d{2})\b'  # MM/YY
    ]

    found_dates = []

    for pattern in date_patterns:
        for word in words:
            matches = re.findall(pattern, word)
            found_dates.extend(matches)

    return found_dates


def filter_future_dates(dates):
    current_date = datetime.now()
    valid_dates = []

    for date_str in dates:
        date_obj = None  # Initialize date_obj
        try:
            if '-' in date_str:
                if len(date_str) == 7:  # DD-MM-YYYY
                    date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                elif len(date_str) == 5:  # MM-YY
                    date_obj = datetime.strptime(date_str + '-01', "%m-%y-%d")
            else:
                if len(date_str) == 10:  # DD/MM/YYYY
                    date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                elif len(date_str) == 5:  # MM/YY
                    date_obj = datetime.strptime(date_str + '/01', "%m/%y/%d")

            if date_obj and date_obj > current_date:
                valid_dates.append(date_str)

        except ValueError:
            continue

    return valid_dates


def search_for_expiration_indicators_and_dates(image_path):
    expiration_phrases = ["BY;", "BY:", "EXP", "DT.", "DT:", "DT;", "EXPIRY", "EXP", "BEST", "BEFORE;", "BEFORE:"]
    words = extract_all_detected_words(image_path)
    found_phrases = [phrase for phrase in expiration_phrases if phrase in words]

    if found_phrases:
        found_dates = find_valid_dates(words)
        future_dates = filter_future_dates(found_dates)
        return future_dates

    return []


# Test the function with an image
image_path = 'WhatsApp Image 2024-10-20 at 21.35.29_8116351e.jpg'
future_dates = search_for_expiration_indicators_and_dates(image_path)

print("Future Dates Found:")
print(future_dates)
