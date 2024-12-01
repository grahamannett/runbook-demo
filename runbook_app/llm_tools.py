import os

from together import Together

from runbook_app.page_chat.chat_messages.model_chat_interaction import ChatInteraction

AI_MODEL: str = "UNKNOWN"


def get_ai_client() -> Together:
    ai_provider = os.environ.get("AI_PROVIDER")
    match ai_provider:
        case "ollama":
            return Together(
                base_url="http://localhost:11434/v1",
                api_key="ollama",
            )

        case "together":
            return Together(
                api_key=os.environ.get("TOGETHER_API_KEY"),
            )
        case "openai":
            raise NotImplementedError("Only using Ollama/Together for now")

        case _:
            raise ValueError(f"Invalid AI Provider: {ai_provider}")


def get_ai_model() -> str:
    global AI_MODEL
    ai_model = os.environ.get("AI_PROVIDER")
    match ai_model:
        case "ollama":
            AI_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2-vision:11b")
        case "openai":
            raise NotImplementedError("Only using Ollama/Together for now")
        case "together":
            AI_MODEL = "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo"
        case _:
            raise ValueError(f"Invalid AI PROVIDER/MODEL: {ai_model}")
    return AI_MODEL


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

    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "You are a helpful assistant. Respond in markdown.",
                },
            ],
        },
    ]
    for chat_interaction in chat_interactions:
        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": chat_interaction.prompt,
                    },
                ],
            },
        )
        messages.append(
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": chat_interaction.answer,
                    },
                ],
            },
        )

    messages.append(
        {
            "role": "user",
            "content": prompt,
        },
    )
    return messages
