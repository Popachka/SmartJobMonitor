from pydantic_ai.models.google import GoogleModel, Model
from pydantic_ai.providers.google import GoogleProvider
from src.infrastructure.config import config


def get_google_model() -> Model:
    provider = GoogleProvider(api_key=config.GOOGLE_API_KEY)
    model = GoogleModel(config.GOOGLE_MODEL, provider=provider)

    return model