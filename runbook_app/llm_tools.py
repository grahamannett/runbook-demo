import os

from together import Together

from runbook_app.db_models import ChatInteraction

AI_MODEL: str = "UNKNOWN"


class LLMConfig:
    ai_provider = os.environ.get("AI_PROVIDER", "ollama")
    ai_provider_url = os.environ.get("AI_PROVIDER_URL", "http://localhost:11434/v1")
    ai_provider_api_key = os.environ.get("AI_PROVIDER_API_KEY", "ollama")

    # other
    ai_model = os.environ.get("AI_MODEL", "llama3.2-vision:11b")  # ollama default


def get_ai_client(ai_provider="ollama", ai_provider_url=None, ai_provider_api_key=None) -> Together:
    match ai_provider:
        case "ollama":
            return Together(base_url=ai_provider_url, api_key=ai_provider_api_key)
        case "together":
            return Together(api_key=ai_provider_api_key)
        case "openai":
            raise NotImplementedError("Only using Ollama/Together for now")
        case _:
            raise ValueError(f"Invalid AI Provider: {ai_provider}")


def get_ai_model(ai_provider: str = "ollama") -> str:
    global model_name
    match ai_provider:
        case "ollama":
            model_name = LLMConfig.ai_model
        case "openai":
            raise NotImplementedError("Only using Ollama/Together for now")
        case "together":
            model_name = "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo"
        case _:
            raise ValueError(f"Invalid AI PROVIDER/MODEL: {ai_provider}")
    return model_name


def _create_messages(
    chat_interactions: list[ChatInteraction],
    prompt: str,
    system_prompt: str,
):
    messages = [
        {
            "role": "system",
            "content": [{"type": "text", "text": system_prompt}],
        },
    ]
    for chat_interaction in chat_interactions:
        messages.append({"role": "user", "content": [{"type": "text", "text": chat_interaction.prompt}]})
        messages.append({"role": "assistant", "content": [{"type": "text", "text": chat_interaction.answer}]})

    messages.append({"role": "user", "content": prompt})
    return messages


def create_messages_for_chat_completion(
    chat_interactions: list[ChatInteraction],
    prompt: str,
) -> list[dict[str, str | list[dict[str, str]]]]:
    """
    Create a list of messages for chat completion based on chat interactions and a new prompt.

    Args:
        chat_interactions (list[ChatInteraction]): A list of previous chat interactions.
        prompt (str): The new prompt to be added to the messages.

    Returns:
        list[dict[str, str | list[dict[str, str]]]]: A list of messages formatted for chat completion.
    """

    messages = _create_messages(
        chat_interactions=chat_interactions,
        prompt=prompt,
        system_prompt="You are a helpful assistant.",
    )

    return messages


def create_messages_for_runbook_completion(
    chat_interactions: list[ChatInteraction],
    prompt: str,
) -> list[dict[str, str | list[dict[str, str]]]]:
    messages = _create_messages(
        chat_interactions=chat_interactions,
        prompt=prompt,
        system_prompt=".",
    )

    return messages
