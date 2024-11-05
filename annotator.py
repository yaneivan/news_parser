from dotenv import load_dotenv

load_dotenv()

def summarize_with_mistral(text):
    from mistralai import Mistral
    import os

    api_key = os.environ["MISTRAL_API_KEY"]
    model = os.environ["MODEL"]

    client = Mistral(api_key=api_key)

    chat_response = client.chat.complete(
        model= model,
        messages = [
            {
                "role": "user",
                "content": f"Summarize the given text. Write summary without any introduction words.\n Text:{text}",
            },
        ]
    )
    return (chat_response.choices[0].message.content)


def create_prompt_for_entity_extraction(text):
    prompt = """
**Objective:**
Analyze the given text and extract named entities. Each entity should be meticulously labeled according to its type for straightforward extraction.

**Format Requirements:**
- The output should be formatted in JSON, containing the text and the corresponding entities list.
- Each entity in the text should be accurately marked and annotated in the 'entities' list.

**Entity Annotation Details:**
- Entities spans can be nested within other entities.
- A single entity may be associated with multiple types. list them in the key "types".

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

def annotate_with_mistral(text):
    from mistralai import Mistral
    import os

    api_key = os.environ["MISTRAL_API_KEY"]
    model = os.environ["MODEL"]

    client = Mistral(api_key=api_key)

    prompt = create_prompt_for_entity_extraction(text)

    chat_response = client.chat.complete(
        model= model,
        messages = [
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )
    return (chat_response.choices[0].message.content)

if __name__ == "__main__":
    # annotate_with_mistral()
    print(annotate_with_mistral("Каждый день приходится сталкиваться с таким случаем, когда человек, находясь внутри смертного греха, дерзает что-то просить у Бога. Очень часто вместо исполнения его просьбы бывает всё наоборот."))