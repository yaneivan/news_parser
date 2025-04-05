def load_txt(file_path):
    """
    Loads a text file and returns its content as the only element of a list.

    :param file_path: Path to the text file.
    :return: A list containing the content of the text file as a single string.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text_content = file.read()
        return [text_content]
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Example usage:
# text_list = load_text('example.txt')
# print(text_list)