from core.messages.use_cases.message import (
    create_a_message,
    delete_message,
    optimize_messages,
)

USECASES = {
    "messages/create_message": create_a_message,
    "messages/delete_message": delete_message,
    "messages/optimize": optimize_messages,
}
