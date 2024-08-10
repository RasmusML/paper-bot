def parse_arguments(text: str) -> tuple[list[str], dict[str, str | bool]]:
    """Parse arguments from a string. Used by the clients."""
    args = _tokenize_arguments(text)
    return _parse_tokens(args)


def _parse_tokens(args: list[str]) -> tuple[list[str], dict[str, str | bool]]:
    args_positional: list[str] = []
    args_optional: dict[str, str | bool] = {}

    in_optional = False

    for arg in args:
        if arg.startswith("--"):
            arg2 = arg[2:]

            in_optional = True
            if "=" in arg:
                arg_name, arg_value = arg2.split("=")

                if arg_name in args_optional:
                    raise PositionalArgumentRedefinitionException(arg_name)

                args_optional[arg_name] = arg_value
            else:
                if arg2 in args_optional:
                    raise PositionalArgumentRedefinitionException(arg2)

                args_optional[arg2] = True

        else:
            if in_optional:
                raise UnexpectedPositionalArgumentException(arg)

            args_positional += [arg]

    args_positional = [_remove_argument_container(arg) for arg in args_positional]  # type: ignore
    args_optional = {k: _remove_argument_container(v) for k, v in args_optional.items()}

    return args_positional, args_optional


def _tokenize_arguments(text: str) -> list[str]:
    args = []

    arg = ""
    inside_apostrophe = False
    for c in text:
        if c == "'":
            inside_apostrophe = not inside_apostrophe

        if inside_apostrophe or (not c.isspace()):
            arg += c
        else:
            if not _is_whitespace(arg):
                args += [arg]
            arg = ""

    if not _is_whitespace(arg):
        args += [arg]

    if inside_apostrophe:
        raise ArgumentDidNotEndException()

    return args


def _is_whitespace(text: str) -> bool:
    return (text == "") or text.isspace()


def _remove_argument_container(text: str | bool) -> str | bool:
    if isinstance(text, str):
        return text.replace("'", "")
    return text


class ArgumentParserException(Exception):
    pass


class PositionalArgumentRedefinitionException(ArgumentParserException):
    def __init__(self, arg_name: str):
        super().__init__(f"Positional argument ({arg_name}) already defined")


class UnexpectedPositionalArgumentException(ArgumentParserException):
    def __init__(self, arg: str):
        super().__init__(f"Unexpected positional argument ({arg}) after optional arguments")


class ArgumentDidNotEndException(ArgumentParserException):
    def __init__(self):
        super().__init__('Argument did not end. Did you forget a "\'"?')
