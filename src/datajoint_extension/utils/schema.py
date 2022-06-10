import importlib
import inspect
import os
from pathlib import Path
from types import ModuleType
from typing import Any, Optional, Union

import datajoint as dj
import importlib_metadata
from datajoint_extension import __pkg_import_name__
from datajoint_extension.typing import T, TNFrameFile, TPathStrNone
from datajoint_extension.utils.generic import (
    chain_path_parts,
    frame_file,
    frame_package,
    pkg_relpath,
)


def dj_config_custom_entry(key: str, fallback: T, envar: str = "") -> T | str:
    value: T | str = os.getenv(envar, fallback) if envar else fallback
    custom = dj.config.get("custom", {})
    return custom.get(key, dj.config.get(key, value))


def get_prefix(fallback: str = __pkg_import_name__, *, sep: str = "_") -> str:
    """Get the database prefix from the `datajoint.config` property.

    Args:
        fallback (str, optional): Fallback value if prefix is not found. Defaults to
            `__pkg_import_name__`, which is the import name of the package.
        sep (str, optional): Separator to append at the end of the prefix string.

    Returns:
        string: The database prefix string.

    Examples:
        Using the default values.

            get_prefix()
            > 'my_pkg_name_'
    """
    entry = dj_config_custom_entry("database.prefix", fallback, "DJ_PREFIX")
    return f"{entry}{sep}" if entry else ""


def append_to_prefix(name: str) -> str:
    """Append a module name to the configured database prefix.

    Args:
        name (str): Name of module to append to database prefix.

    Returns:
        string: Extended database prefix.

    Examples:
        Using the default values.

            append_to_prefix('core')
            > 'my_pkg_name_core'
    """
    if not name:
        raise ValueError("string to append cannot be empty.")
    return get_prefix() + name


def set_missing_configs(
    *,
    db_prefix: Optional[str] = None,
    db_host: str = "localhost",
    db_user: str = "root",
    db_pwd: str = "simple",
    file: Path | str | None = None,
) -> None:
    """Set common DataJoint configuration values _only_ if they are missing from the
    existing config or configuration file.

    Args:
        db_prefix (str | None): Value to use for `"database.prefix"`.
        db_host (str): Value to use for `"database.host"`.
        db_user (str): Value to use for `"database.user"`.
        db_pwd (str): Value to use for `"database.password"`.
        file (Path | str | None): Path to initialize a datajoint `JSON` config
            file before setting the rest of the arguments.
    """

    if file:
        dj.config.load(file)

    dj.config["database.user"] = dj.config.get("database.user") or db_user
    dj.config["database.host"] = dj.config.get("database.host") or db_host
    dj.config["database.password"] = dj.config.get("database.password") or db_pwd
    dj.config["custom"] = {
        **{"database.prefix": db_prefix or get_prefix(sep="")},
        **dj.config.get("custom", {}),
    }


class LazySchema(dj.Schema):
    """Delayed activation of a Schema instance with stored context info.

    Overrides activation functionality from `datajoint.Schema`. This uses the packages'
    database prefix and call stack to determine a schema's name. The method
    `activate` must be called at least once at a later point in the pipeline.
    """

    def __init__(
        self,
        schema_name=None,
        context=None,
        *,
        connection=None,
        create_schema=True,
        create_tables=True,
        add_objects=None,
        module_name=None,
    ):
        call_stack = inspect.stack()[1]

        if not schema_name:
            schema_name = LazySchema.make_lazy_name(
                call_stack, root_schema_dirname="pipeline"
            )

        if not module_name:
            module_name = LazySchema.make_lazy_name(call_stack, use_schema_naming=False)

        self._lazy_module_name = module_name
        self._lazy_schema_name = schema_name

        super().__init__(
            schema_name=None,
            context=context,
            connection=connection,
            create_schema=create_schema,
            create_tables=create_tables,
            add_objects=self._module_objects(add_objects),
        )

    def activate(
        self,
        schema_name=None,
        *,
        connection=None,
        create_schema=None,
        create_tables=None,
        add_objects=None,
    ):
        if self.is_activated():
            return

        if add_objects is None:
            add_objects = self._lazy_module_name

        super().activate(
            schema_name=schema_name or self._lazy_schema_name,
            connection=connection,
            create_schema=create_schema,
            create_tables=create_tables,
            add_objects=self._module_objects(add_objects),
        )

    def _module_objects(
        self, module: Optional[Union[str, dict[str, Any], ModuleType]]
    ) -> Optional[dict]:
        if module is None or isinstance(module, dict):
            return module

        if isinstance(module, str):
            module = importlib.import_module(module)

        if not inspect.ismodule(module):
            raise TypeError(
                f"The argument 'module'<{type(module)}> must be a module's "
                "name, dictionary of objects, or ModuleType object."
            )

        return vars(module)

    @staticmethod
    def make_lazy_name(
        source: TNFrameFile,
        package: str = "",
        *,
        use_schema_naming: bool = True,
        root_schema_dirname: TPathStrNone = None,
    ) -> Union[str, None]:
        if source is None:
            source = inspect.stack()[1]
        package = package or frame_package(source, fallback="")
        src_file = frame_file(source)
        if not src_file or not src_file.is_absolute():
            return None
        src_file_relative_to_pkg = (
            pkg_relpath(src_file, package_import_name=package) if package else None
        )
        if use_schema_naming:
            relative_parts = (
                src_file_relative_to_pkg.parts
                if src_file_relative_to_pkg
                else (src_file.name,)
            )
            if src_file_relative_to_pkg and root_schema_dirname:
                root_schema_idx = [
                    i for i, x in enumerate(relative_parts) if x == root_schema_dirname
                ]
                if root_schema_idx and len(relative_parts) > 1:
                    relative_parts = tuple(relative_parts[root_schema_idx[0] + 1 :])
            schema_suffix = chain_path_parts(Path(*relative_parts), sep="_")
            return append_to_prefix(schema_suffix)
        return (
            chain_path_parts(package, src_file_relative_to_pkg)
            if src_file_relative_to_pkg
            else None
        )
