"""Utilities for Sphinx extensions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Self

from docutils import nodes

__all__ = [
    "RoleContent",
    "make_section",
]

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
        >>> RoleContent.parse("Tables <lsst.afw.table.Table>")
        RoleContent(last_component=False, display=Tables',
        ref='lsst.afw.table.Table')

        >>> RoleContent.parse("~lsst.afw.table.Table")
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


def make_section(section_id: str, contents: list[nodes.Node] | None = None) -> nodes.section:
    """Make a docutils section node.

    Parameters
    ----------
    section_id
        Section identifier, which is appended to both the ``ids`` and ``names``
        attributes.
    contents
        List of docutils nodes that are inserted into the section.

    Returns
    -------
    docutils.nodes.section
        Docutils section node.
    """
    section = nodes.section()
    section["ids"].append(nodes.make_id(section_id))
    section["names"].append(section_id)
    if contents is not None:
        section.extend(contents)
    return section
