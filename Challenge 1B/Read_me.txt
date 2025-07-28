
## 🛠 How to Build and Run

### 1. Build Docker Image:
docker build --platform linux/amd64 -t mysolution:abc123 . (BASH)

###2.How to Run:
docker run --rm -v $(pwd)/input:/app/input --network none mysolution:abc123   (BASH)

Output is written to challenge1b_output.json inside each collection.

📦 Constraints
1.Model size: ~80MB (MiniLM)
2.No internet access during runtime
3.Offline-compatible
4.CPU-only


Output Format:
{
  "metadata": { ... },
  "extracted_sections": [ ... ],
  "subsection_analysis": [ ... ]
}







# Approach Explanation – Adobe Round 1B

## 📌 Problem
Given a collection of PDFs and a user persona + task, extract and rank the most relevant document sections and sub-sections.

## 🔍 Methodology

### 1. Text Extraction
Used PyMuPDF to extract paragraph-like blocks from PDFs. We filtered short or noisy lines and preserved page structure.

### 2. Section Ranking
Used the `all-MiniLM-L6-v2` sentence transformer to encode:
- Persona + task prompt
- Each PDF paragraph

Cosine similarity determined relevance scores. Top-5 paragraphs were selected based on this ranking.

### 3. Sub-section Extraction
For each top section, we semantically chunked the content using sentence splitting. Each sub-chunk was re-ranked using the same query. A threshold of 0.3 was used to filter relevant insights.

## 📦 Offline Support
All models are downloaded during Docker build. Runtime is offline-only (`--network none`).

## 📊 Why It Works
This solution generalizes across domains due to embedding-based semantic matching, making it robust to both narrative documents (like travel guides) and technical reports (like research papers).

## 💡 Possible Improvements
- Add visual layout signals (font size, bold, etc.) to weight headings
- Use document chunking with overlap for longer paragraphs
- Add deduplication across overlapping content
