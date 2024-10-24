import operator
from typing import TypedDict

from reactpy import component, html, run

from reactpy_router import browser_router, link, route, use_params

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
            route("/with/{names}", messages_with()),  # note the path param
        ),
        route("{404:any}", html.h1("Missing Link 🔗‍💥")),
    )


@component
def home():
    return html.div(
        html.h1("Home Page 🏠"),
        link({"to": "/messages"}, "Messages"),
    )


@component
def all_messages():
    last_messages = {", ".join(msg["with"]): msg for msg in sorted(message_data, key=operator.itemgetter("id"))}
    messages = []
    for msg in last_messages.values():
        msg_hyperlink = link(
            {"to": f"/messages/with/{'-'.join(msg['with'])}"},
            f"Conversation with: {', '.join(msg['with'])}",
        )
        msg_from = f"{'' if msg['from'] is None else '🔴'} {msg['message']}"
        messages.append(html.li({"key": msg["id"]}, html.p(msg_hyperlink), msg_from))

    return html.div(
        html.h1("All Messages 💬"),
        html.ul(messages),
    )


@component
def messages_with():
    names = tuple(use_params()["names"].split("-"))  # and here we use the path param
    messages = [msg for msg in message_data if tuple(msg["with"]) == names]
    return html.div(
        html.h1(f"Messages with {', '.join(names)} 💬"),
        html.ul([
            html.li(
                {"key": msg["id"]},
                f"{msg['from'] or 'You'}: {msg['message']}",
            )
            for msg in messages
        ]),
    )


run(root)

MessageDataType = TypedDict(
    "MessageDataType",
    {"id": int, "with": list[str], "from": str | None, "message": str},
)
