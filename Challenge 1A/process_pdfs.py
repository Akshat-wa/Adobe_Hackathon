import json, logging, re, time, unicodedata, collections
from pathlib import Path
import fitz
import numpy as np
from sklearn.cluster import KMeans
import jsonschema

BaseDir          = Path(__file__).parent
InputDir         = BaseDir / "inputs"
OutputDir        = BaseDir / "outputs"
SchemaPath       = BaseDir / "schema" / "output_schema.json"

NumLevels        = 3
AllowedLevels    = {"H1", "H2", "H3"}
MinChars         = 4
MaxChars         = 70
MaxWords         = 10
TitleMinWords    = 2
CapsOkWords      = 2
MaxPerSize       = 6

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
                raw = " ".join(s["text"].strip() for s in ln["spans"]).strip()
                if not raw:
                    continue
                txt = CleanText(raw)
                if not txt:
                    continue
                size = max(s.get("size", 0) for s in ln["spans"])
                lines.append({"page": pageIdx, "size": float(size), "text": txt})
    return lines

def MapSizesToLevels(sizes):
    uniq = sorted(set(sizes))
    if len(uniq) <= NumLevels:
        return {s: f"H{min(i+1, NumLevels)}" for i, s in enumerate(sorted(uniq, reverse=True))}
    km = KMeans(n_clusters=NumLevels, random_state=42).fit(np.array(uniq).reshape(-1, 1))
    centers = km.cluster_centers_.flatten()
    order = np.argsort(-centers)
    labelToLevel = {lbl: f"H{idx+1}" for idx, lbl in enumerate(order)}
    return {s: labelToLevel[lbl] for s, lbl in zip(uniq, km.labels_)}

def PromoteSecond(sizeMap, lines):
    ordered = sorted(sizeMap, reverse=True)
    if len(ordered) < 2:
        return sizeMap
    largest, second = ordered[0], ordered[1]
    if sum(1 for ln in lines if ln["size"] == largest) == 1:
        for sz in sizeMap:
            if sz == second and sizeMap[sz] == "H2":
                sizeMap[sz] = "H1"
            elif sizeMap[sz] == "H3":
                sizeMap[sz] = "H2"
    return sizeMap

_TableTokens = {"s.no", "age", "relationship", "name", "date", "signature"}

def LooksTableLabel(text: str) -> bool:
    if text.lower().rstrip(":") in _TableTokens:
        return True
    if text.endswith(":"):
        return True
    if re.match(r"^\d+[\.\)]\s", text):
        return True
    return False

def IsHeading(text: str) -> bool:
    if LooksTableLabel(text):
        return False
    if not (MinChars <= len(text) <= MaxChars):
        return False
    if len(text.split()) > MaxWords:
        return False
    if not re.search(r"[A-Za-z]", text):
        return False
    if text.upper() == text:
        if re.search(r"\d", text) or len(text.split()) < CapsOkWords:
            return False
    if re.search(r"\d", text) and not re.match(r"^\d+(\.\d+)*\s", text):
        return False
    return True

def ExtractOutline(pdf: Path):
    lines = ExtractLines(pdf)
    if not lines:
        return {"title": "", "outline": []}
    sizeCounts = collections.Counter((ln["page"], ln["size"]) for ln in lines)
    candidates = [ln for ln in lines if sizeCounts[(ln["page"], ln["size"])] <= MaxPerSize]
    sizeMap = MapSizesToLevels([ln["size"] for ln in candidates])
    sizeMap = PromoteSecond(sizeMap, candidates)
    headings = [{"level": sizeMap[ln["size"]], "text": ln["text"], "page": ln["page"]} for ln in candidates if ln["size"] in sizeMap]
    firstH1 = next((h["text"] for h in headings if h["level"] == "H1" and h["page"] == 0), "")
    title = firstH1 if len(firstH1.split()) >= TitleMinWords else ""
    freq = collections.Counter(h["text"] for h in headings)
    outline = [h for h in headings if h["level"] in AllowedLevels and freq[h["text"]] == 1 and IsHeading(h["text"]) and not (h["level"] == "H1" and h["text"] == firstH1 and h["page"] == 0)]
    return {"title": title, "outline": outline}

def Validate(data): jsonschema.validate(data, Schema)

def ProcessAll():
    OutputDir.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(InputDir.glob("*.pdf"))
    if not pdfs:
        logging.warning("No PDFs found")
        return
    times = []
    for pdf in pdfs:
        start = time.perf_counter()
        try:
            res = ExtractOutline(pdf)
            Validate(res)
            (OutputDir / f"{pdf.stem}.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), "utf-8")
            times.append(time.perf_counter() - start)
            logging.info("✓ %s (%.2fs)", pdf.name, times[-1])
        except Exception as e:
            logging.error("✗ %s: %s", pdf.name, e)
    if times:
        logging.info("Processed %d PDFs, avg %.2fs", len(times), sum(times) / len(times))

if __name__ == "__main__":
    logging.info("Starting PDF outline extraction")
    ProcessAll()
    logging.info("Done")