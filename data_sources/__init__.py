from .telegram_channel import load_texts
from .load_from_txt import load_txt
from .load_from_folder import load_from_folder
from .load_n_split_txt import split_text

def get_source(source: str):
    """
    Возвращает функцию загрузки данных для указанного источника.

    :param source: Название источника данных ("telegram", "txt", "folder").
    :return: Функцию загрузки данных.
    :raises ValueError: Если источник данных не поддерживается.
    """
    providers = {
        "telegram": load_texts,
        "txt": load_txt,
        "folder": load_from_folder,
        "splitter": split_text,
    }
    provider_function = providers.get(source.lower())
    if not provider_function:
        raise ValueError(f"Источник данных {source} не поддерживается")
    return provider_function