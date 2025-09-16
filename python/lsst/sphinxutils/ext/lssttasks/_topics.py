"""Directives that mark task and configurable topics / pages."""

from __future__ import annotations

from docutils import nodes
from sphinx.errors import SphinxError
from sphinx.util.docutils import SphinxDirective
from sphinx.util.logging import getLogger

from ._crossrefs import format_config_id, format_task_id
from ._utils import extract_docstring_summary, get_docstring, get_type

__all__ = [
    "ConfigTopicDirective",
    "ConfigurableTopicDirective",
    "TaskTopicDirective",
]


class BaseTopicDirective(SphinxDirective):
    """Base for topic target directives."""

    _logger = getLogger(__name__)

    has_content = True
    required_arguments = 1

    @property
    def directive_name(self) -> str:
        raise NotImplementedError

    def get_type(self, class_name: str) -> str:
        """Get the topic type."""
        raise NotImplementedError

    def get_target_id(self, class_name: str) -> str:
        """Get the reference ID for this topic directive."""
        raise NotImplementedError

    def run(self) -> list[nodes.Node]:
        """Run the directive.

        Returns
        -------
        `list`
            Nodes to add to the doctree.
        """
        try:
            class_name = self.arguments[0]
        except IndexError:
            raise SphinxError(f"{self.directive_name} directive requires a class name as an argument")
        self._logger.debug("%s using class %s", self.directive_name, class_name)

        summary_node = self._create_summary_node(class_name)

        # target_id = format_task_id(class_name)
        target_id = self.get_target_id(class_name)
        target_node = nodes.target("", "", ids=[target_id])

        # Store these task/configurable topic nodes in the environment for
        # later cross referencing.
        if not hasattr(self.env, "lsst_task_topics"):
            setattr(self.env, "lsst_task_topics", {})
        lsst_task_topics = getattr(self.env, "lsst_task_topics")
        lsst_task_topics[target_id] = {
            "docname": self.env.docname,
            "lineno": self.lineno,
            "target": target_node,
            "summary_node": summary_node,
            "fully_qualified_name": class_name,
            "type": self.get_type(class_name),
        }

        return [target_node]

    def _create_summary_node(self, class_name: str) -> list[nodes.Node]:
        if len(self.content) > 0:
            return self.parse_content_to_nodes()
        else:
            # Fallback is to get summary sentence from class docstring.
            return self._get_docstring_summary(class_name)

    def _get_docstring_summary(self, class_name: str) -> list[nodes.Node]:
        obj = get_type(class_name)
        summary_text = extract_docstring_summary(get_docstring(obj))
        if summary_text == "":
            summary_text = "No description available."
        summary_text = summary_text.strip() + "\n"
        return self.parse_text_to_nodes(summary_text)


class ConfigurableTopicDirective(BaseTopicDirective):
    """``lsst-configurable-topic`` directive that labels a Configurable's topic
    page.

    Configurables are essentially generalized tasks. They have a ConfigClass,
    but don't have run methods.
    """

    directive_name = "lsst-configurable-topic"
    """Default name of this directive."""

    def get_type(self, class_name: str) -> str:
        return "Configurable"

    def get_target_id(self, class_name: str) -> str:
        return format_task_id(class_name)


class TaskTopicDirective(BaseTopicDirective):
    """``lsst-task-topic`` directive that labels a Task's topic page."""

    directive_name = "lsst-task-topic"
    """Default name of this directive."""

    def get_type(self, class_name: str) -> str:
        from lsst.pipe.base import PipelineTask

        obj = get_type(class_name)
        if issubclass(obj, PipelineTask):
            return "PipelineTask"
        else:
            return "Task"

    def get_target_id(self, class_name: str) -> str:
        return format_task_id(class_name)


class ConfigTopicDirective(BaseTopicDirective):
    """``lsst-config-topic`` directive that labels a Config topic page.

    Configs are lsst.pex.config.config.Config subclasses.
    """

    directive_name = "lsst-config-topic"
    """Default name of this directive."""

    def get_object(self, class_name: str) -> str:
        return "Config"

    def get_target_id(self, class_name: str) -> str:
        return format_config_id(class_name)
