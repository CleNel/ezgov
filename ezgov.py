import requests
import os
import pdfplumber

from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

# Direct PDF link
url = "https://www.congress.gov/119/crec/2025/09/11/171/149/CREC-2025-09-11.pdf"

# Output directory and filename
out_dir = "daily_digest_pdfs"
os.makedirs(out_dir, exist_ok=True)
filename = os.path.join(out_dir, os.path.basename(url))
header_fraction = 0.26
width_fraction = 0.05
footer_fraction = 0.15
ncols = 3
header = True

def download_pdf(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in response.iter_content(1024):
                if chunk:
                    f.write(chunk)
        print(f"PDF downloaded successfully: {filename}")
    else:
        print(f"Failed to download. Status code: {response.status_code}")

def get_page_layout(page, hf = 0.1, wf = 0.05, ff = 0.15, ncols = 3):
    """Return layout info (header + column bounding boxes) for a given PDF page."""
    width, height = page.width, page.height

    # Margins
    margin = width * wf
    usable_x0 = margin
    usable_x1 = width - margin
    usable_width = usable_x1 - usable_x0

    # Header box (top strip of the page)
    header_height = height * hf
    header_bbox = (0, 0, width, header_height)

    # Column boxes (below header, split left-to-right)
    col_width = usable_width / ncols
    col_top = height * hf
    col_bot = height - (height * ff)
    col_bboxes = []
    for i in range(ncols):
        left = usable_x0 + (i * col_width)
        right = usable_x0 + ((i + 1) * col_width)
        bbox = (left, col_top, right, col_bot)
        col_bboxes.append(bbox)

    return {
        "width": width,
        "height": height,
        "header_bbox": header_bbox,
        "col_bboxes": col_bboxes,
    }

def preview_page_with_boxes(pdf_path, page_num=0, hf = 0.1, wf = 0.05, ff = 0.15, ncols = 3):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num]
        layout = get_page_layout(page, hf=hf, wf=wf, ff=ff, ncols=ncols)

        fig, ax = plt.subplots(1, figsize=(10, 14))
        img = page.to_image(resolution=150).original
        ax.imshow(img, cmap="gray", extent=[0, layout["width"], 0, layout["height"]])

        # Header
        if header:
            hb = layout["header_bbox"]
            ax.add_patch(Rectangle(
                (hb[0], page.height - hb[3]), hb[2] - hb[0], hb[3] - hb[1],
                linewidth=2, edgecolor='red', facecolor='none'
            ))

        # Columns
        for cb in layout["col_bboxes"]:
            ax.add_patch(Rectangle(
                (cb[0], page.height - cb[3]), cb[2] - cb[0], cb[3] - cb[1],
                linewidth=2, edgecolor='blue', facecolor='none'
            ))

        ax.set_title(f"Preview of Cropped Regions (Page {page_num+1})")
        ax.axis("off")
        plt.savefig(f"page{page_num+1}_preview.png", dpi=150, bbox_inches="tight")

def extract_first_page_with_header(pdf_path, hf = 0.26, wf = 0.05, ff = 0.15, ncols = 3):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        layout = get_page_layout(page, hf=hf, wf=wf, ff=ff, ncols=ncols)

        # --- Header text (force bbox orientation) ---
        if header:
            x0, y0, x1, y1 = layout["header_bbox"]
            header_text = page.crop((x0, y0, x1, y1)).extract_text() or ""

        # --- Column texts ---
        col_texts = []
        for bbox in layout["col_bboxes"]:
            x0, y0, x1, y1 = bbox
            bbox_norm = (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
            col_text = page.crop(bbox_norm).extract_text() or ""
            col_texts.append(col_text.strip())

        # Combine
        if header:
            full_text = header_text.strip() + "\n\n" + "\n\n".join(col_texts)
        else:
            full_text = col_texts

    # Save text
    text_file = os.path.splitext(pdf_path)[0] + "_page1_with_header.txt"
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"First page with header+columns saved to: {text_file}")
    return full_text

def extract_rest(pdf_path, hf = 0.05, wf = 0.05, ff = 0.15, ncols = 3):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for i, page in enumerate(pdf.pages[1:], start=1):
            layout = get_page_layout(page, hf=hf, wf=wf, ff=ff, ncols=ncols)

            # --- Header text (force bbox orientation) ---
            if header:
                x0, y0, x1, y1 = layout["header_bbox"]
                header_text = page.crop((x0, y0, x1, y1)).extract_text() or ""

            # --- Column texts ---
            col_texts = []
            for bbox in layout["col_bboxes"]:
                x0, y0, x1, y1 = bbox
                bbox_norm = (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
                col_text = page.crop(bbox_norm).extract_text() or ""
                col_texts.append(col_text.strip())

            # Combine
            if header:
                full_text = full_text + f"PAGE {i+1}" + "\n\n" + "\n\n".join(col_texts) + "\n\n"
            else:
                full_text = col_texts

    # Save text
    text_file = os.path.splitext(pdf_path)[0] + "_rest.txt"
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"Rest of the text saved to: {text_file}")
    return full_text

if __name__ == "__main__":
    # Step 1: Download PDF
    download_pdf(url, filename)

    # Step 2: Preview the first page with header/column boxes
    preview_page_with_boxes(filename, page_num=0, hf=0.26)
    preview_page_with_boxes(filename, page_num=1, hf=0.045, ff=0.04)
    print("Preview image saved as page_preview.png")

    # Step 3: Extract text from first page
    # HeaderText = extract_first_page_with_header(filename)
    #RestText = extract_rest(filename)
    #print("Extracted text:\n")
    #print(HeaderText[:500])  # show first 500 chars for sanity check
