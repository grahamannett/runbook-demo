import os
from enum import Enum

import ollama

from runbook.db_models import ChatInteraction
from runbook.rag_tools import prompt

AI_MODEL: str = "UNKNOWN"

# redefinitions


def chat(*args, **kwargs) -> ollama.ChatResponse:
    return ollama.chat(*args, **kwargs)


class LLMConfig:
    ai_provider = os.environ.get("AI_PROVIDER", "ollama")
    ai_provider_api_key = os.environ.get("AI_PROVIDER_API_KEY", "ollama")
    ai_provider_url = os.environ.get("AI_PROVIDER_URL", "http://localhost:11434/v1")

    # other
    ai_model = os.environ.get("AI_MODEL", "llama3.2-vision:11b")  # ollama default

    ai_model_chat_completion_kwargs = {
        # ignore these but keeping as they were on original
        # "top_k": 50
        # "truncate": 130560
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7,
        "repetition_penalty": 1,
        "stop": ["<|eot_id|>", "<|eom_id|>"],
    }


class ResponseType(Enum):
    STREAM = "stream"
    FULL = "full"


class LLMClient(ollama.Client):
    # all of these sdk's are annoying/problematic af


def _fix_chat_completion_kwargs_openai(kwargs: dict) -> dict:
    if "repetition_penalty" in kwargs:
        kwargs["frequency_penalty"] = kwargs.pop("repetition_penalty")
    if "truncate" in kwargs:
        kwargs["max_completion_tokens"] = kwargs.pop("truncate")
    if "top_k" in kwargs:
        kwargs.pop("top_k")

    return kwargs


_non_ollama_error = "Only using Ollama for now due to issues with Together"


def get_ai_client(ai_provider="ollama", ai_provider_url=None, ai_provider_api_key=None) -> LLMClient:
    match ai_provider:
        case "ollama":
            return LLMClient(base_url=ai_provider_url, api_key=ai_provider_api_key)
        case "openai":
            return LLMClient(api_key=ai_provider_api_key)
        case _:
            raise NotImplementedError(_non_ollama_error)


def get_ai_model(ai_provider: str = "ollama") -> str:
    match ai_provider:
        case "ollama":
            model_name = LLMConfig.ai_model
        case "openai":
            model_name = "gpt-4o"
        case _:
            raise ValueError(f"Invalid AI PROVIDER/MODEL: {ai_provider}")
    return model_name


def _create_messages(
    chat_interactions: list[ChatInteraction],
    prompt: str,
    system_prompt: str,
):
    messages = [{"role": "system", "content": [{"type": "text", "text": system_prompt}]}]
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


def create_html_parse_prompt(html_content: str, instructions: str = prompt.rag_html_parse_prompt):
    messages = _create_messages(
        chat_interactions=[],
        prompt=html_content,
        system_prompt=instructions,
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


def stream_get_content_openai_api(item):
    if item.choices and item.choices[0] and item.choices[0].delta:
        answer_text = item.choices[0].delta.content
        return answer_text
    return None
    # Ensure answer_text is not None before concatenation
    # if answer_text is not None:
    #     self.chat_interactions[-1].answer += answer_text
    # else:
    #     answer_text = ""
    #     self.chat_interactions[-1].answer += answer_text
