import pandas as pd
from sklearn.metrics import precision_score, recall_score, roc_auc_score
from sentence_transformers import SentenceTransformer, util
import re


def extract_go_terms_from_file(file_path):
    """从给定的文本文件中提取GO术语和描述"""
    go_terms = []
    pattern = r'(\bGO:\d{7}\b) $([^)]+)$: (.*)'

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        matches = re.findall(pattern, content)

        for match in matches:
            go_id, go_term, description = match
            go_terms.append((go_id, go_term, description))

    return go_terms


# 提前加载模型以节省每次调用的时间
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# 加载CSV数据
csv_path = 'C:\\Users\\29901\\PycharmProjects\\GeneLLM\\2015111评估\\水稻（zy）\\go.osa.converted.csv'
df_csv = pd.read_csv(csv_path)

# 提取预测结果文件路径
prediction_file_path = 'C:\\Users\\29901\\PycharmProjects\\GeneLLM\\2015111评估\\水稻（zy）\\LOC_Os06g31050.txt'

# 从文件中提取预测结果中的GO信息
predicted_go_terms = extract_go_terms_from_file(prediction_file_path)

# 假设我们正在处理LOC_Os06g31050基因
gene_id = 'LOC_Os06g31050'

# 从CSV中过滤出对应的基因ID的数据
df_filtered = df_csv[df_csv['GeneID'] == gene_id]

# 准备数据结构来存储TP, FP, FN
tp, fp, fn = 0, 0, 0
y_true, y_scores = [], []

# 设置阈值
threshold = 0.5  # 以百分比表示的阈值

# 提取出所有的预测描述，用于批量编码
all_predictions = [desc for _, _, desc in predicted_go_terms]
pred_embeddings = model.encode(all_predictions, convert_to_tensor=True, batch_size=32)

# 创建一个映射，将每个GO ID映射到其描述及其索引
go_id_to_desc_and_index = {row['GO']: (row['Description'], idx) for idx, row in df_filtered.iterrows()}

# 计算描述之间的语义相似度
for i, (go_id, go_term, desc) in enumerate(predicted_go_terms):
    if go_id in go_id_to_desc_and_index:
        csv_desc, csv_idx = go_id_to_desc_and_index[go_id]
        similarity = util.pytorch_cos_sim(pred_embeddings[i], model.encode(csv_desc, convert_to_tensor=True))

        print(f"Comparing GO: {go_id}, Similarity: {similarity.item()}")  # 打印相似度

        if similarity.item() >= threshold:
            tp += 1  # 描述一致，为TP
            y_true.append(1)
            y_scores.append(similarity.item())
        else:
            fp += 1  # GO ID一致但描述不一致，为FP
            y_true.append(0)
            y_scores.append(similarity.item())
    else:
        fn += 1  # 既没有相同的GO ID也没有描述，为FN

# 输出TP, FP, FN
print(f"True Positives (TP): {tp}")
print(f"False Positives (FP): {fp}")
print(f"False Negatives (FN): {fn}")

# 计算Precision和Recall
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0

# 输出Precision和Recall
print(f"Precision: {precision}")
print(f"Recall: {recall}")

# 对于AUC，我们需要一系列的预测概率和真实标签
if len(y_true) > 0 and sum(y_true) != len(y_true) and sum(y_true) != 0:
    auc = roc_auc_score(y_true, y_scores)
    print(f"AUC: {auc}")
else:
    print("AUC cannot be calculated due to all samples being of the same class.")