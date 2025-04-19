from nltk.translate.bleu_score import sentence_bleu, corpus_bleu
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

# 清洗文本数据，去除Markdown格式标记
def clean_text(text):
    # 去除粗体标记和其他不必要的符号
    cleaned_text = re.sub(r'\*\*|$|$|$|$|\-', '', text)
    return cleaned_text.strip()

# 计算BLEU评分
def calculate_bleu(reference, candidate):
    reference = [clean_text(reference).split()]
    candidate = clean_text(candidate).split()
    score = sentence_bleu(reference, candidate, weights=(0.5, 0.5))
    return score

# 打印BLEU评分
def print_bleu_scores(baseline, candidate, title):
    bleu_score = calculate_bleu(baseline, candidate)
    print(f"\n{title}:\nBLEU Score: {bleu_score:.4f}")

# 对比 Predicted Function and Traits 部分
print("Using 1.txt as baseline:")
print_bleu_scores(predicted_function_1, predicted_function_2, "Predicted Function and Traits (1.txt vs 2.txt)")
print_bleu_scores(final_prediction_1, conclusion_2, "Final Prediction (1.txt vs 2.txt Conclusion)")

print("\nUsing 2.txt as baseline:")
print_bleu_scores(predicted_function_2, predicted_function_1, "Predicted Function and Traits (2.txt vs 1.txt)")
print_bleu_scores(conclusion_2, final_prediction_1, "Final Prediction (2.txt Conclusion vs 1.txt)")