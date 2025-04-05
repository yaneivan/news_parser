from openai import OpenAI
from .base_provider import BaseLLMProvider
import os
from dotenv import load_dotenv

load_dotenv()

class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        base_url = os.environ["BASE_URL"]
        api_key = os.environ["OPENAI_API_KEY"]
        self.model = os.environ["MODEL"]
        self.client = OpenAI(
            base_url=base_url,  
            api_key=api_key,   
        )   

    def summarize(self, input_text) -> str:
        """Returns summary of input text"""
        chat_response = self.client.chat.completions.create(
        model = self.model,
        messages = [
                {
                    "role": "user",
                    "content": f"Summarize the given text. Write summary without any introduction words. Твой ответ должен быть на русском языке.\n Text:{input_text}",
                }])
        return (chat_response.choices[0].message.content) 

    # with examples
    def create_prompt_for_entity_extraction(self, text):
        prompt = """
    **Objective:**
    Analyze the given text and extract named entities. Each entity should be meticulously labeled according to its type for straightforward extraction.

    **Format Requirements:**
    - The output should be formatted in JSON, containing the text and the corresponding entities list.
    - Each entity in the text should be accurately marked and annotated in the 'entities' list.

    **Entity Annotation Details:**
    - Entities spans can be nested within other entities.
    - A single entity may be associated with multiple types. list them in the key "types".
    - Классы должны быть названы на русском языке.
    - Классы должны быть с большой буквы. 

    **Output Schema:**

    ```json
    {
    "text": "{text}",
    "entities": [
        {"entity": "entity name", "types": ["type 1", "type 2", ...]},
        ...
    ]
    }
    ```

    """

        # Adding the dynamically created text to the prompt
        prompt += f"""
    Text: 
    "{text}">
    """

        return prompt

    def annotate(self, input_text) -> str:
        """Returns annotated text"""

        prompt = self.create_prompt_for_entity_extraction(input_text)

        chat_response = self.client.chat.completions.create(
            model= self.model,
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                }])

        return (chat_response.choices[0].message.content)

    def rate(self, input_text) -> str:
        """Оценивает текст для обучения NER. Возвращает JSON-строку с полями 'score' (Excellent/Good/Average/Poor/Unusable) 
        и 'reasoning_behind_score' (обоснование оценки). Критерии:
        
        1. Количество сущностей: 5+ (Excellent), 3-4 (Good), 2-3 (Average), 1-2 (Poor), 0 (Unusable)
        2. Разнообразие классов: минимум 2 категории для Good, 3+ для Excellent
        3. Контекст: ясность и однозначность определения сущностей
        
        Пример вывода: 
        '{"reasoning_behind_score": "5+ сущностей из 3 категорий, ясный контекст", "score": "Excellent"}' 
        """

        chat_response = self.client.chat.completions.create(
        model = self.model,
        messages = [
                {
                    "role": "user",
                    "content": 
                    f"""Проанализируй текст для обучения NER-модели. **Детализированная инструкция**:

1. **Критерии оценки**:
   - Количество сущностей: 
     • 5+ → Excellent
     • 3-4 → Good
     • 2-3 → Average
     • 1-2 → Poor
     • 0 → Unusable
   - Разнообразие классов: 
     • Примеры: персона (PERSON), организация (ORG), локация (LOC), дата (DATE)
     • Минимум 2 класса для Good, 3+ для Excellent
   - Контекст: 
     • Сущности должны быть однозначны в контексте (например, "Яблоко" = компания, а не фрукт)
     • Текст не должен требовать внешних знаний для интерпретации

2. **Оценочные классы**:
   - Excellent: 5+ сущностей, 3+ класса, идеальный контекст
   - Good: 3-4 сущности, 2 класса, понятный контекст
   - Average: 2-3 сущности, 1-2 класса, контекст частично ясен
   - Poor: 1-2 сущности, 1 класс, неоднозначный контекст
   - Unusable: нет сущностей/бессвязный текст

3. **Формат ответа**:
   - JSON-строка (в ответе должна быть только json строка, без лишних рассуждений вне формата) с полями `reasoning_behind_score` (лаконичный анализ по всем критериям) и `score` (оценочный класс)
   - Пример: 
     {{"reasoning_behind_score": "5 сущностей (PERSON, ORG, DATE), контекст позволяет однозначно определить классы", "score": "Excellent"}}

Текст для анализа: {input_text}""",
                }])
        return (chat_response.choices[0].message.content) 
