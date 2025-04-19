from rouge import Rouge

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

# 计算 ROUGE 评分
rouge = Rouge()


def print_rouge_scores(candidate, reference, title):
    if not candidate or not reference:
        print(f"Skipping ROUGE calculation for {title} because either the candidate or reference text is empty.")
        return

    scores = rouge.get_scores(candidate, reference)[0]
    print(f"\n{title}:\n")
    for metric, score in scores.items():
        print(f"{metric}: Precision: {score['p']:.4f}, Recall: {score['r']:.4f}, F1: {score['f']:.4f}")


# 对比 Predicted Function and Traits 部分
print("Using 1.txt as baseline:")
print_rouge_scores(predicted_function_2, predicted_function_1, "Predicted Function and Traits (1.txt vs 2.txt)")
print_rouge_scores(final_prediction_1, conclusion_2, "Final Prediction (1.txt vs 2.txt Conclusion)")

print("\nUsing 2.txt as baseline:")
print_rouge_scores(predicted_function_1, predicted_function_2, "Predicted Function and Traits (2.txt vs 1.txt)")
print_rouge_scores(conclusion_2, final_prediction_1, "Final Prediction (2.txt Conclusion vs 1.txt)")