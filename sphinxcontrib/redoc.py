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
import json

import jinja2
import jsonschema
import pkg_resources
import yaml

from six.moves import urllib
from sphinx.util.fileutil import copy_asset
from sphinx.util.osutil import copyfile, ensuredir


_HERE = os.path.abspath(os.path.dirname(__file__))
_REDOC_CONF_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
            'page': {'type': 'string'},
            'spec': {'type': 'string'},
            'embed': {'type': 'boolean'},
            'template': {'type': 'string'},
            'opts': {
                'type': 'object',
                'properties': {
                    'lazy-rendering': {'type': 'boolean'},
                    'suppress-warnings': {'type': 'boolean'},
                    'hide-hostname': {'type': 'boolean'},
                    'required-props-first': {'type': 'boolean'},
                    'no-auto-auth': {'type': 'boolean'},
                    'path-in-middle-panel': {'type': 'boolean'},
                    'hide-loading': {'type': 'boolean'},
                    'native-scrollbars': {'type': 'boolean'},
                    'untrusted-spec': {'type': 'boolean'},
                    'expand-responses': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    }
                },
                'additionalProperties': False,
            },
        },
        'required': ['page', 'spec'],
        'additionalProperties': False,
    },
}


def render(app):
    try:
        # Settings set in Sphinx's conf.py may contain improper configuration
        # or typos. In order to prevent misbehaviour or failures deep down the
        # code, we want to ensure that all required settings are passed and
        # optional settings has proper type and/or value.
        jsonschema.validate(app.config.redoc, schema=_REDOC_CONF_SCHEMA)
    except jsonschema.ValidationError as exc:
        raise ValueError(
            'Improper configuration for sphinxcontrib-redoc at %s: %s' % (
                '.'.join((str(part) for part in exc.path)),
                exc.message,
            )
        )

    for ctx in app.config.redoc:
        if 'template' in ctx:
            template_path = os.path.join(app.confdir, ctx['template'])
        else:
            template_path = os.path.join(_HERE, 'redoc.j2')

        with io.open(template_path, encoding='utf-8') as f:
            template = jinja2.Template(f.read())

        # In embed mode, we are going to embed the whole OpenAPI spec into
        # produced HTML. The rationale is very simple: we want to produce
        # browsable HTMLs ready to be used without any web server.
        if ctx.get('embed') is True:
            # Parse & dump the spec to have it as properly formatted json
            specfile = os.path.join(app.confdir, ctx['spec'])
            with io.open(specfile, encoding='utf-8') as specfp:
                try:
                    spec_contents = yaml.safe_load(specfp)
                except ValueError as ver:
                    raise ValueError('Cannot parse spec %r: %s'
                                     % (ctx['spec'], ver))

                ctx['spec'] = json.dumps(spec_contents)

        # The 'spec' may contain either HTTP(s) link or filesystem path. In
        # case of later we need to copy the spec into output directory, as
        # otherwise it won't be available when the result is deployed.
        elif not ctx['spec'].startswith(('http', 'https')):

            specpath = os.path.join(app.builder.outdir, '_specs')
            specname = os.path.basename(ctx['spec'])

            ensuredir(specpath)

            copyfile(
                # Since the path may be relative it should be joined with
                # base URI which is a path of directory with conf.py in
                # our case.
                os.path.join(app.confdir, ctx['spec']),
                os.path.join(specpath, specname))

            # The link inside the rendered document must refer to a new
            # location, the place where it has been copied to.
            ctx['spec'] = os.path.join('_specs', specname)

        # Propagate information about page rendering to Sphinx. There's
        # a little trick in here: we pass an actual Jinja2 template instance
        # instead of template name. This is passible due to Jinja2 API where
        # we can pass a template instance to Jinja2 environment and so on.
        # Such little trick allows us to avoid other hacks which require
        # manipulating of Sphinx's 'templates_path' option.
        ctx.setdefault('opts', {})
        yield ctx['page'], ctx, template


def assets(app, exception):
    # Since '_static' directory may not exist in case of failed build, we
    # need to either ensure its existence here or do not try to copy  assets
    # in case of failure.
    if not exception:
        copy_asset(
            os.path.join(_HERE, 'redoc.js'),
            os.path.join(app.builder.outdir, '_static'))

        # It's hard to keep up with ReDoc releases, especially when you don't
        # watch them closely. Hence, there should be a way to override built-in
        # ReDoc bundle with some upstream one.
        if app.config.redoc_uri:
            urllib.request.urlretrieve(
                app.config.redoc_uri,
                os.path.join(app.builder.outdir, '_static', 'redoc.js'))


def setup(app):
    app.add_config_value('redoc', [], 'html')
    app.add_config_value('redoc_uri', None, 'html')

    app.connect('html-collect-pages', render)
    app.connect('build-finished', assets)

    version = pkg_resources.get_distribution('sphinxcontrib-redoc').version
    return {'version': version, 'parallel_read_safe': True}
