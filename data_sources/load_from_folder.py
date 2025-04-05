import os

def load_from_folder(folder_path):
    """
    Загружает все текстовые файлы из папки и возвращает их содержимое в виде списка.

    :param folder_path: Путь к папке с текстовыми файлами.
    :return: Список, где каждый элемент — содержимое одного файла.
    """
    texts = []  # Список для хранения содержимого файлов

    # Проверяем, существует ли папка
    if not os.path.exists(folder_path):
        print(f"Ошибка: Папка '{folder_path}' не найдена.")
        return texts

    # Итерируемся по всем файлам в папке
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)  # Полный путь к файлу

        # Проверяем, что это файл (а не подпапка) и имеет расширение .txt
        if os.path.isfile(file_path) and filename.endswith('.txt'):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    text_content = file.read()  # Читаем содержимое файла
                    texts.append(text_content)  # Добавляем в список
            except Exception as e:
                print(f"Ошибка при чтении файла '{filename}': {e}")

    return texts

# Пример использования:
# texts = load_from_folder('path/to/folder')
# print(texts)