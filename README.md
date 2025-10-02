# EZGov – US Senate Daily Digest Extractor

This project downloads the **United States Senate Daily Digest** PDFs from congress.gov, 
previews their layout (header + multi-column text), and extracts text from the first page 
into a machine-readable format.

---

## Features

- 📥 **Automatic PDF download** from congress.gov
- 🖼 **Visual page preview** with header and column bounding boxes
- ✂ **Text extraction** by header + column layout
- 💾 Saves extracted text to `.txt` files for further processing
- 🐍 Written in pure Python with `pdfplumber` and `requests`

---

## Example Workflow

1. **Download the PDF**
   - The script fetches a Daily Digest PDF directly from congress.gov.

2. **Preview the layout**
   - Generates a PNG (`page_preview.png`) with red box for the header 
     and blue boxes for columns.

3. **Extract text**
   - Reads header text left-to-right, then processes each column top-to-bottom.
   - Output is saved in `<filename>_page1_with_header.txt`.

---

## Requirements

- Python 3.8+
- Virtual environment (recommended)

### Install dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` should contain:

```
requests
pdfplumber
matplotlib
```

---

## Usage

Clone the repository and run:

```bash
python ezgov.py
```

This will:

1. Download the specified Daily Digest PDF  
2. Save the preview image as `page_preview.png`  
3. Save the extracted text file next to the PDF  

---

## Project Structure

```
.
├── ezgov.py               # Main script
├── daily_digest_pdfs/     # Downloaded PDFs + extracted text
├── page_preview.png       # Example preview with bounding boxes
├── requirements.txt       # Dependencies
└── README.md              # This file
```

---

## Next Steps

- Extend parsing to multiple pages  
- Store extracted text in a database (SQLite/Postgres)  
- Add CLI options for different dates/issues  
- Automate daily retrieval  

---

## License

MIT License – see [LICENSE](LICENSE) for details.
