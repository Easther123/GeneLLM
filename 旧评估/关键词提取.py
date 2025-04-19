import re


def extract_genes_from_text(text):
    # Initialize a dictionary to hold the extracted gene information
    gene_info = {
        'homologous_genes': [],
        'coexpressed_genes': [],
        'similar_genes': []
    }

    # Define regex patterns for extracting gene names in different sections
    patterns = {
        'homologous_genes': r'Arabidopsis homolog\s*$(\w+)$\s*:\s*(.*?)(?=\.|$)',
        'coexpressed_genes': r'co-expressed with genes such as\s*(.*?)(?=, which are involved|\.)',
        'similar_genes': r'High similarity with\s*(\bGhir_\w+\b)\s*$([\d.]+)%$'
    }

    # Helper function to apply regex and collect gene names
    def collect_genes(pattern, category, text):
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        if matches:
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join(match).strip()
                else:
                    match = match.strip()
                genes = re.findall(r'\b(Ghir_\w+|AT\dG\d{5})\b', match)
                if genes:
                    gene_info[category].extend(genes)
                else:
                    print(f"Debug: No genes found in match for category '{category}': {match}")
        else:
            print(f"Debug: No matches found for category '{category}'")

    # Extract gene names from each section
    for category, pattern in patterns.items():
        collect_genes(pattern, category, text)

    return gene_info


def process_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()

        print(f"Processing file: {filename}")
        gene_data = extract_genes_from_text(content)

        # Print the extracted gene information
        for category, genes in gene_data.items():
            print(f"{category}:")
            if genes:
                for gene in genes:
                    print(f"  - {gene}")
            else:
                print("  - None")
    except FileNotFoundError:
        print(f"Error: The file {filename} does not exist.")
    except Exception as e:
        print(f"An error occurred while processing {filename}: {e}")


# Example usage with multiple files
file_list = ['1.txt', '2.txt']
for file in file_list:
    process_file(file)