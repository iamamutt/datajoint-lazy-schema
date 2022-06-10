"""Type aliases and other typing information used across modules."""

from inspect import FrameInfo
from pathlib import Path
from typing import Optional, TypeAlias, TypeGuard, TypeVar, Union

T = TypeVar("T")
TPathStr: TypeAlias = Union[Path, str]
TPathStrNone: TypeAlias = Optional[TPathStr]
TPartsPathStr: TypeAlias = Union[tuple[str, ...], TPathStr]
TStrTuple: TypeAlias = tuple[str, ...]
TNoneStr: TypeAlias = Optional[str]
TFrame: TypeAlias = FrameInfo
TFrameFile: TypeAlias = Union[TPathStr, TFrame]
TNFrameFile: TypeAlias = Optional[TFrameFile]


def is_frame(input: object) -> TypeGuard[TFrame]:
    """Determines whether and object is a frame stack."""
    return isinstance(input, FrameInfo)


def is_pathstr(input: object) -> TypeGuard[TPathStr]:
    """Determines whether and object is a frame stack."""
    return isinstance(input, (Path, str))
