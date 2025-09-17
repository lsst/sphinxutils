"""Implements the ``package-docs`` CLI for single-package documentation builds
in the LSST Stack.
"""

__all__ = ("main",)

import logging
import os
import shutil
import sys

import click

from ..build import discover_package_doc_dir, run_sphinx

# Add -h as a help shortcut option
CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-d",
    "--dir",
    "root_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    default=".",
    help="Root Sphinx doc/ directory. You don't need to set this argument "
    "explicitly as long as the current working directory is any of:\n\n"
    "- the root of the package\n"
    "- the doc/ directory\n"
    "- a subdirectory of doc/\n",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (debug-level logging).",
)
@click.version_option()
@click.pass_context
def main(ctx: click.Context, root_dir: str, verbose: bool) -> None:
    """package-docs is a CLI for building single-package previews of
    documentation in the LSST Stack.

    Use package-docs during development to quickly preview your documentation
    and docstrings.

    .. warning::

       Using package-docs to compile standalone documentation for a single
       package will generate warnings related to missing references. This is
       normal because the full documentation set is not built in the mode.
       Before shipping revised documentation for a package, always make sure
       cross-package references work by doing a full-site build either locally
       with the stack-docs CLI or the site's Jenkins job.

    The key commands provided by package-docs are:

    - ``package-docs build``: compile the package's documentation.
    - ``package-docs clean``: removes documentation build products from a
      package.
    """
    # Subcommands should use the click.pass_context decorator to get this
    # ctx.obj object as the first argument.
    ctx.obj = {"root_dir": root_dir, "verbose": verbose}

    # Set up application logging. This ensures that only documenteer's
    # logger is activated. If necessary, we can add other app's loggers too.
    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logger = logging.getLogger("documenteer")
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(log_level)


@main.command()
@click.argument("topic", default=None, required=False, nargs=1)
@click.pass_context
def help(ctx: click.Context, topic: str | None, **kw: object) -> None:
    """Show help for any command."""
    # The help command implementation is taken from
    # https://www.burgundywall.com/post/having-click-help-subcommand
    if topic is None:
        if ctx.parent is not None:
            click.echo(ctx.parent.get_help())
        else:
            click.echo(main.get_help(ctx))
    else:
        click.echo(main.commands[topic].get_help(ctx))


@main.command()
@click.option("-W", "--warning-is-error", is_flag=True, help="Treat warnings as errors.")
@click.option("-n", "--nitpicky", is_flag=True, help="Activate Sphinx's nitpicky mode.")
@click.pass_context
def build(ctx: click.Context, warning_is_error: bool, nitpicky: bool) -> None:
    """Build documentation as HTML.

    The build HTML site is located in the ``doc/_build/html`` directory
    of the package.
    """
    root_dir = discover_package_doc_dir(ctx.obj["root_dir"])
    return_code = run_sphinx(root_dir, warnings_as_errors=warning_is_error, nitpicky=nitpicky)
    if return_code > 0:
        sys.exit(return_code)


@main.command()
@click.pass_context
def clean(ctx: click.Context) -> None:
    """Clean Sphinx build products.

    Use this command to clean out build products after a failed build, or
    in preparation for running a build from a clean state.

    This command removes the following directories from the package's doc/
    directory:

    - ``_build`` (the Sphinx build itself)
    - ``py-api`` (pages created by automodapi for the Python API reference)
    """
    logger = logging.getLogger(__name__)

    root_dir = discover_package_doc_dir(ctx.obj["root_dir"])

    dirnames = ["py-api", "_build"]
    dirnames = [os.path.join(root_dir, dirname) for dirname in dirnames]
    for dirname in dirnames:
        if os.path.isdir(dirname):
            shutil.rmtree(dirname)
            logger.debug("Cleaned up %r", dirname)
        else:
            logger.debug("Did not clean up %r (missing)", dirname)
