from typing import Any

from voice_helper.schema import FieldSpec, FieldType

__all__ = ["FieldSpec", "FieldType", "render_voice_session"]


def __getattr__(name: str) -> Any:
    if name == "render_voice_session":
        from voice_helper.streamlit_bridge import render_voice_session

        return render_voice_session
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)
