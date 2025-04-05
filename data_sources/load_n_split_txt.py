import os

def split_text(filepath, chunk_size_chars=1000, overlap_chars=200):
    """
    Читает файл, разбивает его текст на части с перекрытием и возвращает список чанков.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        start = 0
        chunks = []
        while start < len(text):
            end = min(start + chunk_size_chars, len(text))

            # Находим последний перенос строки в пределах overlap
            if end + overlap_chars < len(text):
                overlap = text[end:end + overlap_chars]
                newline_pos = overlap.rfind('\n')

                if newline_pos != -1:
                    end = end + newline_pos + 1

            chunk = text[start:end]
            chunks.append(chunk)
            start = end

        return chunks

    except FileNotFoundError:
        print(f"Ошибка: Файл '{filepath}' не найден.")
        return []
    except Exception as e:
        print(f"Ошибка при чтении или разбиении файла '{filepath}': {e}")
        return []



if __name__ == "__main__":
    filepath = "input_data/4pages.txt"  # Замените на ваш путь к файлу
    chunk_size = 1000
    overlap = 200

    chunks = split_text_in_memory(filepath, chunk_size, overlap)

    for i, chunk in enumerate(chunks):
        print(f"Обработка чанка {i+1}:")
        # ... ваш код для обработки chunk ...
        print(chunk)
        print("\n" * 4)