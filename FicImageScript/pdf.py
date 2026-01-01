import fitz  # PyMuPDF
import requests
from PIL import Image
from io import BytesIO
import re


def download_image(url):
    """Downloads an image and returns its bytes."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        return response.content
    raise Exception(f"Failed to download image from {url}")


def insert_image_with_aspect_ratio(page, rect, image_bytes):
    """Inserts an image into a PDF page while preserving aspect ratio."""
    # Get the dimensions of the placeholder
    placeholder_width = rect.width
    placeholder_height = rect.height

    # Open the image with PIL to get its size
    image = Image.open(BytesIO(image_bytes))
    img_width, img_height = image.size

    # Calculate the new dimensions to fit the placeholder
    aspect_ratio = img_width / img_height
    if placeholder_width / placeholder_height > aspect_ratio:
        # Scale based on height
        new_width = placeholder_height * aspect_ratio
        new_height = placeholder_height
    else:
        # Scale based on width
        new_width = placeholder_width
        new_height = placeholder_width / aspect_ratio

    # Center the image within the placeholder
    x0 = rect.x0 + (placeholder_width - new_width) / 2
    y0 = rect.y0 + (placeholder_height - new_height) / 2
    x1 = x0 + new_width
    y1 = y0 + new_height
    new_rect = fitz.Rect(x0, y0, x1, y1)

    # Insert the image
    page.insert_image(new_rect, stream=image_bytes)
    print(f"Image inserted at {new_rect}.")


def update_pdf(file_path):
    print(f"Updating PDF: {file_path}")
    # Open the PDF
    doc = fitz.open(file_path)

    # Placeholder pattern
    placeholder_pattern = r"\[img:\s*(https?://\S+)\]"

    # Iterate through the pages
    for page_number in range(len(doc)):
        page = doc[page_number]
        text = page.get_text()

        # Find placeholders
        matches = re.findall(placeholder_pattern, text)
        if matches:
            for url in matches:
                try:
                    # Download image
                    image_bytes = download_image(url)

                    # Find the placeholder location
                    placeholders = page.search_for("[img:")

                    # Or search for the exact match
                    for rect in placeholders:
                        insert_image_with_aspect_ratio(page, rect, image_bytes)

                        # Optionally remove the placeholder text
                        page.add_redact_annot(rect, fill=(1, 1, 1))  # White-out the placeholder
                        page.apply_redactions()

                except Exception as e:
                    print(f"Error processing {url}: {e}")

    # Save the modified PDF
    doc.save("updated.pdf")
    print("PDF updated and saved as 'updated.pdf'.")
