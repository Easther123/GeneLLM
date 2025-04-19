from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import re

# 提供的文本片段
predicted_function_1 = """
Gene **Ghir_A02G007610** is predicted to function as a **transcriptional regulator involved in abiotic stress responses (e.g., drought tolerance) and developmental processes (e.g., fiber development)**. Specifically, it likely plays a role in **negative regulation of abscisic acid (ABA) signaling**, a key hormonal pathway during stress adaptation, and **auxin-mediated signaling in fiber tissues**. This prediction is supported by homologous gene data, tissue-specific expression patterns, co-expression networks, and Gene Ontology (GO) annotations.
"""

predicted_function_2 = """
Gene **Ghir_A02G007610** is predicted to be a **transcriptional regulator involved in abiotic stress response, particularly drought tolerance, and developmental processes such as fiber differentiation and root development**. This prediction is supported by:
- Homology with Arabidopsis NAC transcription factors (e.g., ATAF1/ANAC002), which are known to regulate stress responses and ABA signaling.
- Tissue-specific expression patterns showing high activity in roots, cotyledons, and stems, suggesting roles in stress adaptation and early development.
- GO annotations indicating involvement in transcriptional regulation and DNA binding.
"""

final_prediction_1 = """
Gene **Ghir_A02G007610** is a **NAC transcription factor** involved in **negative regulation of ABA signaling** and **transcriptional reprogramming** during abiotic stress (e.g., drought tolerance). It also plays a role in **fiber development** and **reproductive processes**. The gene's high expression in root, cotyledon, and stem tissues supports its role in developmental processes, while its co-expression with carbohydrate metabolic genes suggests involvement in energy homeostasis during stress.
"""

conclusion_2 = """
**Ghir_A02G007610** is predicted to function as a **NAC transcription factor involved in abiotic stress response (e.g., drought tolerance) and developmental processes (e.g., root and fiber differentiation)**. This prediction is supported by homologous gene functions, tissue-specific expression patterns, co-expression networks, and GO annotations. External validation from STRING and PlantTFDB further strengthens the hypothesis, highlighting the gene's role in transcriptional regulation under stress and developmental conditions.
"""

# 创建模板文本
template_predicted_function = """
Gene Ghir_A02G007610 is predicted to function as a transcriptional regulator involved in abiotic stress responses, particularly drought tolerance, and developmental processes such as fiber development and root differentiation. Specifically:

- **Stress Response**: It plays a role in the negative regulation of abscisic acid (ABA) signaling, which is a key hormonal pathway during stress adaptation. Additionally, it contributes to auxin-mediated signaling in fiber tissues.
- **Developmental Processes**: The gene is implicated in fiber development and root differentiation, with high expression levels observed in roots, cotyledons, and stems, indicating significant participation in developmental events.
- **Molecular Mechanism**: Homology with Arabidopsis NAC transcription factors (e.g., ATAF1/ANAC002) supports its classification as a NAC transcription factor. Co-expression networks and tissue-specific expression patterns further validate its role in transcriptional regulation under stress conditions.
- **Supporting Evidence**: Predictions are reinforced by homologous gene functions, tissue-specific expression data, co-expression networks, and Gene Ontology (GO) annotations. External validation from databases like STRING and PlantTFDB strengthens the hypothesis regarding its functional significance.
"""

template_final_prediction = """
Gene Ghir_A02G007610 is a NAC transcription factor involved in the negative regulation of ABA signaling and transcriptional reprogramming during abiotic stress, specifically drought tolerance. It also plays a role in fiber development and reproductive processes. High expression in root, cotyledon, and stem tissues supports its role in developmental processes. Co-expression with carbohydrate metabolic genes suggests involvement in energy homeostasis during stress. This prediction is supported by:
- Homology with Arabidopsis NAC transcription factors (e.g., ATAF1/ANAC002), which regulate stress responses and ABA signaling.
- Tissue-specific expression patterns showing high activity in roots, cotyledons, and stems, suggesting roles in stress adaptation and early development.
- GO annotations indicating involvement in transcriptional regulation and DNA binding.
External validation from databases like STRING and PlantTFDB further strengthens the hypothesis.
"""

# 清洗文本数据，去除Markdown格式标记
def clean_text(text):
    cleaned_text = re.sub(r'\*\*|$|$|$|$|\-', '', text)
    return cleaned_text.strip()

# 计算BLEU评分
def calculate_bleu(reference, candidate, weights=(0.25, 0.25, 0.25, 0.25)):
    reference = [clean_text(reference).split()]
    candidate = clean_text(candidate).split()
    smoothing = SmoothingFunction().method1  # 使用平滑函数以避免零分
    score = sentence_bleu(reference, candidate, weights=weights, smoothing_function=smoothing)
    return score

# 打印BLEU评分
def print_bleu_scores(template, candidate, title):
    bleu_score_template = calculate_bleu(template, candidate)
    print(f"\n{title}:\nTemplate BLEU Score: {bleu_score_template:.4f}")

# 对比 Predicted Function and Traits 部分
print("Comparing 1.txt against template:")
print_bleu_scores(template_predicted_function, predicted_function_1, "Predicted Function and Traits (1.txt vs Template)")

print("\nComparing 2.txt against template:")
print_bleu_scores(template_predicted_function, predicted_function_2, "Predicted Function and Traits (2.txt vs Template)")

# 对比 Final Prediction 部分
print("\nComparing 1.txt Final Prediction against template:")
print_bleu_scores(template_final_prediction, final_prediction_1, "Final Prediction (1.txt vs Template)")

print("\nComparing 2.txt Conclusion against template:")
print_bleu_scores(template_final_prediction, conclusion_2, "Final Prediction (2.txt Conclusion vs Template)")