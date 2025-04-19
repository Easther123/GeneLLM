from sentence_transformers import SentenceTransformer, util

# 初始化预训练的Sentence-BERT模型
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


def calculate_semantic_similarity(text1, text2):
    # 将文本编码为向量
    embeddings = model.encode([text1, text2], convert_to_tensor=True)

    # 计算余弦相似度
    cosine_similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])

    return cosine_similarity.item()


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

# 计算并打印每对文本片段的语义相似度分数
similarity_pf1_pf2 = calculate_semantic_similarity(predicted_function_1, predicted_function_2)
similarity_fp1_c2 = calculate_semantic_similarity(final_prediction_1, conclusion_2)

print(f"Semantic Similarity between predicted_function_1 and predicted_function_2: {similarity_pf1_pf2:.4f}")
print(f"Semantic Similarity between final_prediction_1 and conclusion_2: {similarity_fp1_c2:.4f}")