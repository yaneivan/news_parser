#################
# Should be remade, after I changed project structure
#################





# @log_execution_time
# def summarize_with_gemeni(text):
#     import google.generativeai as genai
#     import os

#     api_key = os.environ["GOOGLE_API_KEY"]
#     model = os.environ["GOOGLE_MODEL"]

#     genai.configure(api_key=api_key)

#     generation_config = {
#     "temperature": 0,
#     "top_p": 0.95,
#     "top_k": 40,
#     "max_output_tokens": 8192,
#     "response_mime_type": "text/plain",
#     }

#     model = genai.GenerativeModel(
#         model_name=model,
#         generation_config=generation_config,
#         )
    
#     chat_session = model.start_chat(
#         history=[
#         ]
#     )

#     response = chat_session.send_message(f"Summarize the given text. Write summary without any introduction words. Твой ответ должен быть на русском языке.\n Text:{text}")

#     update_token_count('token_usage/input', response.usage_metadata.prompt_token_count)
#     update_token_count('token_usage/output', response.usage_metadata.candidates_token_count)

#     return (response.text)

# @log_execution_time
# def annotate_with_gemeni(text):
#     import google.generativeai as genai
#     import os
#     # import typing_extensions as typing  

#     api_key = os.environ["GOOGLE_API_KEY"]
#     model = os.environ["GOOGLE_MODEL"]

#     genai.configure(api_key=api_key)

#     generation_config = {
#     "temperature": 0,
#     "top_p": 0.95,
#     "top_k": 40,
#     "max_output_tokens": 8192,
#     "response_mime_type": "text/plain",
#     }

#     model = genai.GenerativeModel(
#         model_name=model,
#         generation_config=generation_config,
#         )

#     # from typing import TypedDict, List

#     import typing_extensions as typing

#     class Entity(typing.TypedDict):
#         entity: str
#         types: typing.List[str]

#     class Entry(typing.TypedDict):
#         text: str
#         entities: typing.List[Entity]

#     response = model.generate_content(
#         f"""Analyze the given text and extract named entities. Each entity should be meticulously labeled according to its type for straightforward extraction. Классы должны быть написаны с большой буквы, и на русском языке. 
#         Классы могут быть любые, чем разнообразнее, тем лучше.
#         text - это оригинальный текст
        
#         Входной текст:
#         {text}""",
#         generation_config=genai.GenerationConfig(
#             response_mime_type="application/json", response_schema=Entry
#         ),
#     )

#     update_token_count('token_usage/input', response.usage_metadata.prompt_token_count)
#     update_token_count('token_usage/output', response.usage_metadata.candidates_token_count)


#     return (response.text)

# @log_execution_time
# def rate_with_gemeni(text):
#     import typing_extensions as typing
#     import google.generativeai as genai
#     import enum
#     import os
    
#     api_key = os.environ["GOOGLE_API_KEY"]
#     model = os.environ["GOOGLE_MODEL"]

#     genai.configure(api_key=api_key)

#     generation_config = {
#     "temperature": 0,
#     "top_p": 0.95,
#     "top_k": 40,
#     "max_output_tokens": 8192,
#     "response_mime_type": "text/plain",
#     }

#     model = genai.GenerativeModel(
#         model_name=model,
#         generation_config=generation_config,
#         )

#     class Choice(enum.Enum):
#         Excellent = "Excellent"
#         Good = "Good"
#         Average = "Average"
#         Poor = "Poor"
#         Unusable = "Unusable"


#     class Score(typing.TypedDict):
#         reasoning_behind_score: str
#         score: Choice

#     response = model.generate_content(
#         f"""Вы — модель, которая помогает оценивать тексты, используемые для обучения алгоритмов Named Entity Recognition (NER). Вам будет предоставлен текст. Ваша задача:

#     Проанализировать текст и определить его качество с точки зрения пригодности для обучения NER.
#     Рассуждать по предложенным критериям и обосновать свою оценку.
#     Выдать окончательную оценку в формате JSON, где указываются причина оценки и сам класс из пяти вариантов.

# Критерии оценки

# Текст должен быть оценён по следующим параметрам:

#     Количество сущностей
#         Сущности — это имена людей, названия организаций, географические места, даты, события, продукты и другие подобные элементы.
#         Чем больше сущностей содержится в тексте, тем выше его ценность.
#         Минимальное количество для хорошего текста — три сущности. Если сущностей меньше, это снижает оценку.

#     Разнообразие классов сущностей
#         Текст должен содержать сущности из разных категорий (например, люди, организации, даты, места).
#         Если все сущности относятся к одному классу (например, только имена людей), это снижает оценку.

#     Ясность контекста
#         Сущности должны упоминаться в понятном и связном контексте.
#         Контекст позволяет отличить, например, человека с именем "Москва" от города Москва или компанию с названием "Яблоко" от фрукта.
#         Оценивайте текст в целом. Даже если он выглядит вырванным из более широкого контекста, это не снижает его ценности, если он содержит полезные сущности.

# Оценочные классы

# Используйте один из пяти классов качества:

#     Excellent
#         Количество сущностей: 5 и больше.
#         Разнообразие классов: несколько категорий (например, люди, места, события).
#         Контекст: полностью понятный и связный.

#     Good
#         Количество сущностей: 3–4.
#         Разнообразие классов: минимум две категории.
#         Контекст: в целом понятный, но могут быть небольшие сомнения.

#     Average
#         Количество сущностей: 2–3.
#         Разнообразие классов: однотипные или недостаточно разнообразные сущности.
#         Контекст: иногда неясен, но текст всё ещё полезен.

#     Poor
#         Количество сущностей: 1–2.
#         Разнообразие классов: все сущности однотипные.
#         Контекст: недостаточно понятный для практического использования.

#     Unusable
#         Количество сущностей: нет или почти нет.
#         Разнообразие классов: отсутствует.
#         Контекст: текст бессвязный, бессмысленный или пустой.

# Формат ответа

# Сначала напишите рассуждения о тексте, обосновывая выбор оценки по каждому из трёх критериев.


# Текст, который необходимо оценить:

# {text}""",
#         generation_config=genai.GenerationConfig(
#             response_mime_type="application/json", response_schema=Score
#         ),
#     )

    
#     update_token_count('token_usage/input', response.usage_metadata.prompt_token_count)
#     update_token_count('token_usage/output', response.usage_metadata.candidates_token_count)



#     return response.text



# if __name__ == "__main__":
#     # annotate_with_mistral()
#     # print(annotate_with_mistral("Каждый день приходится сталкиваться с таким случаем, когда человек, находясь внутри смертного греха, дерзает что-то просить у Бога. Очень часто вместо исполнения его просьбы бывает всё наоборот."))

#     print(annotate_with_gemeni("Каждый день приходится сталкиваться с таким случаем, когда человек, находясь внутри смертного греха, дерзает что-то просить у Бога. Очень часто вместо исполнения его просьбы бывает всё наоборот."))

#     print(annotate_with_gemeni("Атака беспилотников на Москву увеличила спрос на системы обнаружения и блокировки дронов среди промышленников, транспортников и граждан. Покупатели в основном используют устройства в зоне военных действий, но некоторые покупают их для личных нужд."))

