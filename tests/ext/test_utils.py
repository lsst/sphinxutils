"""Tests for lsst.sphinxutils.ext.utils (utilities for Sphinx extensions)."""

from __future__ import annotations

import unittest

from lsst.sphinxutils.ext.utils import RoleContent


class RoleContentTestCase(unittest.TestCase):
    """Tests for the RoleContent class."""

    def test_custom_display(self) -> None:
        """Test a custom display content."""
        content = RoleContent.parse("Tables <lsst.afw.table.Table>")
        self.assertEqual(
            content, RoleContent(last_component=False, display="Tables", ref="lsst.afw.table.Table")
        )

    def test_last_component(self) -> None:
        """Test the last component flag."""
        content = RoleContent.parse("~lsst.afw.table.Table")
        self.assertEqual(content, RoleContent(last_component=True, display=None, ref="lsst.afw.table.Table"))

    def test_no_display(self) -> None:
        """Test a role with no custom display."""
        content = RoleContent.parse("lsst.afw.table.Table")
        self.assertEqual(content, RoleContent(last_component=False, display=None, ref="lsst.afw.table.Table"))
