"""A basic test that establishes CI works.

This is a placeholder for adding real tests for the package later.
"""

from __future__ import annotations

import unittest

from lsst.sphinxutils.version import __version__


class NullTestCase(unittest.TestCase):
    """A basic test that establishes CI works."""

    def test_null(self) -> None:
        self.assertIsNotNone(__version__)
