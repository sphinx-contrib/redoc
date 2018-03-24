import os
import textwrap

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

    def run(conf):
        confpy = jinja2.Template(textwrap.dedent('''
            import os

            project = 'sphinxcontrib-redoc'
            copyright = '2017, Ihor Kalnytskyi'

            extensions = ['sphinxcontrib.redoc']
            source_suffix = '.rst'
            master_doc = 'index'
            redoc = [
                {
                    'name': 'Github API (v3)',
                    'page': 'api/github/index',
                    'spec': '_specs/github.yml',
                    {% if opts is not none %}
                    'opts': {
                        {% for key, value in opts.items() %}
                        '{{ key }}': {{ value }},
                        {% endfor %}
                    },
                    {% endif %}
                },
            ]
        ''')).render(opts=conf)
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

    run_sphinx({})

    assert outdir.join('_static', 'redoc.js').check()
    assert outdir.join('_static', 'redoc.js').computehash() \
        == extdir.join('redoc.js').computehash()


def test_openapi_spec_is_copied(run_sphinx, tmpdir):
    srcdir, outdir = tmpdir.join('src'), tmpdir.join('out')

    run_sphinx({})

    assert outdir.join('_specs', 'github.yml').check()
    assert outdir.join('_specs', 'github.yml').computehash() \
        == srcdir.join('_specs', 'github.yml').computehash()


@pytest.mark.parametrize('options, attributes', [
    (None,
     {'spec-url': os.path.join('..', '..', '_specs', 'github.yml')}),

    ({},
     {'spec-url': os.path.join('..', '..', '_specs', 'github.yml')}),

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
     {'spec-url': os.path.join('..', '..', '_specs', 'github.yml')}),

    ({'lazy-rendering': True},
     {'spec-url': os.path.join('..', '..', '_specs', 'github.yml'),
      'lazy-rendering': ''}),

    ({'suppress-warnings': True},
     {'spec-url': os.path.join('..', '..', '_specs', 'github.yml'),
      'suppress-warnings': ''}),

    ({'hide-hostname': True},
     {'spec-url': os.path.join('..', '..', '_specs', 'github.yml'),
      'hide-hostname': ''}),

    ({'required-props-first': True},
     {'spec-url': os.path.join('..', '..', '_specs', 'github.yml'),
      'required-props-first': ''}),

    ({'no-auto-auth': True},
     {'spec-url': os.path.join('..', '..', '_specs', 'github.yml'),
      'no-auto-auth': ''}),

    ({'path-in-middle-panel': True},
     {'spec-url': os.path.join('..', '..', '_specs', 'github.yml'),
      'path-in-middle-panel': ''}),

    ({'hide-loading': True},
     {'spec-url': os.path.join('..', '..', '_specs', 'github.yml'),
      'hide-loading': ''}),

    ({'native-scrollbars': True},
     {'spec-url': os.path.join('..', '..', '_specs', 'github.yml'),
      'native-scrollbars': ''}),

    ({'untrusted-spec': True},
     {'spec-url': os.path.join('..', '..', '_specs', 'github.yml'),
      'untrusted-spec': ''}),

    ({'expand-responses': ['200', '404']},
     {'spec-url': os.path.join('..', '..', '_specs', 'github.yml'),
      'expand-responses': '200,404'}),
])
def test_redocjs_page_is_generated(run_sphinx, tmpdir, options, attributes):
    run_sphinx(options)

    html = tmpdir.join('out').join('api', 'github', 'index.html').read()
    soup = bs4.BeautifulSoup(html, 'html.parser')

    assert soup.title.string == 'Github API (v3)'
    assert soup.redoc.attrs == attributes
    assert soup.script.attrs['src'] == os.path.join(
        '..', '..', '_static', 'redoc.js')
