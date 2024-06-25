from typing import TypedDict

from reactpy import component, html, run
from reactpy_router import browser_router, link, route

message_data: list["MessageDataType"] = [
    {"id": 1, "with": ["Alice"], "from": None, "message": "Hello!"},
    {"id": 2, "with": ["Alice"], "from": "Alice", "message": "How's it going?"},
    {"id": 3, "with": ["Alice"], "from": None, "message": "Good, you?"},
    {"id": 4, "with": ["Alice"], "from": "Alice", "message": "Good, thanks!"},
    {"id": 5, "with": ["Alice", "Bob"], "from": None, "message": "We meeting now?"},
    {"id": 6, "with": ["Alice", "Bob"], "from": "Alice", "message": "Not sure."},
    {"id": 7, "with": ["Alice", "Bob"], "from": "Bob", "message": "I'm here!"},
    {"id": 8, "with": ["Alice", "Bob"], "from": None, "message": "Great!"},
]


@component
def root():
    return browser_router(
        route("/", home()),
        route(
            "/messages",
            all_messages(),
            # we'll improve upon these manually created routes in the next section...
            route("/with/Alice", messages_with("Alice")),
            route("/with/Alice-Bob", messages_with("Alice", "Bob")),
        ),
        route("*", html.h1("Missing Link 🔗‍💥")),
    )


@component
def home():
    return html.div(
        html.h1("Home Page 🏠"),
        link("Messages", to="/messages"),
    )


@component
def all_messages():
    last_messages = {", ".join(msg["with"]): msg for msg in sorted(message_data, key=lambda m: m["id"])}
    return html.div(
        html.h1("All Messages 💬"),
        html.ul(
            [
                html.li(
                    {"key": msg["id"]},
                    html.p(
                        link(
                            f"Conversation with: {', '.join(msg['with'])}",
                            to=f"/messages/with/{'-'.join(msg['with'])}",
                        ),
                    ),
                    f"{'' if msg['from'] is None else '🔴'} {msg['message']}",
                )
                for msg in last_messages.values()
            ]
        ),
    )


@component
def messages_with(*names):
    messages = [msg for msg in message_data if set(msg["with"]) == names]
    return html.div(
        html.h1(f"Messages with {', '.join(names)} 💬"),
        html.ul(
            [
                html.li(
                    {"key": msg["id"]},
                    f"{msg['from'] or 'You'}: {msg['message']}",
                )
                for msg in messages
            ]
        ),
    )


run(root)

MessageDataType = TypedDict(
    "MessageDataType",
    {"id": int, "with": list[str], "from": str | None, "message": str},
)
