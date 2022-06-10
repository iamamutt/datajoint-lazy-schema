def get_version() -> str:
    """Get the version number for the current package.

    Returns:
        str: Version number taken from the installed package version.
    """
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover

    try:
        __version__ = version("datajoint-lazy-schema")
    except PackageNotFoundError:
        __version__ = "unknown"
    finally:
        del version, PackageNotFoundError

    return __version__


__version__: str = get_version()
version: str = __version__
__pkg_import_name__: str = "datajoint_extension"
