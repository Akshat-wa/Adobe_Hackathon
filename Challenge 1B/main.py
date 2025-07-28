import os
import json
from pdf_parser import parse_pdf
from relevance_ranker import rank_sections, extract_subsections
from utils import load_input_spec, get_timestamp

def process_collection(collection_dir):
    input_path = os.path.join(collection_dir, "challenge1b_input.json")
    output_path = os.path.join(collection_dir, "challenge1b_output.json")
    pdf_dir = os.path.join(collection_dir, "PDFs")

    persona, job, document_list = load_input_spec(input_path)

    all_sections = []
    for filename in document_list:
        filepath = os.path.join(pdf_dir, filename)
        all_sections.extend(parse_pdf(filepath))

    ranked = rank_sections(all_sections, persona, job)
    top5 = ranked[:5]
    refined = extract_subsections(top5, persona, job)

    output = {
        "metadata": {
            "input_documents": document_list,
            "persona": persona,
            "job_to_be_done": job,
            "timestamp": get_timestamp()
        },
        "extracted_sections": [
            {
                "document": s["document"],
                "section_title": s["section_title"],
                "importance_rank": i + 1,
                "page_number": s["page_number"]
            } for i, s in enumerate(top5)
        ],
        "subsection_analysis": refined
    }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Output written to {output_path}")

def main():
    base_dir = "/app/input"
    for collection_name in os.listdir(base_dir):
        collection_path = os.path.join(base_dir, collection_name)
        if os.path.isdir(collection_path) and os.path.exists(os.path.join(collection_path, "challenge1b_input.json")):
            process_collection(collection_path)

if __name__ == "__main__":
    main()
