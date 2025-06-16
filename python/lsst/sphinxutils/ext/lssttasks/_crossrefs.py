"""Targets and reference roles for LSST Task objects."""

from __future__ import annotations

from docutils import nodes
from docutils.nodes import Element, Inline, Node, literal, make_id, reference, system_message
from sphinx.application import Sphinx
from sphinx.util.docutils import ReferenceRole
from sphinx.util.logging import getLogger

from ..utils import RoleContent

__all__ = (
    "format_task_id",
    "format_config_id",
    "format_configfield_id",
    "pending_task_xref",
    "TaskReferenceRole",
    "ConfigReferenceRole",
    "ConfigFieldReferenceRole",
    "process_pending_task_xref_nodes",
    "process_pending_config_xref_nodes",
    "process_pending_configfield_xref_nodes",
)


def format_task_id(task_class_name: str) -> str:
    """Format the ID of a task topic reference node.

    Parameters
    ----------
    task_class_name
        Importable name of the task class. For example,
        ``'lsst.pipe.tasks.processCcd.ProcessCcdTask'``.

    Returns
    -------
    str
        Node ID for the task topic reference node.
    """
    return make_id(f"lsst-task-{task_class_name}")


def format_config_id(config_class_name: str) -> str:
    """Format the ID of a standalone config topic reference node.

    Parameters
    ----------
    config_class_name
        Importable name of the config class. For example,
        ``'lsst.pipe.tasks.processCcd.ProcessCcdConfig'``.

    Returns
    -------
    str
        Node ID for the config topic reference node.
    """
    return make_id(f"lsst-config-{config_class_name}")


def format_configfield_id(config_class_name: str, field_name: str) -> str:
    """Format the ID of a configuration field topic.

    Parameters
    ----------
    config_class_name
        Importable name of the config class. For example,
        ``'lsst.pipe.tasks.processCcd.ProcessCcdConfig'``.
    field_name
        Name of the configuration field attribute.

    Returns
    -------
    node_id
        Node ID for the config topic reference node.
    """
    return make_id(f"lsst-configfield-{config_class_name}-{field_name}")


# docutils notes are traditionally lowercase


class pending_task_xref(Inline, Element):  # noqa: N801
    """Node for task cross-references that cannot be resolved without complete
    information about all documents.
    """


class pending_config_xref(Inline, Element):  # noqa: N801
    """Node for config cross-references (to ``lsst-config`` directives) that
    cannot be resolved without complete information about all documents.
    """


class pending_configfield_xref(Inline, Element):  # noqa: N801
    """Node for cross-references to configuration field nodes that
    cannot be resolved without complete information about all documents.
    """


class TaskReferenceRole(ReferenceRole):
    """Sphinx role for referencing task topics created by the ``lsst-task``
    directive.
    """

    def run(self) -> tuple[list[Node], list[system_message]]:
        """Process the role.

        Notes
        -----
        The task reference role leaves a ``pending_task_xref`` node that will
        be later resolved by the ``process_pending_task_xref_nodes`` function
        during the ``doctree-resolved`` event.
        """
        node = pending_task_xref(rawsource=self.text)
        return [node], []


def process_pending_task_xref_nodes(app: Sphinx, doctree: Node, fromdocname: str) -> None:
    """Process the ``pending_task_xref`` nodes during the ``doctree-resolved``
    event to insert links to the locations of ``lsst-task-topic`` directives.
    """
    logger = getLogger(__name__)
    env = app.builder.env

    for node in doctree.traverse(pending_task_xref):
        content: list[Node] = []

        # The source of the node is the class name the user entered via the
        # lsst-task-topic role. For example:
        # lsst.pipe.tasks.processCcd.ProcessCcdTask
        role_parts = RoleContent.parse(node.rawsource)
        task_id = format_task_id(role_parts.ref)
        if role_parts.display:
            # user's custom display text
            display_text = role_parts.display
        elif role_parts.last_component:
            # just the name of the class
            display_text = role_parts.ref.split(".")[-1]
        else:
            display_text = role_parts.ref
        link_label = literal()
        link_label += nodes.Text(display_text)

        if hasattr(env, "lsst_task_topics") and task_id in env.lsst_task_topics:
            # A task topic, marked up with the lsst-task-topic directive is
            # available
            task_data = env.lsst_task_topics[task_id]

            ref_node = reference("", "")
            ref_node["refdocname"] = task_data["docname"]
            ref_node["refuri"] = app.builder.get_relative_uri(fromdocname, task_data["docname"])
            ref_node["refuri"] += "#" + task_data["target"]["refid"]

            ref_node += link_label

            content.append(ref_node)

        else:
            # Fallback if the task topic isn't known. Just print the label text
            content.append(link_label)

            message = "lsst-task could not find a reference to %s"
            logger.warning(message, role_parts.ref, location=node)

        # replacing the pending_task_xref node with this reference
        node.replace_self(content)


class ConfigReferenceRole(ReferenceRole):
    """Sphinx role for referencing config topics created by the
    ``lsst-config-topic`` directive.
    """

    def run(self) -> tuple[list[Node], list[system_message]]:
        """Process the role.

        Notes
        -----
        The config reference role leaves a ``pending_config_xref`` node that
        will be later resolved by the ``process_pending_config_xref_nodes``
        function during the ``doctree-resolved`` event.
        """
        node = pending_config_xref(rawsource=self.text)
        return [node], []


def process_pending_config_xref_nodes(app: Sphinx, doctree: Node, fromdocname: str) -> None:
    """Process the ``pending_config_xref`` nodes during the
    ``doctree-resolved`` event to insert links to the locations of
    ``lsst-config-topic`` directives.

    See Also
    --------
    `config_ref_role`
    `ConfigTopicTargetDirective`
    `pending_config_xref`
    """
    logger = getLogger(__name__)
    env = app.builder.env

    for node in doctree.traverse(pending_config_xref):
        content: list[Node] = []

        # The source of the node is the content the authored entered in the
        # lsst-config role
        role_parts = RoleContent.parse(node.rawsource)
        config_id = format_config_id(role_parts.ref)
        if role_parts.display:
            # user's custom display text
            display_text = role_parts.display
        elif role_parts.last_component:
            # just the name of the class
            display_text = role_parts.ref.split(".")[-1]
        else:
            display_text = role_parts.ref
        link_label = literal()
        link_label += nodes.Text(display_text)

        if hasattr(env, "lsst_task_topics") and config_id in env.lsst_task_topics:
            # A config topic, marked up with the lsst-task directive is
            # available
            config_data = env.lsst_task_topics[config_id]

            ref_node = reference("", "")
            ref_node["refdocname"] = config_data["docname"]
            ref_node["refuri"] = app.builder.get_relative_uri(fromdocname, config_data["docname"])
            ref_node["refuri"] += "#" + config_data["target"]["refid"]

            ref_node += link_label

            content.append(ref_node)

        else:
            # Fallback if the config topic isn't known. Just print the
            # role's formatted content.
            content.append(link_label)

            message = "lsst-config could not find a reference to %s"
            logger.warning(message, role_parts.ref, location=node)

        # replacing the pending_config_xref node with this reference
        node.replace_self(content)


class ConfigFieldReferenceRole(ReferenceRole):
    """Sphinx role for referencing configuration field topics created by the
    ``lsst-config-field``, ``lsst-task-config-subtasks``, and
    ``lsst-task-config-subtasks`` directives.
    """

    def run(self) -> tuple[list[Node], list[system_message]]:
        """Process the role.

        Notes
        -----
        The config field reference role leaves a ``pending_configfield_xref``
        node that will be later resolved by the
        ``process_pending_configfield_xref_nodes`` function during the
        ``doctree-resolved`` event.
        """
        node = pending_configfield_xref(rawsource=self.text)
        return [node], []


def process_pending_configfield_xref_nodes(app: Sphinx, doctree: Node, fromdocname: str) -> None:
    """Process the ``pending_configfield_xref`` nodes during the
    ``doctree-resolved`` event to insert links to the locations of
    configuration field nodes.

    See Also
    --------
    `format_configfield_id`
    `configfield_ref_role`
    `pending_configfield_xref`
    """
    logger = getLogger(__name__)
    env = app.builder.env

    for node in doctree.traverse(pending_configfield_xref):
        content: list[Node] = []

        # The source is the text the user entered into the role, which is
        # the importable name of the config class's and the attribute
        role_parts = RoleContent.parse(node.rawsource)
        namespace_components = role_parts.ref.split(".")
        field_name = namespace_components[-1]
        class_namespace = ".".join(namespace_components[:-1])
        configfield_id = format_configfield_id(class_namespace, field_name)
        if role_parts.display:
            # user's custom display text
            display_text = role_parts.display
        elif role_parts.last_component:
            # just the name of the class
            display_text = role_parts.ref.split(".")[-1]
        else:
            display_text = role_parts.ref

        if hasattr(env, "lsst_configfields") and configfield_id in env.lsst_configfields:
            # A config field topic is available
            configfield_data = env.lsst_configfields[configfield_id]

            ref_node = reference("", "")
            ref_node["refdocname"] = configfield_data["docname"]
            ref_node["refuri"] = app.builder.get_relative_uri(fromdocname, configfield_data["docname"])
            ref_node["refuri"] += "#" + configfield_id

            link_label = literal()
            link_label += nodes.Text(display_text)
            ref_node += link_label

            content.append(ref_node)

        else:
            # Fallback if the config field isn't known. Just print the Config
            # field attribute name
            literal_node = literal()
            literal_node += nodes.Text(field_name)
            content.append(literal_node)

            message = "lsst-config-field could not find a reference to %s"
            logger.warning(message, role_parts.ref, location=node)

        # replacing the pending_configfield_xref node with this reference
        node.replace_self(content)
