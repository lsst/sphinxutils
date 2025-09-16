"""Utilities for the lssttask extensions."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from importlib import import_module
from typing import TYPE_CHECKING, Any

from lsst.pex.config import Config
from lsst.pipe.base import Task
from sphinx.errors import SphinxError
from sphinx.util.docstrings import prepare_docstring
from sphinx.util.inspect import getdoc
from sphinx.util.logging import getLogger

if TYPE_CHECKING:
    from lsst.pex.config import ConfigurableField, Field, RegistryField

__all__ = [
    "get_docstring",
    "extract_docstring_summary",
    "get_type",
    "get_task_config_fields",
    "get_subtask_fields",
    "typestring",
    "get_task_config_fields",
    "get_subtask_fields",
]


def get_docstring(obj: object) -> list[str]:
    """Extract the docstring from an object as individual lines.

    Parameters
    ----------
    obj
        The Python object (class, function or method) to extract docstrings
        from.

    Returns
    -------
    `list` of `str`
        Individual docstring lines with common indentation removed, and
        newline characters stripped.

    Notes
    -----
    If the object does not have a docstring, a docstring with the content
    ``"Undocumented."`` is created.
    """
    docstring = getdoc(obj, allow_inherited=True)
    if docstring is None:
        logger = getLogger(__name__)
        logger.warning("Object %s doesn't have a docstring.", obj)
        docstring = "Undocumented"
    return prepare_docstring(docstring)


def extract_docstring_summary(docstring: list[str]) -> str:
    """Get the first summary sentence from a docstring.

    Parameters
    ----------
    docstring
        Typically the output from `get_docstring`.

    Returns
    -------
    `str`
        The plain-text summary sentence from the docstring.
    """
    summary_lines = []
    for line in docstring:
        if line == "":
            break
        else:
            summary_lines.append(line)
    return " ".join(summary_lines)


def get_type(type_name: str) -> type:
    """Get a type given its importable name.

    Parameters
    ----------
    str
        Name of the Python type, such as ``mypackage.MyClass``.

    Returns
    -------
    type
        The object's type.
    """
    parts = type_name.split(".")
    if len(parts) < 2:
        raise SphinxError(f"Type must be fully-qualified, of the form ``module.MyClass``. Got: {type_name}")
    module_name = ".".join(parts[0:-1])
    name = parts[-1]
    return getattr(import_module(module_name), name)


def typestring(obj_type: Any) -> str:
    """Make a string for the object's type.

    Parameters
    ----------
    obj
        Python object type.

    Returns
    -------
    str
        String representation of the object's type. This is the type's
        importable namespace.

    Examples
    --------
    >>> import docutils.nodes
    >>> para = docutils.nodes.paragraph()
    >>> typestring(type(para))
    'docutils.nodes.paragraph'
    """
    obj_type = type(obj_type)
    return ".".join((obj_type.__module__, obj_type.__name__))


def get_task_config_class(task_name: str) -> type[Config]:
    """Get the Config class for a task given its fully-qualified name.

    Parameters
    ----------
    task_name : `str`
        Name of the task, such as
        ``lsst.pipe.tasks.calibrate.CalibrateTask``.

    Returns
    -------
    type
        The configuration class type (not an instance) corresponding to the
        task.
    """
    task_class = get_type(task_name)

    if not isinstance(task_class, Task):
        raise SphinxError(f"Task {task_name} is not a Task subclass.")

    return task_class.ConfigClass


def get_task_config_fields(config_class: type[Config]) -> dict[str, Field]:
    """Get all configuration Fields from a Config class.

    Parameters
    ----------
    config_class : ``lsst.pipe.base.Config``-type
        The configuration class (not an instance) corresponding to a Task.

    Returns
    -------
    config_fields : `dict`
        Mapping where keys are the config attribute names and values are
        subclasses of ``lsst.pex.config.Field``. The mapping is alphabetically
        ordered by attribute name.
    """
    from lsst.pex.config import Field

    def is_config_field(obj: object) -> bool:
        return isinstance(obj, Field)

    return _get_alphabetical_members(config_class, is_config_field)


def get_subtask_fields(config_class: type[Config]) -> dict[str, ConfigurableField | RegistryField]:
    """Get all configurable subtask fields from a Config class.

    Parameters
    ----------
    config_class : ``lsst.pipe.base.Config``-type
        The configuration class (not an instance) corresponding to a Task.

    Returns
    -------
    subtask_fields : `dict`
        Mapping where keys are the config attribute names and values are
        subclasses of ``lsst.pex.config.ConfigurableField`` or
        ``RegistryField``). The mapping is alphabetically ordered by
        attribute name.
    """
    from lsst.pex.config import ConfigurableField, RegistryField

    def is_subtask_field(obj: object) -> bool:
        return isinstance(obj, ConfigurableField | RegistryField)

    return _get_alphabetical_members(config_class, is_subtask_field)


def _get_alphabetical_members(obj: object, predicate: Callable) -> dict[str, Any]:
    """Get members of an object, sorted alphabetically.

    Parameters
    ----------
    obj
        An object type.
    predicate
        Callable that takes an attribute and returns a bool of whether the
        attribute should be returned or not.

    Returns
    -------
    members
        Dictionary of

        - Keys: attribute name
        - Values: attribute

        The dictionary is ordered according to the attribute name.

    Notes
    -----
    This uses the insertion-order-preserved nature of `dict` in Python 3.6+.

    See Also
    --------
    `inspect.getmembers`
    """
    fields = dict(inspect.getmembers(obj, predicate))
    keys = list(fields.keys())
    keys.sort()
    return {k: fields[k] for k in keys}
