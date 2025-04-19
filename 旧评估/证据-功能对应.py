import re
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import numpy as np

# 加载预训练的Sentence-BERT模型
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


def calculate_similarity(evidence, prediction):
    # 计算两个文本之间的余弦相似度并打印调试信息
    print(f"Calculating similarity between:\nEvidence: {evidence}\nPrediction: {prediction}")
    embeddings = model.encode([evidence, prediction], convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(embeddings[0], embeddings[1])
    score = cosine_scores.item()
    print(f"Similarity score: {score}")
    return score


def extract_info(text):
    # 正则表达式匹配每个证据部分及其描述
    pattern_section = r"####\s*\*\*(.*?)\*\*:\n(.*?)(?=####|\Z)"
    pattern_description = r"- \*\*(.*?)\*\*(?:\s*$(.*?)$)?(?:\s*(--.*)?)?"

    evidence_dict = {}
    matches = list(re.finditer(pattern_section, text, re.DOTALL | re.MULTILINE))
    print(f"Found {len(matches)} sections.")  # 打印找到的段落数量

    for match in matches:
        section_title = match.group(1).strip()
        descriptions = [m.group(1).strip() for m in
                        re.finditer(pattern_description, match.group(2), re.DOTALL | re.MULTILINE)]
        print(f"Section: {section_title}, Descriptions: {descriptions}")  # 打印每个段落及其描述

        if descriptions:
            evidence_dict[section_title] = descriptions

    final_predictions = [
        "Negative regulation of ABA signaling",
        "Involvement in abiotic stress responses (e.g., drought tolerance)",
        "Participation in root development and stress adaptation mechanisms",
        "Roles in early seed development and structural growth",
        "Function in early stages of fiber development"
    ]

    return evidence_dict, final_predictions


def generate_table(evidence_dict, final_predictions):
    data = []
    similarities = []

    for section, descriptions in evidence_dict.items():
        for desc in descriptions:
            max_similarity = 0.0
            best_match = ""
            for pred in final_predictions:
                similarity = calculate_similarity(desc, pred)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = pred
            data.append([section, desc, best_match, round(max_similarity, 4)])
            similarities.append(max_similarity)

    df = pd.DataFrame(data,
                      columns=["Evidence Type", "Evidence Function Description", "Final Prediction Correspondence",
                               "SBERT Similarity Score"])

    # 添加平均值行
    if not df.empty:
        avg_similarity = round(np.mean(similarities), 4)
        avg_row = pd.DataFrame([["Average", "", "", avg_similarity]],
                               columns=["Evidence Type", "Evidence Function Description", "Final Prediction Correspondence",
                                        "SBERT Similarity Score"])
        df = pd.concat([df, avg_row], ignore_index=True)

    return df


if __name__ == "__main__":
    with open("1.txt", "r", encoding="utf-8") as file:
        content = file.read()
        print("File content preview:")
        print(content[:500])  # 打印文件开头部分内容以确认其格式

    # Extract information from the content
    evidence_dict, final_predictions = extract_info(content)

    # Generate the table
    table = generate_table(evidence_dict, final_predictions)

    if not table.empty:
        print("\nGenerated Table:")
        print(table.to_markdown(index=False))
    else:
        print("No data to display.")