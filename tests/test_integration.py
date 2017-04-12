import os
import re

import py
import pytest
import pkg_resources

from sphinx.application import Sphinx


here = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope='session')
def sphinxdocs(tmpdir_factory):
    srcdir = os.path.join(here, '..', 'docs')
    outdir = tmpdir_factory.getbasetemp().strpath

    Sphinx(
        srcdir=srcdir,
        confdir=srcdir,
        outdir=outdir,
        doctreedir=os.path.join(outdir, '.doctrees'),
        buildername='html'
    ).build()

    yield py.path.local(srcdir), tmpdir_factory.getbasetemp()


def test_redocjs_lib_is_copied(sphinxdocs):
    srcdir, outdir = sphinxdocs
    extdir = py.path.local(
        pkg_resources.get_provider('sphinxcontrib.redoc').module_path)

    assert outdir.join('_static', 'redoc.js').check()
    assert outdir.join('_static', 'redoc.js').computehash() \
        == extdir.join('redoc.js').computehash()


def test_redocjs_page_is_generated(sphinxdocs):
    srcdir, outdir = sphinxdocs

    assert outdir.join('api', 'github', 'index.html').check()

    html = outdir.join('api', 'github', 'index.html').read()
    patterns = [
        r'<redoc spec-url="../../_specs/github.yml"\s+lazy-rendering\s+'
        r'expand-responses="">\s*</redoc>',
        r'<script src="../../_static/redoc.js">\s*</script>',
    ]

    for pattern in patterns:
        assert re.search(pattern, html)


def test_openapi_spec_is_copied(sphinxdocs):
    srcdir, outdir = sphinxdocs

    assert outdir.join('_specs', 'github.yml').check()
    assert outdir.join('_specs', 'github.yml').computehash() \
        == srcdir.join('_specs', 'github.yml').computehash()
