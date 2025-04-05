from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):
    @abstractmethod
    def summarize(self, input_text) -> str:
        """Returns summary of input text, just like a regular string"""
        pass 

    @abstractmethod
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
        pass

    @abstractmethod
    def rate(self, input_text) -> str:
        """Оценивает текст для обучения NER. Возвращает JSON-строку с полями 'score' (Excellent/Good/Average/Poor/Unusable) 
        и 'reasoning_behind_score' (обоснование оценки). Критерии:
        
        1. Количество сущностей: 5+ (Excellent), 3-4 (Good), 2-3 (Average), 1-2 (Poor), 0 (Unusable)
        2. Разнообразие классов: минимум 2 категории для Good, 3+ для Excellent
        3. Контекст: ясность и однозначность определения сущностей
        
        Пример вывода: 
        '{"reasoning_behind_score": "5+ сущностей из 3 категорий, ясный контекст", "score": "Excellent"}' 
        """