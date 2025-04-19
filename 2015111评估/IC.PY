import os
import re
import pandas as pd
from collections import Counter
import math

# 定义解析GO术语的函数
def parse_go_terms(file_path):
    """解析文本文件中的GO术语"""
    section_pattern = re.compile(r'#### \*\*(Biological Processes|Molecular Functions|Cellular Components)\*\*:\n')
    entry_pattern = re.compile(r'\d+\. \*\*(GO:\d+)\*\* - ([^\n]+)\.\n\s+- Evidence: (.*)')

    go_terms = []

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        sections = list(section_pattern.finditer(content))

        for i, section in enumerate(sections):
            start_pos = section.end()
            end_pos = len(content) if i == len(sections) - 1 else sections[i + 1].start()

            section_content = content[start_pos:end_pos]
            entries = entry_pattern.findall(section_content)

            for entry in entries:
                go_terms.append(entry[0])

    return go_terms

# 定义读取CSV文件并获取基线GO术语的函数
def load_baseline_csv(csv_file_path):
    df = pd.read_csv(csv_file_path)
    baseline_go_ids = df['GO'].dropna().unique().tolist()
    print(f"Loaded {len(baseline_go_ids)} unique GO IDs from baseline CSV.")
    return baseline_go_ids

# 定义计算IC值的函数
def calculate_ic_values(go_term_counts, total_count):
    ic_values = {}
    for go_id, count in go_term_counts.items():
        frequency = count / total_count
        ic_value = -math.log2(frequency) if frequency > 0 else 0
        ic_values[go_id] = ic_value
    return ic_values

# 定义主函数，用于处理所有文件并生成IC值CSV
def generate_ic_csv(txt_files_dir, csv_file_path, output_csv_path):
    all_go_terms = []

    # 遍历所有txt文件，解析GO术语
    for filename in os.listdir(txt_files_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(txt_files_dir, filename)
            go_terms = parse_go_terms(file_path)
            all_go_terms.extend(go_terms)

    # 获取基线GO术语
    baseline_go_ids = load_baseline_csv(csv_file_path)

    # 统计每个GO术语的出现次数
    go_term_counts = Counter(all_go_terms)

    # 确保所有基线GO术语都被包含在内
    for go_id in baseline_go_ids:
        if go_id not in go_term_counts:
            go_term_counts[go_id] = 0

    # 计算IC值
    total_count = sum(go_term_counts.values())
    ic_values = calculate_ic_values(go_term_counts, total_count)

    # 创建DataFrame并保存为CSV
    ic_df = pd.DataFrame(list(ic_values.items()), columns=['GO_ID', 'IC'])
    ic_df.to_csv(output_csv_path, index=False)
    print(f"IC values saved to {output_csv_path}")

if __name__ == "__main__":
    # 设置文件路径为绝对路径
    txt_files_dir = r'C:/Users/29901/PycharmProjects/GeneLLM/2015111评估/棉花（分给zy的）/'
    csv_file_path = r'C:/Users/29901/PycharmProjects/GeneLLM/2015111评估/棉花（分给zy的）/GO.csv'
    output_csv_path = r'C:/Users/29901/PycharmProjects/GeneLLM/2015111评估/棉花（分给zy的）/ic_values.csv'

    # 调用函数生成IC值CSV
    generate_ic_csv(txt_files_dir, csv_file_path, output_csv_path)