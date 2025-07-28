# Adobe Hackathon Round 1A – PDF Outline Extractor

## Overview

This solution extracts structured outlines (Title, H1, H2, H3 headings with page numbers) from PDFs.

## Docker Build & Run

### Build the Docker image

(BASH)
docker build --platform linux/amd64 -t mysolution:abc123 .


How to run? -->  (BASH)
docker run --rm -v "${PWD}\input:/app/input" -v "${PWD}\output:/app/output" --network none mysolution:abc123



Output Schema:
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}


Tech Used:
1.Python 3.10
2.PyMuPDF for PDF parsing
3.scikit-learn for heading clustering
4.jsonschema for output validation
5.Docker (cross-platform, no internet, CPU-only)


🧩 How It Works
1.Extracts all visible text lines from PDFs using PyMuPDF
2.Cleans and normalizes lines
3.Clusters lines by font size to estimate heading levels
4.Selects meaningful headings based on heuristics
5.Validates final JSON using provided schema

