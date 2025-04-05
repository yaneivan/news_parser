from .base_provider import BaseLLMProvider
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Literal

load_dotenv()

class OpenAIStructuredProvider(BaseLLMProvider):
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

    def annotate(self, input_text) -> str:
        """Returns annotated text, in format:
        
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
        class Entity(BaseModel):
            entity: str
            types: List[str]

        class Entry(BaseModel):
            text: str
            entities: List[Entity]

        completion = self.client.beta.chat.completions.parse(
            temperature=0,
            model=self.model,
            messages=[
                {"role": "user", "content": f"""Analyze the given text and extract named entities. Each entity should be meticulously labeled according to its type for straightforward extraction. Классы должны быть написаны с большой буквы, и на русском языке. 
                Классы могут быть любые, чем разнообразнее, тем лучше.
                text - это оригинальный текст
                
                Входной текст:
                {input_text}"""}
            ],
            response_format=Entry,
        )
        return completion.choices[0].message.content

    def rate(self, input_text) -> str:
        """Оценивает текст для обучения NER. Возвращает JSON-строку с полями 'score' (Excellent/Good/Average/Poor/Unusable) 
        и 'reasoning_behind_score' (обоснование оценки). Критерии:
        
        1. Количество сущностей: 5+ (Excellent), 3-4 (Good), 2-3 (Average), 1-2 (Poor), 0 (Unusable)
        2. Разнообразие классов: минимум 2 категории для Good, 3+ для Excellent
        3. Контекст: ясность и однозначность определения сущностей
        
        Пример вывода: 
        '{"reasoning_behind_score": "5+ сущностей из 3 категорий, ясный контекст", "score": "Excellent"}' 
        """

        class RatingResponse(BaseModel):
            reasoning_behind_score: str
            score: Literal["Excellent", "Good", "Average", "Poor", "Unusable"]

        completion = self.client.beta.chat.completions.parse(
            temperature=0,
            model=self.model,
            messages=[
                {"role": "user", "content": f"""Проанализируй текст для обучения NER-модели. **Детализированная инструкция**:

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

Текст для анализа: {input_text}"""}
            ],
            response_format=RatingResponse,
        )
        return completion.choices[0].message.content