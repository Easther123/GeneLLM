import os
import csv
from sentence_transformers import SentenceTransformer, util

# 初始化预训练模型
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# 定义文件路径
folder_path = r'C:\Users\29901\PycharmProjects\GeneLLM\2015111评估\棉花（分给zy的）'
go_csv_path = os.path.join(folder_path, 'GO.csv')
output_folder = os.path.join(folder_path, '结果2')

# 创建输出文件夹（如果不存在）
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 读取CSV文件并创建一个字典存储GO信息
go_dict = {}
with open(go_csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        go_dict[row['GeneID']] = {'GO': row['GO'], 'Description': row['Description']}


# 数据规范化函数
def normalize(text):
    return text.strip().lower() if text else text


# 计算语义相似度
def semantic_similarity(desc1, desc2):
    embeddings1 = model.encode(desc1, convert_to_tensor=True)
    embeddings2 = model.encode(desc2, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(embeddings1, embeddings2)
    return cosine_scores.item()


# 设置相似度阈值
similarity_threshold = 0.7

# 处理每个.txt文件
for txt_file in [f for f in os.listdir(folder_path) if f.endswith('.txt')]:
    gene_name = txt_file.split('.')[0]
    tp, fp, fn = 0, 0, 0

    # 读取txt文件内容
    with open(os.path.join(folder_path, txt_file), 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 获取CSV文件中对应基因的GO信息
    ref_go_info = go_dict.get(gene_name, None)

    if ref_go_info is None:
        print(f"Warning: Gene {gene_name} not found in GO.csv")
        continue

    ref_go_id = normalize(ref_go_info['GO'])
    ref_description = normalize(ref_go_info['Description'])

    # 遍历每一行并计算TP, FP, FN
    for line in lines:
        parts = line.strip().split(' - ')
        if len(parts) != 2:
            print(f"Warning: Invalid format in line: {line}")
            continue

        go_id, description = parts
        go_id = normalize(go_id)
        description = normalize(description)

        similarity_score = semantic_similarity(description, ref_description)
        print(
            f"Comparing {go_id} - {description} with {ref_go_id} - {ref_description}, Similarity: {similarity_score:.2f}")  # Debugging line

        # 尝试语义相似度匹配
        if similarity_score >= similarity_threshold:
            tp += 1
        # 如果描述不匹配，尝试匹配GO ID
        elif go_id == ref_go_id:
            fp += 1
        else:
            fn += 1

    # 计算Precision, Recall
    try:
        precision = tp / (tp + fp)
    except ZeroDivisionError:
        precision = 0

    try:
        recall = tp / (tp + fn)
    except ZeroDivisionError:
        recall = 0

    # AUC计算通常需要概率估计值，这里可能无法直接计算，因此省略
    auc = "N/A"

    # 输出结果到文件
    output_file_path = os.path.join(output_folder, f'{gene_name}_result.txt')
    with open(output_file_path, 'w', encoding='utf-8') as result_file:
        result_file.write(f'TP: {tp}, FP: {fp}, FN: {fn}\n')
        result_file.write(f'Precision: {precision:.2f}, Recall: {recall:.2f}, AUC: {auc}\n')
        result_file.write(f'Similarity Threshold: {similarity_threshold}\n')

print("处理完成")