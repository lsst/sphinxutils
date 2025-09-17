"""Tests for lsst.sphinxutils.ext.packagetoctree (package-toctree and
module-toctree directives).
"""

from __future__ import annotations

from typing import IO
from unittest import TestCase

import pytest
from bs4 import BeautifulSoup, Tag
from sphinx.application import Sphinx
from sphinx.util import logging

from lsst.sphinxutils.ext.packagetoctree import _filter_index_pages


@pytest.mark.sphinx("html", testroot="packagetoctree")
def test_packagetoctree(app: Sphinx, status: IO[str], warning: IO[str]) -> None:
    """Test the packagetoctree extension on a test site."""
    app.verbosity = 2
    logging.setup(app, status, warning)
    app.builder.build_all()

    index_html = (app.outdir / "index.html").read_text()
    index_soup = BeautifulSoup(index_html, "html.parser")
    print(f"index.html: {app.outdir / 'index.html'}")

    # Check the module toctree
    wrapper = index_soup.find("div", class_="module-toctree")
    if isinstance(wrapper, Tag):
        wrapper_entries = [
            (item.text, item.a.get("href"))
            for item in wrapper.find_all("li")
            if isinstance(item, Tag) and item.a is not None
        ]
    else:
        wrapper_entries = []
    # Note that `lsst.skipthis` is *not* present
    assert wrapper_entries == [
        ("lsst.packageA", "modules/lsst.packageA/index.html"),
        ("lsst.packageB", "modules/lsst.packageB/index.html"),
    ]

    # Check the EUPS package toctree
    wrapper = index_soup.find("div", class_="package-toctree")
    if isinstance(wrapper, Tag):
        wrapper_entries = [
            (item.text, item.a.get("href"))
            for item in wrapper.find_all("li")
            if isinstance(item, Tag) and item.a is not None
        ]
    else:
        wrapper_entries = []
    # Note that `skipthis` is *not* present
    assert wrapper_entries == [
        ("A", "packages/A/index.html"),
        ("B", "packages/B/index.html"),
    ]


class TestFilterIndexPages(TestCase):
    """Test _filter_index_pages."""

    def test_filter_index_pages(self) -> None:
        """Test _filter_index_pages."""
        docnames = [
            "index",
            "basedir/A/index",
            "basedir/B/index",
            "basedir/B/subdir/indexotherdir/C/index",
        ]
        expected = [
            "basedir/A/index",
            "basedir/B/index",
        ]
        assert set(expected) == set(_filter_index_pages(docnames, "basedir"))
