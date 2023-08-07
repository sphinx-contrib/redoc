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
import posixpath

import jinja2
import jsonschema
import pkg_resources
import yaml


from docutils import nodes
from sphinx.util.docutils import SphinxDirective
from docutils.parsers.rst import directives
from six.moves import urllib
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util.fileutil import copy_asset
from sphinx.util.osutil import copyfile, ensuredir, relative_uri


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


def render(app, context=None):
    app_content = False
    if context is None:
        context = app.config.redoc
        app_content = True
    if app_content:
        try:
            # Settings set in Sphinx's conf.py may contain improper
            # configuration or typos. In order to prevent misbehaviour or
            # failures deep down the code, we want to ensure that all required
            # settings are passed and optional settings has proper type and/or
            # value.
            jsonschema.validate(context, schema=_REDOC_CONF_SCHEMA)
        except jsonschema.ValidationError as exc:
            raise ValueError(
                'Improper configuration for sphinxcontrib-redoc at %s: %s' % (
                    '.'.join((str(part) for part in exc.path)),
                    exc.message,
                )
            )

    for ctx in context:
        template = None
        template_path = os.path.join(_HERE, 'redoc.j2')
        if 'template' in ctx:
            if isinstance(ctx['template'], jinja2.Template):
                template = ctx['template']
            else:
                template_path = os.path.join(app.confdir, ctx['template'])

        if template is None:
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
                os.path.join(specpath, specname)
            )

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
            os.path.join(app.builder.outdir, '_static'),
        )

        # It's hard to keep up with ReDoc releases, especially when you don't
        # watch them closely. Hence, there should be a way to override built-in
        # ReDoc bundle with some upstream one.
        if app.config.redoc_uri:
            urllib.request.urlretrieve(
                app.config.redoc_uri,
                os.path.join(app.builder.outdir, '_static', 'redoc.js'))


def boolean_directive(argument):
    return argument.strip().lower() in ('true', 'yes', 'on', 'y', '1')


class HTMLBuilder(StandaloneHTMLBuilder):
    # clone of StandaloneHTMLBuilder.handle_page with a few changes
    def render_page(
        self,
        pagename: str,
        addctx: dict,
        templatename: str = 'page.html',
    ) -> str:
        ctx = self.globalcontext.copy()
        # current_page_name is backwards compatibility
        ctx['pagename'] = ctx['current_page_name'] = pagename
        ctx['encoding'] = self.config.html_output_encoding
        default_baseuri = self.get_target_uri(pagename)
        # in the singlehtml builder, default_baseuri still contains an #anchor
        # part, which relative_uri doesn't really like...
        default_baseuri = default_baseuri.rsplit('#', 1)[0]

        if self.config.html_baseurl:
            ctx['pageurl'] = posixpath.join(self.config.html_baseurl,
                                            pagename + self.out_suffix)
        else:
            ctx['pageurl'] = None

        def pathto(
            otheruri: str,
            resource: bool = False,
            baseuri: str = default_baseuri,
        ) -> str:
            if resource and '://' in otheruri:
                # allow non-local resources given by scheme
                return otheruri
            elif not resource:
                otheruri = self.get_target_uri(otheruri)
            uri = relative_uri(baseuri, otheruri) or '#'
            if uri == '#' and not self.allow_sharp_as_current_path:
                uri = baseuri
            return uri
        ctx['pathto'] = pathto

        def hasdoc(name: str) -> bool:
            if name in self.env.all_docs:
                return True
            if name == 'search' and self.search:
                return True
            if name == 'genindex' and self.get_builder_config(
                'use_index',
                'html',
            ):
                return True
            return False
        ctx['hasdoc'] = hasdoc

        ctx['toctree'] = lambda **kwargs: self._get_local_toctree(
            pagename,
            **kwargs,
        )
        self.add_sidebars(pagename, ctx)
        ctx.update(addctx)

        # revert script_files and css_files
        self.script_files[:] = self._script_files
        self.css_files[:] = self._css_files

        self.update_page_context(pagename, templatename, ctx, None)

        # sort JS/CSS before rendering HTML
        try:
            # Convert script_files to list to support non-list script_files
            # (refs: #8889)
            ctx['script_files'] = sorted(
                ctx['script_files'],
                key=lambda js: js.priority
            )
        except AttributeError:
            # Skip sorting if users modifies script_files directly
            # (maybe via `html_context`).
            # refs: #8885
            #
            # Note: priority sorting feature will not work in this case.
            pass

        try:
            ctx['css_files'] = sorted(
                ctx['css_files'],
                key=lambda css: css.priority
            )
        except AttributeError:
            pass

        return self.templates.render(templatename, ctx)


class RedocDirective(SphinxDirective):
    _app = None

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'name': directives.unchanged_required,
        'spec': directives.unchanged,
        'embed': directives.flag,
        'template': directives.path,
        # options
        'opt.lazy-rendering': directives.flag,
        'opt.suppress-warnings': directives.flag,
        'opt.hide-hostname': directives.flag,
        'opt.required-props-first': directives.flag,
        'opt.no-auto-auth': directives.flag,
        'opt.path-in-middle-panel': directives.flag,
        'opt.hide-loading': directives.flag,
        'opt.native-scrollbars': directives.flag,
        'opt.untrusted-spec': directives.flag,
    }

    has_content = True

    @property
    def builder(self):
        return self._app.builder

    def run(self):
        # this is the HTML you would put in your .rst file
        # redoc container
        page = self.get_source_info()[0]
        relative_path = os.path.relpath(
            page, self._app.confdir
        ).rsplit('.', 1)[0]
        context = {
            "page": relative_path,
            "template": os.path.join(_HERE, 'redoc_content.j2')
        }

        for k, v in self.options.items():
            if k.startswith('opt.'):
                context.setdefault('opts', {})[k[4:]] = v
            else:
                context[k] = v

        if self.content:
            context['template'] = jinja2.Template('\n'.join(self.content))

        builder = HTMLBuilder(self._app, self.env)
        builder.init()
        builder.prepare_writing([])
        # using ReDoc to generate the HTML
        for i in render(self._app, [context]):
            html = builder.render_page(i[0], i[1], i[2])
            break

        return [nodes.raw('', html, format='html')]


def setup(app):
    app.add_config_value('redoc', [], 'html')
    app.add_config_value('redoc_uri', None, 'html')

    app.connect('html-collect-pages', render)
    app.connect('build-finished', assets)

    RedocDirective._app = app
    app.add_directive('redoc', RedocDirective)

    version = pkg_resources.get_distribution('sphinxcontrib-redoc').version
    return {'version': version, 'parallel_read_safe': True}
