import json, logging, re, time, unicodedata, collections
from pathlib import Path
import fitz
import numpy as np
from sklearn.cluster import KMeans
import jsonschema

BaseDir = Path(__file__).parent
InputDir = Path("/app/input")
OutputDir = Path("/app/output")
SchemaPath = BaseDir / "schema" / "output_schema.json"

NumLevels = 3
AllowedLevels = {"H1", "H2", "H3"}
MinChars = 4
MaxChars = 70
MaxWords = 10
TitleMinWords = 2
CapsOkWords = 2
MaxPerSize = 6

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

Schema = json.loads(Path(SchemaPath).read_text("utf-8"))

def CleanText(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).replace("\u00AD", "")
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\b([A-Za-z])\s+([A-Za-z]+)", r"\1\2", text)
    return text.strip(" \t\n–—-:•.")

def ExtractLines(pdf: Path):
    doc = fitz.open(str(pdf))
    lines = []
    for pageIdx, page in enumerate(doc):
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for ln in block["lines"]:
                line_text = " ".join([sp["text"] for sp in ln["spans"]]).strip()
                if not line_text:
                    continue
                span = ln["spans"][0]
                lines.append({
                    "text": line_text,
                    "size": round(span["size"]),
                    "font": span["font"],
                    "bold": "Bold" in span["font"],
                    "caps": sum(map(str.isupper, line_text)),
                    "words": line_text.count(" "),
                    "page": pageIdx + 1
                })
    return lines

def ClusterLines(lines):
    sizes = np.array([line["size"] for line in lines]).reshape(-1, 1)
    clusters = KMeans(n_clusters=min(NumLevels + 1, len(set(sizes.flatten())))).fit(sizes)
    centers = sorted(set(clusters.cluster_centers_.flatten()), reverse=True)[:NumLevels]
    levels = {s: f"H{idx + 1}" for idx, s in enumerate(centers)}
    for line, label in zip(lines, clusters.labels_):
        size = clusters.cluster_centers_[label][0]
        line["level"] = levels.get(size)
    return lines

def IsTitle(text): return text and len(text.split()) >= TitleMinWords

def GenerateOutput(lines):
    headings = [l for l in lines if l["level"] in AllowedLevels and MinChars <= len(l["text"]) <= MaxChars and l["words"] <= MaxWords]
    if not headings:
        return {"title": "", "outline": []}
    headings = sorted(headings, key=lambda l: (l["page"], l["level"]))
    title = next((l["text"] for l in headings if IsTitle(l["text"])), "")
    outline = [{"level": l["level"], "text": l["text"], "page": l["page"]} for l in headings]
    return {"title": title, "outline": outline}

def main():
    InputDir.mkdir(parents=True, exist_ok=True)
    OutputDir.mkdir(parents=True, exist_ok=True)
    for pdf_file in InputDir.glob("*.pdf"):
        try:
            logging.info(f"Processing {pdf_file.name}")
            lines = ExtractLines(pdf_file)
            clustered = ClusterLines(lines)
            result = GenerateOutput(clustered)
            jsonschema.validate(result, Schema)
            output_path = OutputDir / pdf_file.with_suffix(".json").name
            output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        except Exception as e:
            logging.error(f"Failed to process {pdf_file.name}: {e}")

if __name__ == "__main__":
    main()
