"""Sphinx extensions for documenting LSST Science Pipelines Tasks."""

from sphinx.application import Sphinx
from sphinx.util.typing import ExtensionMetadata

from lsst.sphinxutils.version import __version__

from ._crossrefs import (
    ConfigFieldReferenceRole,
    ConfigReferenceRole,
    TaskReferenceRole,
    pending_config_xref,
    pending_configfield_xref,
    pending_task_xref,
    process_pending_config_xref_nodes,
    process_pending_configfield_xref_nodes,
    process_pending_task_xref_nodes,
)


def setup(app: Sphinx) -> ExtensionMetadata:
    """Set up extensions for documenting Science Pipelines tasks."""
    app.add_role("lsst-task", TaskReferenceRole)
    app.add_role("lsst-config", ConfigReferenceRole)
    app.add_role("lsst-config-field", ConfigFieldReferenceRole)

    app.add_node(pending_task_xref)
    app.add_node(pending_config_xref)
    app.add_node(pending_configfield_xref)

    app.connect("doctree-resolved", process_pending_task_xref_nodes)
    app.connect("doctree-resolved", process_pending_config_xref_nodes)
    app.connect("doctree-resolved", process_pending_configfield_xref_nodes)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
