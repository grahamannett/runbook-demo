from runbook_app.page_chat.chat_messages.model_chat_interaction import ChatInteraction


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
