from reactpy_router.resolvers import ConversionInfo, ReactPyResolver


# Create a custom resolver that uses the following pattern: "{name:type}"
class CustomResolver(ReactPyResolver):
    def __init__(
        self,
        route,
        param_pattern=r"{(?P<name>\w+)(?P<type>:\w+)?}",  # Match parameters that use the "{name:type}" format
        converters={  # Enable matching for the following types: int, str, any
            "int": ConversionInfo(regex=r"\d+", func=int),
            "str": ConversionInfo(regex=r"[^/]+", func=str),
            "any": ConversionInfo(regex=r".*", func=str),
        },
    ) -> None:
        super().__init__(route, param_pattern, converters)
