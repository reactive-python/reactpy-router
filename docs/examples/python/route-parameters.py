from reactpy import component, html, run

from reactpy_router import link, route, simple
from reactpy_router.core import use_params

message_data = [
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
    return simple.router(
        route("/", home()),
        route(
            "/messages",
            all_messages(),
            route("/with/{names}", messages_with()),  # note the path param
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
    last_messages = {
        ", ".join(msg["with"]): msg
        for msg in sorted(message_data, key=lambda m: m["id"])
    }
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
def messages_with():
    names = set(use_params()["names"].split("-"))  # and here we use the path param
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
