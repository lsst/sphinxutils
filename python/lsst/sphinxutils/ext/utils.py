"""Utilities for Sphinx extensions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Self

__all__ = ["RoleContent"]

ROLE_DISPLAY_PATTERN = re.compile(r"(?P<display>.+)<(?P<reference>.+)>")


@dataclass
class RoleContent:
    """Interpreted content of a Sphinx role."""

    last_component: bool
    """If `True`, the display should show only the last component of a
    namespace.
    """

    display: str | None
    """Custom display content."""

    ref: str
    """The reference content. If the role doesn't have a custom display, the
    reference will be the role's content. The ``ref`` never includes a ``~``
    prefix.
    """

    @classmethod
    def parse(cls, role_rawsource: str) -> Self:
        """Split the ``rawsource`` of a role into standard components.

        Parameters
        ----------
        role_rawsource : `str`
            The content of the role: its ``rawsource`` attribute.

        Returns
        -------
        RoleContent
            The parsed role content.

        Examples
        --------
        >>> RoleContent.parse('Tables <lsst.afw.table.Table>')
        RoleContent(last_component=False, display=Tables',
        ref='lsst.afw.table.Table')

        >>> RoleContent.parse('~lsst.afw.table.Table')
        RoleContent(last_component=True, display=None,
        ref='lsst.afw.table.Table')
        """
        if role_rawsource.startswith("~"):
            # Only the last part of a namespace should be shown.
            last_component = True
            # Strip that marker off
            role_rawsource = role_rawsource.lstrip("~")
        else:
            last_component = False

        match = ROLE_DISPLAY_PATTERN.match(role_rawsource)
        if match:
            display = match.group("display").strip()
            ref = match.group("reference").strip()
        else:
            # No suggested display
            display = None
            ref = role_rawsource.strip()

        return cls(last_component=last_component, display=display, ref=ref)
