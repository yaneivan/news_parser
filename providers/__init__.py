from .openai_provider import OpenAIProvider
from .openai_structured_provider import OpenAIStructuredProvider

def get_provider(provider_name: str):
    providers = {
        "openai": OpenAIProvider,
        "structured_openai": OpenAIStructuredProvider,
        # Добавьте другие провайдеры здесь
    }
    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Провайдер {provider_name} не поддерживается")
    return provider_class()