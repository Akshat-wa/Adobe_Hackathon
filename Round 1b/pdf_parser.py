import fitz  # PyMuPDF

def parse_pdf(filepath):
    doc = fitz.open(filepath)
    sections = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            for line in b.get("lines", []):
                span_texts = [s["text"] for s in line["spans"] if len(s["text"].strip()) > 5]
                if not span_texts:
                    continue
                text = " ".join(span_texts).strip()
                if 10 < len(text) < 300:
                    sections.append({
                        "document": filepath.split("/")[-1],
                        "page_number": page_num + 1,
                        "section_title": text[:120],
                        "text": text
                    })
    return sections
