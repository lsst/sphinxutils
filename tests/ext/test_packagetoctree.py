"""Tests for lsst.sphinxutils.ext.packagetoctree (package-toctree and
module-toctree directives).
"""

from unittest import TestCase

from lsst.sphinxutils.ext.packagetoctree import _filter_index_pages


class TestFilterIndexPages(TestCase):
    """Test _filter_index_pages."""

    def test_filter_index_pages(self) -> None:
        """Test _filter_index_pages."""
        docnames = [
            "index",
            "basedir/A/index",
            "basedir/B/index",
            "basedir/B/subdir/index" "otherdir/C/index",
        ]
        expected = [
            "basedir/A/index",
            "basedir/B/index",
        ]
        assert set(expected) == set(list(_filter_index_pages(docnames, "basedir")))
