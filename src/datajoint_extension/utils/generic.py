import importlib.util
import inspect
import itertools
from importlib.metadata import PackageNotFoundError, packages_distributions
from pathlib import Path
from typing import NoReturn, Optional, Union, overload

from datajoint_extension import __pkg_import_name__
from datajoint_extension.typing import (
    TFrame,
    TNFrameFile,
    TNoneStr,
    TPartsPathStr,
    TPathStr,
    TPathStrNone,
    TStrTuple,
    is_frame,
    is_pathstr,
)


@overload
def pkg_abspath(
    import_name: TNoneStr = None, must_exist: bool = False
) -> Union[None, Path]:
    ...


@overload
def pkg_abspath(
    import_name: TNoneStr = None, must_exist: bool = True
) -> Union[NoReturn, Path]:
    ...


def pkg_abspath(import_name=None, must_exist=True):
    import_name = import_name or __pkg_import_name__
    pkg_spec = importlib.util.find_spec(import_name)
    if not pkg_spec:
        if must_exist:
            raise PackageNotFoundError(import_name)
        return None
    pkg_path: str = str(pkg_spec.origin)
    return Path(pkg_path).parent


def pkg_relpath(
    file: TPathStr,
    package_import_name: TNoneStr = None,
    package_root_path: TPathStrNone = None,
    append_to_package_root_path: TPathStrNone = None,
) -> Optional[Path]:
    src_path = Path(file)
    root_path = Path(package_root_path or pkg_abspath(package_import_name))
    if append_to_package_root_path:
        root_path = root_path.joinpath(append_to_package_root_path)
    return (
        src_path.relative_to(root_path) if src_path.is_relative_to(root_path) else None
    )


@overload
def as_path_parts(file_or_parts: TStrTuple) -> TStrTuple:
    ...


@overload
def as_path_parts(file_or_parts: TPathStr) -> TStrTuple:
    ...


def as_path_parts(file_or_parts: TPartsPathStr) -> TStrTuple:
    """_summary_

    no extension at end

    Args:
        file_or_parts (TPartsPathStr, TPathStr]): _description_

    Returns:
        tuple[str]: _description_
    """
    if file_or_parts is None:
        return TStrTuple()

    if isinstance(file_or_parts, (tuple, list)):
        parts = file_or_parts

    elif is_pathstr(file_or_parts):
        file_or_parts = Path(file_or_parts)
        parts = (
            *file_or_parts.parts[:-1],
            file_or_parts.stem,
        )
    else:
        raise TypeError(
            f"argument must be of type <{TPartsPathStr}>, "
            f"not '{type(file_or_parts)}'"
        )

    return (*filter(None, parts),)


def chain_path_parts(*args: TPartsPathStr, sep=".") -> str:
    part_gen = (as_path_parts(parts) for parts in args)
    return sep.join(itertools.chain.from_iterable(part_gen))


def frame_file(source: TNFrameFile) -> Union[Path, None]:
    if is_frame(source):
        return Path(source.filename)
    elif is_pathstr(source):
        return Path(source)
    else:
        return None


def frame_package(
    source: Optional[TFrame] = None, fallback: str = __pkg_import_name__
) -> str:
    if source is None:
        source = inspect.stack()[1]
    dist = packages_distributions()
    pkg = source.frame.f_locals.get("__package__")
    pkg = pkg.split(".", maxsplit=1)[0] if pkg else ""
    return pkg if pkg and pkg in dist else fallback
