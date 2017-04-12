import os
import pkg_resources


project = 'sphinxcontrib-redoc'
copyright = '2017, Ihor Kalnytskyi'
release = pkg_resources.get_distribution('sphinxcontrib-redoc').version
version = '.'.join(release.split('.')[:2])

extensions = ['sphinx.ext.extlinks', 'sphinxcontrib.redoc']
source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = ['_build']
pygments_style = 'sphinx'
extlinks = {
    'issue': ('https://github.com/ikalnytskyi/sphinxcontrib-redoc/issues/%s', '#'),
    'pr': ('https://github.com/ikalnytskyi/sphinxcontrib-redoc/pull/%s', 'PR #'),
}
redoc = [
    {
        'name': 'Github API (v3)',
        'page': 'api/github/index',
        'spec': '_specs/github.yml',
        'opts': {
            'lazy-rendering': True
        },
    },
]

if not os.environ.get('READTHEDOCS') == 'True':
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Unfortunately, Sphinx doesn't support code highlighting for standard
# reStructuredText `code` directive. So let's register 'code' directive
# as alias for Sphinx's own implementation.
#
# https://github.com/sphinx-doc/sphinx/issues/2155
from docutils.parsers.rst import directives
from sphinx.directives.code import CodeBlock
directives.register_directive('code', CodeBlock)

# flake8: noqa
