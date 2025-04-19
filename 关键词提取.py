import spacy

# Load the spaCy English model
nlp = spacy.load("en_core_web_sm")


def extract_keywords(section_text, section_name):
    # Process the text with spaCy
    doc = nlp(section_text)

    # Extract key terms using POS tagging and named entity recognition
    keywords = []

    for token in doc:
        # Check for noun or adjective tokens that are not stop words
        if token.pos_ in ['NOUN', 'ADJ'] and not token.is_stop:
            keywords.append(token.text)

    # Remove duplicates while preserving order
    keywords = list(dict.fromkeys(keywords))

    # Filter out non-informative short words (optional)
    keywords = [word for word in keywords if len(word) > 3]

    # Add section name to each keyword
    keywords_with_section = [(word, section_name) for word in keywords]

    return keywords_with_section


def main():
    # Read file content
    with open('1.txt', 'r', encoding='utf-8') as file:
        content = file.read()

    # Split content into sections based on headers
    sections = {
        'Predicted Function and Traits': '### **Predicted Function and Traits**:',
        'Supporting Evidence': '### **支持证据**：',
        'Conclusion': '### **结论**：'
    }

    extracted_keywords = []

    start_index = 0
    for section_name, header in sections.items():
        end_index = content.find(header, start_index)
        if end_index == -1:
            end_index = len(content)
        else:
            end_index = content.find('\n', end_index)

        section_content = content[start_index:end_index].strip()
        if section_content:
            extracted_keywords.extend(extract_keywords(section_content, section_name))

        start_index = end_index + 1

    # Print extracted keywords with their source sections
    for keyword, section in extracted_keywords:
        print(f"Keyword: {keyword}, Source Section: {section}")


if __name__ == "__main__":
    main()