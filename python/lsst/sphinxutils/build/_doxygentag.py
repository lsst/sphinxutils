"""Utilities for working with Doxygen tag files."""

__all__ = ["get_tag_entity_names"]

from collections.abc import Sequence
from pathlib import Path
from xml.etree import ElementTree


def get_tag_entity_names(tag_path: str | Path, kinds: Sequence[str] | None = None) -> list[str]:
    """Get the list of API names in a Doxygen tag file.

    Parameters
    ----------
    tag_path
        File path of the Doxygen tag file.
    kinds
        If provided, a sequence of API kinds to include in the listing.
        Doxygen types are:

        - namespace
        - struct
        - class
        - file
        - define
        - group
        - variable
        - typedef
        - enumeration
        - function

    Returns
    -------
    list
        List of API names.
    """
    doc = ElementTree.parse(str(tag_path))
    root = doc.getroot()
    names = []
    for compound in root.findall("compound"):
        kind = compound.get("kind")
        name = compound.findtext("name")
        if name and (kinds is None or kind in kinds):
            names.append(name)
        for member in compound.findall("member"):
            member_kind = member.get("kind")
            member_name = member.findtext("name")
            if member_name and (kinds is None or member_kind in kinds):
                names.append(member_name)
    names.sort()
    return names
