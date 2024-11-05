import re
import json

# Эта функция делит на слова
def tokenize_text(text):
    """Tokenize the input text into a list of tokens."""
    return re.findall(r'\w+(?:[-_]\w+)*|\S', text)


def extract_unique_types_from_json(data):
    """
    Извлекает уникальные типы из JSON-данных.

    :param data: JSON-данные в виде словаря.
    :return: Множество уникальных типов.
    """
    unique_types = set()
    for entity in data.get("entities", []):
        types = entity.get("types", [])
        for t in types:
            unique_types.add(t)  # Добавляем типы без изменения регистра
    return unique_types

def split_with_overlap(tokenized_text, max_tokens, overlap):
    """
    Разделяет токенизированный текст на фрагменты длиной max_tokens или меньше, с наложением overlap токенов.

    :param tokenized_text: Список токенов.
    :param max_tokens: Максимальная длина фрагмента.
    :param overlap: Количество токенов для наложения.
    :return: Список фрагментов.
    """
    fragments = []
    start = 0

    while start < len(tokenized_text):
        end = min(start + max_tokens, len(tokenized_text))
        fragment = tokenized_text[start:end]

        # Проверяем, если это последний фрагмент и он полностью дублируется в предыдущем фрагменте
        if len(fragments) > 0 and fragment == fragments[-1][-overlap:]:
            break

        fragments.append(fragment)
        start = end - overlap if end - overlap > start else end

    return fragments

def process_json_answer(text, max_tokens=384, overlap=50):
    text = text.replace('```json', '').replace('```', '')
    js = json.loads(text.strip())
    all_tokens = tokenize_text(js['text'])
    ents = [(k["entity"], k["types"]) for k in js['entities']]
    all_types = extract_unique_types_from_json(js)

    answer = []
    for tokens in split_with_overlap(all_tokens, max_tokens, overlap):    
        # print(tokens)
        spans = []
        for entity in ents:
            entity_tokens = tokenize_text(str(entity[0]))

            # Find the start and end indices of each entity in the tokenized text
            for i in range(len(tokens) - len(entity_tokens) + 1):
                if " ".join(tokens[i:i + len(entity_tokens)]).lower() == " ".join(entity_tokens).lower():
                    for el in entity[1]:
                        spans.append((i, i + len(entity_tokens) - 1, el.replace('_', ' ')))
        answer.append({"tokenized_text": tokens, "ner": spans, "label":list(all_types)})
    return answer