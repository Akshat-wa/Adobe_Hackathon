from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def rank_sections(sections, persona, job):
    query = f"{persona}. Task: {job}"
    q_embed = model.encode(query, convert_to_tensor=True)

    for section in sections:
        section_embed = model.encode(section["text"], convert_to_tensor=True)
        section["score"] = util.cos_sim(q_embed, section_embed).item()

    return sorted(sections, key=lambda x: x["score"], reverse=True)

def extract_subsections(top_sections, persona, job):
    query = f"{persona}. Task: {job}"
    q_embed = model.encode(query, convert_to_tensor=True)
    refined = []

    for sec in top_sections:
        paras = sec["text"].split(". ")
        for para in paras:
            para = para.strip()
            if len(para) > 80:
                para_embed = model.encode(para, convert_to_tensor=True)
                score = util.cos_sim(q_embed, para_embed).item()
                if score > 0.3:
                    refined.append({
                        "document": sec["document"],
                        "refined_text": para,
                        "page_number": sec["page_number"]
                    })
    return refined
