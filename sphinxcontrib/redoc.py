"""
    sphinxcontrib.redoc
    ~~~~~~~~~~~~~~~~~~~

    ReDoc powered OpenAPI spec renderer for Sphinx.
    Enjoy beautiful API docs! ;)

    :copyright: (c) 2017 by Ihor Kalnytskyi.
    :license: BSD, see LICENSE for details.
"""

import io
import os

import jinja2
import pkg_resources

from sphinx.util.osutil import copyfile, ensuredir


here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'redoc.j2'), 'r', encoding='utf-8') as f:
    template = jinja2.Template(f.read())


def render(app):
    for ctx in app.config.redoc:
        # Setup options if they are not passed since 'redoc.j2' template
        # relies on them.
        ctx.setdefault('opts', {})

        # The 'spec' may contain either HTTP(s) link or filesystem path. In
        # case of later we need to copy the spec into output directory, as
        # otherwise it won't be available when the result is deployed.
        if not ctx['spec'].startswith(('http', 'https')):
            specpath = os.path.join(app.builder.outdir, '_specs')
            specname = os.path.basename(ctx['spec'])

            ensuredir(specpath)

            copyfile(
                # Since the path may be relative it should be joined with
                # base URI which is a path of directory with conf.py in
                # our case.
                os.path.join(app.confdir, ctx['spec']),
                os.path.join(specpath, specname))

            # The link inside rendered document must refer to a new location,
            # the place where it has being copied to.
            ctx['spec'] = os.path.join('_specs', specname)

        # Propagate information about page rendering to Sphinx. There's
        # a little trick in here: we pass an actual Jinja2 template instance
        # instead of template name. This is passible due to Jinja2 API where
        # we can pass a template instance to Jinja2 environment and so on.
        # Such little trick allows us to avoid other hacks which require
        # manipulating of Sphinx's 'templates_path' option.
        yield ctx['page'], ctx, template


def assets(app, exception):
    # Since '_static' directory may not exist in case of failed build, we
    # need to either ensure its existence here or do not try to copy  assets
    # in case of failure.
    if not exception:
        copyfile(
            os.path.join(here, 'redoc.js'),
            os.path.join(app.builder.outdir, '_static', 'redoc.js'))


def setup(app):
    app.add_config_value('redoc', [], 'html')
    app.connect('html-collect-pages', render)
    app.connect('build-finished', assets)

    version = pkg_resources.get_distribution('sphinxcontrib-redoc').version
    return {'version': version, 'parallel_read_safe': True}
