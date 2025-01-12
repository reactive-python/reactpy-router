from reactpy_router.resolvers import ConversionInfo, ReactPyResolver


# Create a custom resolver that uses the following pattern: "{name:type}"
class CustomResolver(ReactPyResolver):
    # Match parameters that use the "<name:type>" format
    param_pattern = r"<(?P<name>\w+)(?P<type>:\w+)?>"

    # Enable matching for the following types: int, str, any
    converters = {
        "int": ConversionInfo(regex=r"\d+", func=int),
        "str": ConversionInfo(regex=r"[^/]+", func=str),
        "any": ConversionInfo(regex=r".*", func=str),
    }
