import re

def extract_key_info(file_content):
    # 定义正则表达式
    predicted_function_pattern = r'Gene\s+\*+(Ghir_[A-Z0-9]+)\*+\s+is predicted to function as a\s+\*+(.*?)\*+'
    homolog_gene_pattern = r'Arabidopsis homolog \(AT(\d+G\d+)\):.*?encodes\s+\*+(.*?)\*+'
    homolog_function_pattern = r'known to regulate \*+(.*?)\*+'
    high_expression_pattern = r'(\w+)[ ]*\((\d+\.\d+)[DPA:]?\)[ ]*:.*?high expression'
    moderate_expression_pattern = r'fiber tissues[ ]*\(10DPA: (\d+\.\d+); 20DPA: (\d+\.\d+)\)[ ]*;'
    coexpression_gene_pattern = r'Ghir_[A-Z]{02}G\d{9}'  # 假设共表达基因名称格式为 Ghir_XXGXXXXXXX
    blast_similarity_pattern = r'Ghir_[A-Z]{02}G\d{9} \((\d+\.\d+)%\)'
    final_prediction_pattern = r'Gene\s+\*+(Ghir_[A-Z0-9]+)\*+\s+is a\s+\*+(.*?)\*+'

    # 提取预测功能
    predicted_function = re.findall(predicted_function_pattern, file_content, re.S)

    # 提取同源基因名称和功能
    homolog_genes = re.findall(homolog_gene_pattern, file_content, re.S)
    homolog_functions = re.findall(homolog_function_pattern, file_content, re.S)

    # 提取高表达组织
    high_expressions = re.findall(high_expression_pattern, file_content, re.S)

    # 提取适度表达的纤维组织
    moderate_expressions = re.findall(moderate_expression_pattern, file_content, re.S)

    # 提取共表达基因名称
    coexpression_genes = re.findall(coexpression_gene_pattern, file_content)

    # 提取BLAST相似度数据中的高相似度基因名称和相似度百分比
    blast_similarities = re.findall(blast_similarity_pattern, file_content)

    # 提取最终预测中的功能
    final_predictions = re.findall(final_prediction_pattern, file_content, re.S)

    # 整理提取的信息
    keywords = {
        'Predicted Function': predicted_function,
        'Homolog Genes': homolog_genes,
        'Homolog Functions': homolog_functions,
        'High Expression Tissues': high_expressions,
        'Moderate Expression in Fiber Tissues': moderate_expressions,
        'Coexpression Genes': coexpression_genes,
        'BLAST Similarity Genes': blast_similarities,
        'Final Prediction': final_predictions
    }

    return keywords

# 读取文件内容
with open('1.txt', 'r', encoding='utf-8') as file:
    file_content = file.read()

# 提取关键词
key_info = extract_key_info(file_content)

# 打印提取的关键词
for key, value in key_info.items():
    print(f"{key}: {value}")