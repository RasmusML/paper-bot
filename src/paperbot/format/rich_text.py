"""Slack Rich Text Block Builder.

References
----------
- https://api.slack.com/reference/block-kit/blocks

"""

import inspect
from typing import Any


def rich_text_block(elements: list[Any]) -> dict[str, Any]:
    return {"type": "rich_text", **_expand_params()}


def divider_block() -> dict[str, Any]:
    return {"type": "divider", **_expand_params()}


def rich_text_section(elements: list[Any]) -> dict[str, Any]:
    return {"type": "rich_text_section", **_expand_params()}


def text(text: str, style: dict[str, bool] = None) -> dict[str, Any]:
    return {"type": "text", **_expand_params()}


def link(url: str, text: str = None, unsafe: bool = None, style: dict[str, bool] = None) -> dict[str, Any]:
    return {"type": "link", **_expand_params()}


def style(bold: bool = None, italic: bool = None, strike: bool = None, code: bool = None) -> dict[str, Any]:
    return _expand_params()


def _expand_params() -> dict[str, Any]:
    return _filter_optionals(_scope(n_frames_to_pop=2))


def _scope(n_frames_to_pop: int = 1) -> dict[str, Any]:
    frame = inspect.currentframe()

    for _ in range(n_frames_to_pop):
        frame = frame.f_back

    keys, _, _, values = inspect.getargvalues(frame)
    kwargs = {}
    for key in keys:
        if key != "self":
            kwargs[key] = values[key]
    return kwargs


def _filter_optionals(optionals: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in optionals.items() if v is not None}
