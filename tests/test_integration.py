import os
import textwrap
import json
import io

import yaml
import py
import pytest
import pkg_resources
import jinja2
import bs4

from sphinx.application import Sphinx


here = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope='function')
def run_sphinx(tmpdir):
    src = tmpdir.mkdir('src')
    out = tmpdir.mkdir('out')

    spec = py.path.local(here).join('..', 'docs', '_specs', 'github.yml')
    spec.copy(src.mkdir('_specs').join('github.yml'))

    def run(redoc_overwrite=None, redoc_uri=None):
        conf = {'name': 'Github API (v3)',
                'page': 'api/github/index',
                'spec': '_specs/github.yml'}
        conf.update(redoc_overwrite or {})

        confpy = jinja2.Template(textwrap.dedent('''
            import os

            project = 'sphinxcontrib-redoc'
            copyright = '2017, Ihor Kalnytskyi'

            extensions = ['sphinxcontrib.redoc']
            source_suffix = '.rst'
            master_doc = 'index'
            redoc = {{ redoc }}
            redoc_uri = {{ redoc_uri }}
        ''')).render(redoc=[conf], redoc_uri=repr(redoc_uri))

        src.join('conf.py').write_text(confpy, encoding='utf-8')
        src.join('index.rst').ensure()

        Sphinx(
            srcdir=src.strpath,
            confdir=src.strpath,
            outdir=out.strpath,
            doctreedir=out.join('.doctrees').strpath,
            buildername='html'
        ).build()

    yield run


def test_redocjs_lib_is_copied(run_sphinx, tmpdir):
    outdir = tmpdir.join('out')
    extdir = py.path.local(
        pkg_resources.get_provider('sphinxcontrib.redoc').module_path)

    run_sphinx()

    assert outdir.join('_static', 'redoc.js').check()
    assert outdir.join('_static', 'redoc.js').computehash() \
        == extdir.join('redoc.js').computehash()


def test_redocjs_lib_is_downloaded(run_sphinx, tmpdir):
    outdir = tmpdir.join('out')
    extdir = py.path.local(
        pkg_resources.get_provider('sphinxcontrib.redoc').module_path)

    run_sphinx(redoc_uri=(
        'https://cdn.jsdelivr.net/npm/redoc@2.0.0-alpha.32/bundles'
        '/redoc.standalone.js'))

    assert outdir.join('_static', 'redoc.js').check()
    assert outdir.join('_static', 'redoc.js').computehash() \
        != extdir.join('redoc.js').computehash()
    assert outdir.join('_static', 'redoc.js').computehash() \
        == '6978103258cab653263b5b75c008b474'


def test_openapi_spec_is_copied(run_sphinx, tmpdir):
    srcdir, outdir = tmpdir.join('src'), tmpdir.join('out')

    run_sphinx()

    assert outdir.join('_specs', 'github.yml').check()
    assert outdir.join('_specs', 'github.yml').computehash() \
        == srcdir.join('_specs', 'github.yml').computehash()


@pytest.mark.parametrize('options, attributes', [
    ({},
     {}),

    ({'lazy-rendering': False,
      'suppress-warnings': False,
      'hide-hostname': False,
      'required-props-first': False,
      'no-auto-auth': False,
      'path-in-middle-panel': False,
      'hide-loading': False,
      'native-scrollbars': False,
      'untrusted-spec': False,
      'expand-responses': []},
     {}),

    ({'lazy-rendering': True},
     {'lazy-rendering': ''}),

    ({'suppress-warnings': True},
     {'suppress-warnings': ''}),

    ({'hide-hostname': True},
     {'hide-hostname': ''}),

    ({'required-props-first': True},
     {'required-props-first': ''}),

    ({'no-auto-auth': True},
     {'no-auto-auth': ''}),

    ({'path-in-middle-panel': True},
     {'path-in-middle-panel': ''}),

    ({'hide-loading': True},
     {'hide-loading': ''}),

    ({'native-scrollbars': True},
     {'native-scrollbars': ''}),

    ({'untrusted-spec': True},
     {'untrusted-spec': ''}),

    ({'expand-responses': ['200', '404']},
     {'expand-responses': '200,404'}),

    ({'expand-responses': ['200']},
     {'expand-responses': '200'}),
])
def test_redocjs_page_is_generated(run_sphinx, tmpdir, options, attributes):
    run_sphinx(redoc_overwrite={'opts': options})

    html = tmpdir.join('out').join('api', 'github', 'index.html').read()
    soup = bs4.BeautifulSoup(html, 'html.parser')

    assert soup.title.string == 'Github API (v3)'
    attrs = soup.redoc.attrs
    attrs.pop('id')
    assert attrs == attributes
    assert soup.script.attrs['src'] == os.path.join(
        '..', '..', '_static', 'redoc.js')

    assert os.path.join('..', '..', '_specs', 'github.yml') \
        in soup.find_all('script')[-1].string


@pytest.mark.parametrize(['options', 'rendered'], [
    pytest.param(
        {'lazy-rendering': False,
         'suppress-warnings': False,
         'hide-hostname': False},
        'custom template:\n\n\n\n',
        id='no-options',
    ),
    pytest.param(
        {'lazy-rendering': True,
         'suppress-warnings': False,
         'hide-hostname': False},
        'custom template:\n\nlazy-rendering\n\n',
        id='lazy-rendering',
    ),
    pytest.param(
        {'lazy-rendering': False,
         'suppress-warnings': True,
         'hide-hostname': False},
        'custom template:\n\n\nsuppress-warnings\n',
        id='suppress-warnings',
    ),
    pytest.param(
        {'lazy-rendering': True,
         'suppress-warnings': True,
         'hide-hostname': True},
        'custom template:\n\nlazy-rendering\nsuppress-warnings\nhide-hostname',
        id='all-enabled',
    ),
])
@pytest.mark.parametrize(['get_template'], [
    pytest.param(
        lambda confdir: os.path.join('redoc', 'template.j2'),
        id='relative',
    ),
    pytest.param(
        lambda confdir: os.path.join(confdir, 'redoc', 'template.j2'),
        id='absolute',
    ),
])
def test_custom_template(run_sphinx, tmpdir, options, rendered, get_template):
    tmpdir.mkdir('src', 'redoc')
    tmpdir.join('src', 'redoc', 'template.j2').write_text(
        textwrap.dedent(u'''\
            custom template:

            {{ 'lazy-rendering' if opts['lazy-rendering'] }}
            {{ 'suppress-warnings' if opts['suppress-warnings'] }}
            {{ 'hide-hostname' if opts['hide-hostname'] }}
        '''),
        encoding='utf-8'
    )

    run_sphinx(
        redoc_overwrite={
            'template': get_template(tmpdir.join('src').strpath),
            'opts': options,
        }
    )

    text = tmpdir.join('out').join('api', 'github', 'index.html').read()
    assert text == rendered


def test_embedded_spec(run_sphinx, tmpdir):
    run_sphinx(redoc_overwrite={'embed': True})

    html = tmpdir.join('out').join('api', 'github', 'index.html').read()
    spec = tmpdir.join('src', '_specs', 'github.yml').strpath
    soup = bs4.BeautifulSoup(html, 'html.parser')

    with io.open(spec, encoding='utf-8') as f:
        spec = yaml.safe_load(f)

    embedded_spec = soup.find(id='spec').string
    assert json.loads(embedded_spec) == spec


@pytest.mark.parametrize(['conf', 'error'], [
    pytest.param(
        {'spec': 42},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.spec: 42 is not of type 'string'"
        ),
        id='spec-int'),

    pytest.param(
        {'page': 42},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.page: 42 is not of type 'string'"
        ),
        id='page-int'),

    pytest.param(
        {'opts': {'lazy-rendering': 1}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.lazy-rendering: 1 is not of type 'boolean'"
        ),
        id='lazy-rendering-int'),

    pytest.param(
        {'opts': {'lazy-rendering': 'True'}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.lazy-rendering: 'True' is not of type 'boolean'"
        ),
        id='lazy-rendering-str'),

    pytest.param(
        {'opts': {'suppress-warnings': 1}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.suppress-warnings: 1 is not of type 'boolean'"
        ),
        id='suppress-warnings-int'),

    pytest.param(
        {'opts': {'suppress-warnings': 'True'}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.suppress-warnings: 'True' is not of type 'boolean'"
        ),
        id='suppress-warnings-str'),

    pytest.param(
        {'opts': {'hide-hostname': 1}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.hide-hostname: 1 is not of type 'boolean'"
        ),
        id='hide-hostname-int'),

    pytest.param(
        {'opts': {'hide-hostname': 'True'}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.hide-hostname: 'True' is not of type 'boolean'"
        ),
        id='hide-hostname-str'),

    pytest.param(
        {'opts': {'required-props-first': 1}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.required-props-first: 1 is not of type 'boolean'"
        ),
        id='required-props-first-int'),

    pytest.param(
        {'opts': {'required-props-first': 'True'}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.required-props-first: 'True' is not of type 'boolean'"
        ),
        id='required-props-first-str'),

    pytest.param(
        {'opts': {'no-auto-auth': 1}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.no-auto-auth: 1 is not of type 'boolean'"
        ),
        id='no-auto-auth-int'),

    pytest.param(
        {'opts': {'no-auto-auth': 'True'}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.no-auto-auth: 'True' is not of type 'boolean'"
        ),
        id='no-auto-auth-str'),

    pytest.param(
        {'opts': {'path-in-middle-panel': 1}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.path-in-middle-panel: 1 is not of type 'boolean'"
        ),
        id='path-in-middle-panel-int'),

    pytest.param(
        {'opts': {'path-in-middle-panel': 'True'}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.path-in-middle-panel: 'True' is not of type 'boolean'"
        ),
        id='path-in-middle-panel-str'),

    pytest.param(
        {'opts': {'hide-loading': 1}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.hide-loading: 1 is not of type 'boolean'"
        ),
        id='hide-loading-int'),

    pytest.param(
        {'opts': {'hide-loading': 'True'}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.hide-loading: 'True' is not of type 'boolean'"
        ),
        id='hide-loading-str'),

    pytest.param(
        {'opts': {'native-scrollbars': 1}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.native-scrollbars: 1 is not of type 'boolean'"
        ),
        id='native-scrollbars-int'),

    pytest.param(
        {'opts': {'native-scrollbars': 'True'}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.native-scrollbars: 'True' is not of type 'boolean'"
        ),
        id='native-scrollbars-str'),

    pytest.param(
        {'opts': {'untrusted-spec': 1}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.untrusted-spec: 1 is not of type 'boolean'"
        ),
        id='untrusted-spec-int'),

    pytest.param(
        {'opts': {'untrusted-spec': 'True'}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.untrusted-spec: 'True' is not of type 'boolean'"
        ),
        id='untrusted-spec-str'),

    pytest.param(
        {'opts': {'expand-responses': [200, 404]}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.expand-responses.0: 200 is not of type 'string'"
        ),
        id='expand-responses-int-array'),

    pytest.param(
        {'opts': {'expand-responses': '200'}},
        (
            "Improper configuration for sphinxcontrib-redoc at "
            "0.opts.expand-responses: '200' is not of type 'array'"
        ),
        id='expand-responses-str'),
])
def test_conf_validation(run_sphinx, tmpdir, conf, error):
    with pytest.raises(Exception) as excinfo:
        run_sphinx(redoc_overwrite=conf)
    assert error == str(excinfo.value)
