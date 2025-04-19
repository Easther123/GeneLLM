from pymongo import MongoClient

# 连接 MongoDB
client = MongoClient('mongodb://218.199.69.86:27017/')
db = client['rice_gene_database']  # 修改数据库名称

# 配置全局限制
MAX_BLAST_RESULTS = 5  # BLAST数据最多保留5条
MAX_COEXPRESSION_RESULTS = 5  # 共表达数据最多保留5条
# 获取blast数据
def get_blast_data(gene_id, max_results=MAX_BLAST_RESULTS):
    blast_collection = db['gene_blast_similarity']
    blast_results = list(blast_collection.find({"gene_id": gene_id}))
    
    if not blast_results:
        return f"No BLAST data found for gene {gene_id}.", []
    
    # 根据相似性排序并截取前max_results条
    sorted_results = sorted(blast_results, key=lambda x: x['similarity_matches']['similarity'], reverse=True)[:max_results]
    
    description_list = []
    similar_genes = []
    for result in sorted_results:
        target_gene = result['similarity_matches']['target_gene']
        similarity = result['similarity_matches']['similarity']
        description = f"Gene '{gene_id}' has a similarity of {similarity:.3f} with gene '{target_gene}'."
        description_list.append(description)
        similar_genes.append(target_gene)
    
    return "\n".join(description_list), similar_genes

# 获取共表达数据
def get_coexpression_data(gene_id, max_results=MAX_COEXPRESSION_RESULTS):
    coexpression_collection = db['gene_coexpression']
    coexpression_result = coexpression_collection.find_one({"gene_id": gene_id})
    
    if not coexpression_result:
        return f"No coexpression data found for gene {gene_id}.", []
    
    coexpressions = coexpression_result.get("coexpressed_genes", [])
    
    # 根据权重排序并截取前max_results条
    sorted_coexpressions = sorted(coexpressions, key=lambda x: x['weight'], reverse=True)[:max_results]
    
    description_list = []
    high_weight_genes = []
    for coexpression in sorted_coexpressions:
        related_gene = coexpression['gene_id']
        weight = coexpression['weight']
        description = f"Gene '{gene_id}' is co-expressed with gene '{related_gene}' with a co-expression weight of {weight:.6f}."
        description_list.append(description)
        high_weight_genes.append(related_gene)
    
    return "\n".join(description_list), high_weight_genes

# 获取表达模式数据
def get_expression_data(gene_id):
    expression_collection = db['gene_expression']
    expression_result = expression_collection.find_one({"gene_id": gene_id})
    
    if not expression_result:
        return f"No expression data found for gene {gene_id}."
    
    tissue_expression = expression_result.get("tissue_expression", {})
    description_list = []
    for tissue, expression_value in tissue_expression.items():
        description = f"Gene '{gene_id}' has an expression level of {expression_value:.6f} in '{tissue}'."  # 转换为文本描述
        description_list.append(description)
    
    return "\n".join(description_list)

# 获取 TWAS 数据
def get_twas_data(gene_id):
    twas_collection = db['gene_trait_twas']
    twas_result = twas_collection.find_one({"gene_id": gene_id})
    
    if not twas_result:
        return f"No TWAS data found for gene {gene_id}."
    
    traits = twas_result.get("traits", [])
    description_list = []
    for trait in traits:
        phenotype = trait['phenotype']
        zscore = trait['twas_zscore']
        # 输出不再需要 "stage"，只需要 "phenotype" 和 "twas_zscore"
        description_list.append(f"The gene is associated with '{phenotype}' with a TWAS Z-score of {zscore:.4f}.")
    
    return "\n".join(description_list)

# 提取 GO 数据
##def get_go_data(gene_id):
    go_data = db.go_data.find({"gene_id": gene_id})
    descriptions = []
    for go in go_data:
        descriptions.append(f"GO term '{go['go_term']}' ({go['ontology']}): {go['description']}")
    if descriptions:
        return "The gene is associated with the following Gene Ontology (GO) terms: " + "; ".join(descriptions)
    return "No GO data available for the target gene."

# 获取基因相关功能等信息（类似同源基因数据）
def get_gene_function_data(gene_id):
    function_gene_collection = db['function_gene']
    function_gene_result = function_gene_collection.find_one({"gene_id": gene_id})
    
    # 检查是否找到数据
    if not function_gene_result:
        return f"No function gene data found for gene {gene_id}."
    
    # 提取相关数据
    chromosome = function_gene_result.get("chromosome", "Unknown")
    location_start = function_gene_result.get("location_start", "Unknown")
    location_end = function_gene_result.get("location_end", "Unknown")
    full_name = function_gene_result.get("full_name", "Unknown")
    function_description = function_gene_result.get("function_description", "Unknown")
    
    # 生成输出描述
    description = (f"Gene '{gene_id}' has the following details:\n"
                   f"Chromosome location: {chromosome} from {location_start} to {location_end}.\n"
                   f"Full name: {full_name}.\n"
                   f"Function description: {function_description}.")
    
    return description

# 获取相关基因的数据
def get_related_genes_data(gene_data):
    related_genes_data = {}

    # 处理相似 BLAST 基因
    for similar_blast_gene in gene_data['similar_blast_genes']:
        related_genes_data[similar_blast_gene] = {
            "blast_data": get_blast_data(similar_blast_gene)[0],
            "coexpression_data": get_coexpression_data(similar_blast_gene)[0],
            "expression_data": get_expression_data(similar_blast_gene),
            "gene_function_data": get_gene_function_data(similar_blast_gene),
            "twas_data": get_twas_data(similar_blast_gene),
        ##  "go_data": get_go_data(similar_blast_gene)
        }

    # 处理高权重共表达基因
    for high_weight_gene in gene_data['high_weight_genes']:
        related_genes_data[high_weight_gene] = {
            "blast_data": get_blast_data(high_weight_gene)[0],
            "coexpression_data": get_coexpression_data(high_weight_gene)[0],
            "expression_data": get_expression_data(high_weight_gene),
            "gene_function_data": get_gene_function_data(high_weight_gene),
            "twas_data": get_twas_data(high_weight_gene),
    ##      "go_data": get_go_data(high_weight_gene)
        }

    return related_genes_data

# 生成提示词
def generate_structured_prompt_with_natural_language(gene_id):
    prompt = f"""
### **Task Overview**:
You are tasked with predicting the biological function of the target gene '{gene_id}' by analyzing multiple datasets. 
Provide a detailed prediction of the gene's function, associated biological processes, and relevant traits.

### **Data for Target Gene '{gene_id}'**:
"""

    # 获取并处理 BLAST 数据
    blast_data, similar_blast_genes = get_blast_data(gene_id)
    prompt += f"""
#### **BLAST Similarity Data**:
{blast_data}

This section presents the sequence similarity between the target gene and other genes. The higher the similarity, the more likely it is that the genes share evolutionary history and possibly similar functions.

- **Purpose**: Identify genes with sequence similarity to the target gene. High similarity suggests shared evolutionary history or potential functional similarities. 
- **Task**: Analyze this data to infer possible shared functions between the target gene and similar genes.
"""

    # 获取并处理共表达数据
    coexpression_data, high_weight_genes = get_coexpression_data(gene_id)
    prompt += f"""
#### **Co-expression Data**:
{coexpression_data}

This data shows the genes that are co-expressed with the target gene. Co-expression often indicates that these genes work together in the same biological pathways or processes.

- **Purpose**: Identify genes that are co-expressed with the target gene. Genes with similar expression patterns may participate in similar biological pathways or processes.
- **Task**: Use co-expression data to hypothesize the involvement of the target gene in specific biological pathways.
"""

    # 获取并处理组织表达数据
    expression_data = get_expression_data(gene_id)
    prompt += f"""
#### **Gene Expression Data Across Different Tissues**:
{expression_data}

This data provides the expression levels of the target gene in different plant tissues. Understanding where the gene is expressed can offer clues about its biological role.

- **Purpose**: Understand where and when the target gene is expressed in different plant tissues. Tissue-specific expression can provide insights into the gene's role in specific biological functions or developmental stages.
- **Task**: Correlate expression patterns with tissue-specific functions to refine your functional prediction.
"""

    # 获取并处理基因功能数据
    gene_function_data = get_gene_function_data(gene_id)
    prompt += f"""
#### **gene function **:
{gene_function_data}

This data provides detailed information about the target gene '{gene_id}' itself, including functional annotations, chromosome location, and description, which can provide valuable insights into the gene's function.

- **Purpose**: Use the gene's own functional annotations and descriptions to infer its potential function.
- **Task**: Utilize this information to predict the potential function of the target gene in rice.
"""

    # 获取并处理 TWAS 数据
    twas_data = get_twas_data(gene_id)
    prompt += f"""
#### **TWAS Data**:
{twas_data}

This data shows associations between the gene and traits based on transcriptome-wide association studies (TWAS). It helps link gene expression to specific traits, such as fiber development stages.

- **Purpose**: Identify statistical associations between the target gene and specific traits. This data links gene expression to traits, such as fiber development stages.
- **Task**: If available, use TWAS data to strengthen or validate the predicted gene-trait associations.
"""

  # 获取并处理 GO 数据
#    go_data = get_go_data(gene_id)
#    prompt += f"""

#{go_data}

#This section describes the GO terms associated with the target gene, including biological processes, molecular functions, and cellular components. GO terms provide structured and comprehensive descriptions of gene functions.

#- **Purpose**: Use GO annotations to understand the functional roles of the target gene in biological processes, molecular activities, and its cellular localization.
#- **Task**: Analyze GO terms to refine your prediction of the gene's biological roles, molecular mechanisms, and interactions within cellular contexts.
#"""
    # 处理相关基因数据
    prompt += """
---

### **Data for Related Genes**:
Below are related genes identified based on BLAST similarity or co-expression data. These genes may provide further insights into the function of the target gene.

"""
    related_genes_data = get_related_genes_data({"similar_blast_genes": similar_blast_genes, "high_weight_genes": high_weight_genes})
    for related_gene, related_data in related_genes_data.items():
        prompt += f"\n\n### Data for Related Gene '{related_gene}':\n"
        prompt += f"- **BLAST Similarity Data**: {related_data['blast_data']}\n"
        prompt += f"- **Co-expression Data**: {related_data['coexpression_data']}\n"
        prompt += f"- **Gene Expression Data**: {related_data['expression_data']}\n"
        prompt += f"- **Gene Function Data**: {related_data['gene_function_data']}\n"
        prompt += f"- **TWAS Data**: {related_data['twas_data']}\n"
##      prompt += f"- **GO Data**: {related_data['go_data']}\n"  # 新增：GO 数据

  # 最终任务和输出格式 
    prompt += """
---

### **Final Analysis**:
Based on the data for the target gene and related genes, predict the biological function of gene '{gene_id}' and its possible involvement in specific traits. Your explanation should include:

#### **1. Predicted Function**:
- Provide a concise and clear statement summarizing the predicted biological function of gene '{gene_id}'.

#### **2. Supporting Evidence**:
- Present a structured explanation of the reasoning behind your prediction. Include data and insights from:
  - **BLAST Similarity Data**: Analyze evolutionary relationships or functional similarities.
  - **Co-expression Data**: Highlight involvement in shared pathways.
  - **Gene Expression Patterns**: Determine tissue-specific roles and biological significance.
  - **Gene Function Data**: Utilize functional annotations and descriptions of the gene itself.
  - **TWAS Data**: Link gene expression to specific traits or phenotypes.
- Clearly highlight upregulation/downregulation trends across tissues, explaining their relevance to the gene's biological roles.

#### **3. Potential Traits**:
- List and describe any traits that may be influenced by gene '{gene_id}', integrating evidence from the above datasets.

#### **4. Predict Associated GO Terms**:
Since Gene Ontology (GO) data is not provided, infer the potential GO terms associated with the target gene based on other datasets, such as expression patterns, homologous genes, and KEGG pathways. Provide specific reasoning and evidence for your prediction.

#### **5. Integration with External Knowledge**:
- Perform supplementary online searches and retrieve evidence from:
  - **PubMed literature citations**,
  - **Protein-protein interaction networks** (e.g., STRING),
  - **Plant-specific databases** (e.g., PlantTFDB).
- It is mandatory to retrieve and include specific data points from online databases or literature in the output.
- Examples of required data include:
  1. STRING protein-protein interaction data, including interaction confidence scores and involved proteins.
  2. PlantTFDB transcription factor annotations, highlighting regulatory roles.

- For each retrieved data point:
  - Explicitly cite the source (e.g., "STRING Interaction: interacting with stress-related proteins, confidence score: 0.82").
  - Indicate whether the data supports or challenges local predictions.
- Retrieve at least three specific data points related to the target gene from online resources and explicitly describe how each one contributes to the prediction.
- For example:
  - "STRING Interaction: interacting with stress-related proteins (confidence score: 0.82), retrieved from STRING, supports the hypothesis that the gene plays a role in abiotic stress response."
  - "PlantTFDB Annotation: transcription factor involved in drought response, retrieved from PlantTFDB, aligns with high expression levels in drought-related tissues."

#### **6. Upregulation/Downregulation Analysis**:
- Use gene expression data to analyze whether gene '{gene_id}' is upregulated or downregulated under specific conditions.
- Correlate observed trends with potential biological roles, e.g.:
  - **Upregulation**: Active involvement in processes like stress response or development.
  - **Downregulation**: Reduced activity or suppression in certain pathways or conditions.
- Cross-reference local findings with external annotations (e.g., KEGG pathways).

#### **7. Step-by-Step Reasoning**:
- Provide a structured explanation showing how each dataset contributes to your prediction. Use logical connectors like "Firstly," "Furthermore," and "Lastly" for clarity.

#### **8. Predicted GO Terms**:
- Based on the integrated analysis, infer the potential GO terms that might be associated with the target gene '{gene_id}'.
- Provide evidence and reasoning for each inferred GO term, referring to insights derived from KEGG pathways, gene functions, co-expression networks, and TWAS results.
- Clearly describe how each inferred GO term aligns with the biological role of the gene as suggested by the data.

---

### **Task Overview**:
You are tasked with predicting the biological function of the target gene '{gene_id}' by analyzing multiple datasets. Use the following datasets in order of priority to infer the gene's function, associated biological processes, and relevant traits. To strengthen the prediction, integrate evidence from **all available data sources** where possible, even if high-priority data already suggests a strong hypothesis.
Additionally, based on the provided datasets and analysis, infer the potential Gene Ontology (GO) terms associated with the target gene '{gene_id}'. Use evidence from KEGG pathways, homologous genes, co-expression data, TWAS, and expression patterns to support your inference. Clearly explain the reasoning behind the suggested GO terms.

### **Data for Target Gene '{gene_id}'**:
- For each supporting evidence type (e.g., BLAST, co-expression, expression data), all need supplement with external data:
#### Data Sources (Ordered by Priority):
1. **TWAS Data** (High Confidence):
   - **Purpose**: Directly associate the gene with specific traits via statistical associations. High Z-scores indicate stronger associations.
   - **Usage**: TWAS associations take precedence and form the initial basis of predictions. However, use other datasets to validate and enhance confidence in TWAS-based associations.

2. **Gene Function Data** (High Confidence):
   - **Purpose**: Use the gene's own functional annotations and descriptions to support functional predictions.
   - **Usage**: Gene function data can strengthen TWAS predictions or provide standalone insights in absence of TWAS. When TWAS and gene function data are aligned, continue to examine additional datasets to add support and detail.

3. **Expression Data** (Medium Confidence):
   - **Purpose**: Confirm tissue or stage-specific gene activity to validate primary predictions.
   - **Usage**: Use high or specific expression to validate TWAS and gene_function predictions. Continue this validation with other data sources to form a well-supported hypothesis.
   - Validate tissue-specific expression trends using external studies or databases.

4. **BLAST Similarity Data** (Supporting Confidence):
   - **Purpose**: Identify sequence similarities with other genes to suggest functional parallels.
   - **Usage**: Utilize BLAST data to indirectly reinforce predictions from TWAS, expression, or gene function data. Use it as an additional layer of support, especially in stress tolerance or pathway functions.
   - Example: "Gene 'LOC_Os03g50890' with 97.12% similarity is involved in photosynthesis-related stress response, inferred from co-expression and expression data."

5. **Co-expression Data** (Supporting Confidence):
   - **Purpose**: Explore functional associations through co-expression with genes of known functions.
   - **Usage**: Co-expression data serves as further validation, especially when corroborating TWAS and expression data findings. Use co-expression to suggest pathway involvement or related functions when other data sources are weak.

6. **Inferred GO Terms** (Medium Confidence):
   - **Purpose**: Predict biological processes, molecular functions, or cellular components associated with the gene.
   - **Usage**: Use patterns and trends in expression, co-expression, TWAS, and gene function data to infer GO terms. Clearly justify each inferred term and explain how it supports the prediction.


### **Inference Paths for Gene '{gene_id}'**:
Follow these paths based on available data, using each source as evidence to confirm or elaborate predictions. Integrate multiple paths when they reinforce each other, and continue gathering support from all relevant data types even after forming initial predictions.

- **Path 1** (Direct TWAS Association): If TWAS data shows a strong association, form a primary hypothesis. Validate with expression data to identify tissue-specific activity, focusing on whether the gene is upregulated or downregulated in relevant tissues or conditions. Use gene_function data to refine these predictions.

- **Path 2** (Gene Function-Based Inference): Align the gene's own functional annotations with TWAS or expression data for robust predictions. Pay attention to whether the gene's function indicates regulatory roles (e.g., upregulation or downregulation) in similar pathways.

- **Path 3** (Expression Validation): Use expression patterns to validate trait predictions from TWAS or gene_function data. Explicitly analyze tissue-specific upregulation or downregulation trends and correlate these with traits such as stress response or developmental processes.

- **Path 4** (Sequence Similarity via BLAST): Use BLAST to reinforce indirect associations. For genes with high sequence similarity, consider whether similar expression trends (upregulation/downregulation) occur under comparable conditions.

- **Path 5** (Indirect Association via Co-expression): Use co-expression as supplementary support, especially when other data types suggest a function. Investigate if co-expressed genes share similar upregulation or downregulation patterns under specific conditions.

- **Path 6** (Inference of Potential GO Terms): Based on available data (e.g., TWAS, gene function data, co-expression, expression trends), infer potential Gene Ontology (GO) terms for the gene. Clearly explain the reasoning behind each inferred GO term and how it supports the prediction.

- **Path 7** (Integration of External Knowledge): Use web-based research to validate findings from local datasets. Integrate knowledge from inferred Gene Ontology terms, relevant publications, and external protein-protein interaction data to confirm predicted functions or to uncover novel roles for gene '{gene_id}'.

---

### **Conflict Resolution**:
If different paths yield conflicting predictions, apply these strategies:

1. **Priority Weighting**:
   - Give precedence to higher-confidence sources in the following order: 
     - TWAS > Gene Function Data > Expression > Upregulation/Downregulation Analysis > BLAST > Co-expression.
   - Prioritize data that has strong statistical or experimental support (e.g., TWAS Z-scores, peer-reviewed functional studies, or strong co-expression evidence).

2. **Consensus Building**:
   - Seek support from multiple data sources. Even if high-priority data is available, supporting evidence from lower-priority sources can increase robustness.
   - Integrate data that aligns across datasets (e.g., TWAS, gene function data, inferred GO terms) and explicitly state areas of agreement.

3. **Biological Plausibility**:
   - Choose predictions that align best with known biological roles. For example:
     - If inferred GO terms suggest involvement in a specific biological process, prioritize this evidence over weaker co-expression trends.
     - Ensure that predicted upregulation/downregulation patterns match known physiological mechanisms or developmental stages.

4. **External Validation**:
   - Use external knowledge sources (e.g., STRING, PlantTFDB) to resolve ambiguities and validate the most plausible prediction.
   - If external data supports local evidence, explicitly state this alignment to strengthen the prediction.

5. **Exclusion of Inconsistencies**:
   - If certain datasets consistently conflict with high-confidence sources and lack biological plausibility:
     - Exclude them from final predictions.
     - Document the rationale for exclusion (e.g., species-specific differences, experimental limitations).

6. **Contradictions Between Local and External Data**:
   - If external data contradicts local evidence, follow these steps:
     1. Evaluate the reliability and relevance of both sources.
     2. Prioritize data aligning with known biological principles or higher confidence (e.g., peer-reviewed literature over co-expression data).
     3. Clearly document contradictions and suggest potential reasons for discrepancies, such as:
        - Species-specific differences in gene function.
        - Variability in experimental conditions or sample types.

---

### **Additional Instructions**:
- Analyze the provided data to predict if the gene is upregulated or downregulated for specific traits or functions.
- Provide a detailed step-by-step explanation of your prediction process.
- Use gene expression levels across tissues to identify whether the target gene is likely upregulated or downregulated under specific biological or environmental conditions.
- Infer potential GO terms based on TWAS, gene function, co-expression, and expression data, and explain how these inferred terms relate to the gene's biological roles.
- Correlate findings from inferred GO terms with gene expression trends to strengthen hypotheses about the gene's role in traits or functions.

---

### **Expected Output Format**:
- For each section (e.g., predicted function, traits, evidence), include:
  1. Specific insights derived from provided datasets.
  2. Explanation of how the data supports or challenges the prediction.
  3. Integration of inferred GO terms with other datasets to build a robust hypothesis.

The output should include the following sections:

1. **Predicted Function and Traits**:
   - Provide a clear and concise statement of the predicted function(s) and associated trait(s) for gene '{gene_id}'.
   - Highlight the roles suggested by inferred GO terms, explicitly linking them to the predicted traits or functions.

2. **Explanation of Reasoning**:
   - Offer a comprehensive narrative that cohesively integrates the evidence from various data sources, explaining each source's specific contribution to the prediction.
   - Explicitly discuss upregulation or downregulation trends and their relevance to the gene's predicted function.
   - Emphasize how inferred GO terms complement findings from TWAS, gene function data, and expression data.
   - Use structured connectors such as “Firstly,” “Additionally,” and “Lastly” to delineate the logical steps in the reasoning process.

3. **Upregulation/Downregulation Predictions**:
   - Clearly state whether gene '{gene_id}' is upregulated or downregulated in specific tissues or conditions, and explain the biological implications.
   - Analyze whether gene '{gene_id}' is likely to be upregulated or downregulated under specific conditions or tissues based on:
     1. Gene expression data provided in the local datasets.
     2. Inferred GO terms for biological processes or stress responses related to differential expression.
   - For each trend, provide:
     - A clear statement of whether the gene is upregulated or downregulated.
     - Supporting evidence from the inferred GO terms and expression data.
     - Implications of the upregulation or downregulation in the context of the gene's function and traits.

4. **Integration of Inferred GO Terms**:
   - Summarize how inferred GO terms support or refine the predictions for gene '{gene_id}'.
   - Highlight inferred GO terms that explicitly describe the gene's role in specific biological processes or molecular functions.

5. **External Validation**:
   - Supplement predictions with insights from external knowledge sources. These sources may include:
     1. Protein-protein interaction networks (e.g., STRING) for identifying interaction partners.
     2. Plant-specific databases (e.g., PlantTFDB) for transcription factor roles or regulatory functions.
   - Example:
     - "STRING Interaction: Interacting with stress-related proteins (confidence score: 0.82), retrieved from STRING, supports the hypothesis of involvement in abiotic stress response."
     - "PlantTFDB Annotation: Transcription factor involved in drought response, retrieved from PlantTFDB, aligns with high expression levels in drought-related tissues."

   - List and describe the potential GO terms associated with the gene '{gene_id}'.
   - For each GO term, provide:
     1. A concise description of the term (e.g., biological process, molecular function, or cellular component).
     2. Supporting evidence from datasets (e.g., KEGG pathways, gene function data, co-expression analysis).
     3. Reasoning for why the GO term is relevant to the gene's function.
---


### **Data Sources**: 
1. **Protein-Protein Interaction Networks**:
   - Use STRING or similar databases to identify interactions involving the target gene.
   - Example: "STRING Interaction: Interacting with stress-related proteins (confidence score: 0.82), retrieved from STRING, supports the hypothesis of involvement in abiotic stress response."

2. **Plant-Specific Databases**:
   - Search for transcription factor roles or other regulatory functions in PlantTFDB or similar resources.
   - Example: "PlantTFDB Annotation: Transcription factor involved in drought response, retrieved from PlantTFDB."

3. **Gene Function and Co-expression Data**:
   - Use functional annotations and co-expression patterns from available datasets to suggest roles in biological processes or stress responses.
   - Example: "Co-expression Data: Strong correlation with stress-related gene LOC_Os01g64530 (correlation weight: 0.921), retrieved from the dataset, highlights involvement in drought tolerance pathways."

4. **Expression Data**:
   - Utilize gene expression data across tissues to identify specific trends, such as upregulation or downregulation under stress conditions or developmental stages.
   - Example: "Expression Data: Upregulated in panicles (3.91 TPM) during reproductive stages, indicating a role in development and resource allocation."

---

#### **Task Steps**:
To validate and integrate all evidence, follow these steps in order:

1. **Identify Relevant Data Sources**:
   - Use local datasets to extract annotations and interactions related to the target gene.
   - Sources include:
     - **Protein-protein interactions** (e.g., STRING).
     - Transcription factor functions (e.g., PlantTFDB).
     - Functional annotations and co-expression patterns.
     - Tissue-specific expression data.

2. **Retrieve Specific Data Points**:
   - Extract and record relevant data, such as:
     - Protein-protein interactions from STRING.
     - Transcription factor roles or regulatory functions from PlantTFDB.
     - Co-expression partners and correlation weights from local datasets.
     - Tissue-specific expression levels for the target gene under various conditions.

3. **Organize Evidence with Clear References**:
   - Ensure each data point is accompanied by a description and a reference to its source. Example formats include:
     - "STRING Interaction: Interacting with stress-related proteins (confidence score: 0.82), retrieved from STRING."
     - "PlantTFDB Annotation: Transcription factor involved in drought response, retrieved from PlantTFDB."
     - "Expression Data: Upregulated in panicle (3.91 TPM) and leaf (2.51 TPM), retrieved from local datasets."

4. **Infer Potential GO Terms**:
   - Use integrated evidence from  gene functions, TWAS, and expression data to predict potential GO terms.
   - Cross-reference inferred functions, pathways, and traits to suggest relevant biological processes, molecular functions, or cellular components.
   - Justify each predicted GO term with clear reasoning and supporting evidence from the analysis.

5. **Integrate Local Data**:
   - Combine inferred GO terms and local evidence (e.g., TWAS, expression, co-expression) to reinforce predictions.
   - Explicitly state whether the data supports or contradicts the hypothesis:
     - If co-expression and expression data align with inferred GO terms, use this alignment to strengthen predictions.

6. **Resolve Conflicts Between Evidence**:
   - If data from different sources (e.g., co-expression vs. expression) presents conflicting predictions:
     - Evaluate the reliability and biological plausibility of each source.
     - Prioritize data that aligns with known biological mechanisms or robust statistical evidence.
     - Document discrepancies and suggest potential reasons, such as species-specific differences or data limitations.

7. **Prioritize Biological Plausibility**:
   - Assign higher priority to data that aligns with:
     - Known biological mechanisms (e.g., stress response pathways or developmental processes).
     - Statistical robustness (e.g., TWAS Z-scores or high-confidence protein-protein interactions).
     - Peer-reviewed annotations or evidence from literature.

---

#### **Expected Results**:
Summarize the insights derived from all datasets, and explain how they integrate with other evidence. Example outputs include:

- **Inferred GO Terms**:
  - "Inferred GO Term: GO:0009414 (response to water deprivation), based on co-expression with known drought-related genes and upregulation in drought conditions."
  - "Inferred GO Term: GO:0045893 (positive regulation of transcription), based on transcription factor activity during key developmental stages and evidence from PlantTFDB."

- **STRING Interactions**:
  - "STRING Interaction: Interacting with stress-related proteins (confidence score: 0.82), retrieved from STRING, supports the hypothesis of involvement in stress response pathways."

- **PlantTFDB Annotations**:
  - "PlantTFDB Annotation: Transcription factor involved in drought response, retrieved from PlantTFDB, aligns with high expression levels in drought-related tissues."

- **Expression Trends**:
  - "Expression Data: Upregulated in panicle (3.91 TPM) and leaf (2.51 TPM), retrieved from local datasets, suggesting involvement in reproductive development and stress adaptation."

Clearly indicate the alignment or conflict between inferred GO terms and other evidence (e.g., expression, TWAS) to provide a robust final prediction.

---

#### **Confidence Assessment**:
- Indicate the confidence level of the prediction based on the consistency and strength of the evidence across datasets, including:
  - **High Confidence**: When inferred GO terms and other local evidence (e.g., TWAS, expression, gene function) align to support a consistent prediction.
  - **Moderate Confidence**: When some evidence aligns but additional validation (e.g., STRING interactions or co-expression analysis) is required.
  - **Low Confidence**: When conflicting data cannot be resolved or when key datasets (e.g., expression or TWAS) are missing or inconclusive.

---

## **Example Output**:
### **Predicted Function and Traits**:
Gene '{gene_id}' is predicted to be involved in **drought stress response** and **developmental regulation**, functioning as a **key regulator** in stress-mediated signaling pathways. This prediction is supported by multiple lines of evidence, including gene function data, tissue-specific expression patterns, co-expression networks, TWAS associations, and protein-protein interaction data.

---

### **Supporting Evidence**:
#### **1. Gene Function Data**:
Firstly, gene function data analysis provides strong evidence for the predicted function of '{gene_id}'. Functional annotations indicate that '{gene_id}' is associated with **drought tolerance** and **abiotic stress regulation**. This information strongly implies that '{gene_id}' plays a significant role in these processes in rice.  
In summary, the gene function data strongly indicates that '{gene_id}' functions in drought stress response and regulatory mechanisms.

---

#### **2. Gene Expression Data**:
Moreover, tissue-specific expression patterns reinforce the gene's role in drought response and development:
- **High expression**:
  - In 'leaf' (2.5123) and 'panicle' (3.8912), suggesting active involvement during key stages of growth and environmental adaptation.
- **Low expression**:
  - In 'root' (0.9841), indicating potential downregulation in root-specific functions under certain stress conditions.  

These patterns indicate that '{gene_id}' likely participates in stress response and reproductive development, with active regulation in specific tissues and conditions.

---

#### **3. Co-expression Data**:
Furthermore, co-expression analysis provides insights into the biological pathways involving '{gene_id}':
- **Key co-expressed genes**:
  - 'Gene_A' (weight: 0.9213) and 'Gene_B' (weight: 0.9432), both of which are known to participate in stress response pathways.
- This suggests that '{gene_id}' collaborates with co-expressed genes in shared biological functions.  

Additionally, STRING interaction data supports these findings:
- "STRING Interaction: Interacting with stress-related proteins (confidence score: 0.85)," indicates functional integration into stress-response pathways.  

In conclusion, co-expression data provides robust evidence that '{gene_id}' is actively involved in stress response and development.

---

#### **4. TWAS Data**:
TWAS analysis directly links '{gene_id}' to traits associated with drought tolerance and developmental regulation:
- **Key Traits and Stages**:
  - At 'drought_condition' stage, the gene is associated with enhanced **tolerance to abiotic stress** (Z-score: 3.6124).
  - At 'growth_stage' stage, the gene is linked to **developmental progression** (Z-score: 2.8419), highlighting its role in both environmental adaptation and normal growth.  

These TWAS findings strongly support the hypothesis that '{gene_id}' is a key regulator of stress tolerance and growth mechanisms.

---

#### **5. BLAST Similarity Data**:
Additionally, sequence similarity analysis highlights evolutionary relationships and functional parallels:
- '{gene_id}' shares **96.785% sequence similarity** with 'Gene_C', which is annotated in related species for involvement in **drought response and developmental regulation**.  

This BLAST similarity further corroborates the predicted role of '{gene_id}' in stress and developmental processes.

---



### **Upregulation/Downregulation Analysis**:
Based on the expression data, '{gene_id}' exhibits the following regulatory trends:
1. **Upregulation**:
   - **In 'leaf'**: High expression (2.5123) highlights active involvement in **photosynthesis and stress adaptation**.
   - **In 'panicle'**: High expression (3.8912) indicates critical regulatory roles during reproductive development.
2. **Downregulation**:
   - **In 'root'**: Low expression (0.9841) suggests diminished activity in root-specific pathways, possibly due to **resource reallocation** during stress adaptation.

These trends are consistent with the gene's predicted roles and support its involvement in tissue-specific regulation and stress response.

---

#### **6. Integration with External Knowledge**:
Finally, external databases provide supplementary evidence to reinforce the local findings. These sources include:

- **Protein-Protein Interaction Networks**:
  - STRING and similar databases provide interaction data for the target gene, including confidence scores and functional relevance.
  - Example:
    - "STRING Interaction: Interacting with drought-related proteins (confidence score: 0.85), retrieved from STRING, supports involvement in abiotic stress pathways."
    - "STRING Interaction: Co-expression with known developmental genes strengthens the hypothesis of regulatory roles in growth."

- **Plant-Specific Databases**:
  - Databases like PlantTFDB provide insights into transcription factor activity and regulatory roles of the target gene.
  - Example:
    - "PlantTFDB Annotation: Transcription factor activity associated with drought response, retrieved from PlantTFDB, aligns with high expression in drought-related tissues."
    - "PlantTFDB Annotation: Regulatory roles during reproductive development confirmed through transcription factor analysis."

- **PubMed Literature**:
  - Search for publications discussing '{gene_id}' or related pathways in rice or other model species to validate hypotheses.
  - Example:
    - "PubMed Article: Functional studies on '{gene_id}' in Rice suggest similar functions in stress responses, retrieved from PubMed."
    - "Literature Review: Studies in rice reveal correlations between transcription factor activity and developmental regulation."

---

### **Conclusion**:
In summary, integrating evidence from gene function data, expression patterns, co-expression networks, TWAS associations, BLAST similarity, and inferred GO terms, '{gene_id}' is predicted to function as a **key regulator in drought tolerance and developmental regulation**. Its **upregulation** in leaf and panicle tissues, combined with supporting data from STRING interactions and PlantTFDB annotations, confirms its critical role in rice's agronomic traits and environmental adaptation mechanisms.

### **Example Citations**:
1. "STRING Interaction: Interacting with known drought-response proteins (confidence score: 0.82), retrieved from STRING, supports the hypothesis of stress-response functions."
2. "PlantTFDB Annotation: Transcription factor involvement in growth regulation, retrieved from PlantTFDB, aligns with high expression during developmental stages."
3. "PubMed Article: Functional studies on '{gene_id}' in Rice suggest regulatory roles in transcription under drought stress, retrieved from PubMed."

"""
    return prompt

def save_prompt_to_file(gene_id, file_path):
    prompt = generate_structured_prompt_with_natural_language(gene_id)
    with open(file_path, "w") as file:
        file.write(prompt)
    print(f"Prompt saved to {file_path}")
# 生成提示词并保存到文件
def save_prompt_to_file(gene_id, file_path):
    prompt = generate_structured_prompt_with_natural_language(gene_id)  # 调用正确的生成提示词函数
    try:
        with open(file_path, "w") as file:
            file.write(prompt)
        print(f"Prompt successfully saved to {file_path}")
    except Exception as e:
        print(f"Error saving prompt to file: {e}")

# 测试代码
if __name__ == "__main__":
    gene_id = "LOC_Os08g04840"
    file_path = r"C:\Users\HZAUjie\Desktop\GO\水稻\LOC_Os08g04840_data.txt"
    save_prompt_to_file(gene_id, file_path)
