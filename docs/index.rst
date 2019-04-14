sphinxcontrib-redoc
===================

.. hint::

    Check out `sphinxcontrib-openapi`_ if you are interested in rendering
    OpenAPI spec within Sphinx page (i.e. inline).

.. image:: _static/logo.png
   :width: 200
   :align: right

The Sphinx_ extension that renders OpenAPI_ (fka Swagger) specs with love
(❤️) using amazing ReDoc_. Don't believe it? Here's `the proof`_. Now stop
frustrating and start moving your projects to OpenAPI and ReDoc with this
small first step:

.. code:: bash

    $ pip install sphinxcontrib-redoc


Usage
-----

The whole configuration is done via Sphinx's ``conf.py``. All you have to
do is to:

* enable this extension

  .. code:: python

      extensions = [
         # ...
         'sphinxcontrib.redoc',
      ]

* define OpenAPI specs to render

  .. code:: python

      redoc = [
          {
              'name': 'Batcomputer API',
              'page': 'api',
              'spec': 'specs/batcomputer.yml',
              'embed': True,
          },
          {
              'name': 'Example API',
              'page': 'example/index',
              'spec': 'http://example.com/openapi.yml',
              'opts': {
                  'lazy': False,
                  'nowarnings': False,
                  'nohostname': False,
                  'required-props-first': True,
                  'expand-responses': ["200", "201"],
              }
          },
      ]

  where

  ``name``
    An API (human readable) name that will be used as page title.

  ``page``
    A page name to be used to form an output file. Passing ``api`` means:
    save rendered page as ``{outdir}/api.html``. It also support complex
    paths such as ``foo/bar/api`` which will be resolved into something
    like ``{outdir}/foo/bar/api.html``.

  ``spec``
    A path to an OpenAPI spec to be rendered. Can be either an HTTP(s)
    link to external source, or filesystem path relative to conf directory.

  ``embed`` (default: ``False``)
    If ``True``, the ``spec`` will be embedded into the rendered HTML page.
    Useful for cases when a browsable API ready to be used without any web
    server is needed.
    The ``spec`` must be an ``UTF-8`` encoded JSON on YAML OpenAPI spec;
    embedding an external ``spec`` is currently not supported.

  ``template``
    Non default template to use to render ReDoc HTML page. Must be either
    passed, or omitted.

    .. warning::

       When custom template is used, settings such as ``name``, ``embed`` or
       ``opts`` may not work if they are not supported by the template. Use
       custom templates with caution.

  ``opts``
    An optional dictionary with some of ReDoc settings that might be
    useful. Here they are

    ``lazy-rendering`` (default: ``False``)
      If set, enables lazy rendering mode which is useful for APIs with big
      number of operations (e.g. > 50). In this mode ReDoc shows initial
      screen ASAP and then renders the rest operations asynchronously while
      showing progress bar on the top.

    ``suppress-warnings`` (default: ``False``)
      If set, no warnings are rendered at the top of the document.

    ``hide-hostname`` (default: ``False``)
      If set, both protocol ans hostname are not shown in the operational
      definition.

    ``required-props-first`` (default: ``False``)
      If set, ReDoc shows required properties first in the same order as in
      ``required`` array. Please note, it may be slow.

    ``expand-responses`` (default: ``[]``)
      A list of response codes to be expanded by default.

    ``hide-loading`` (default: ``False``)
      Do not show loading animation. Useful for small OpenAPI specs.

    ``native-scrollbars`` (default: ``False``)
      Use native scrollbar for sidemenu instead of perfect-scroll. May
      dramatically improve performance on big OpenAPI specs.

    ``untrusted-spec`` (default: ``False``)
      If set, the spec is considered untrusted and all HTML/markdown is
      sanitized to prevent XSS.

* if you are not ok with default version, specify the one you want to use

  .. code:: python

      redoc_uri = 'https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js'

Demo
----

* GitHub API

  * `the page <api/github/>`__
  * `the spec <_specs/github.yml>`__


Known Issues
------------

* ReDoc has some performance issues, so loading a pretty huge OpenAPI spec
  may take a time.


Changes
-------

.. include:: ../CHANGES.rst


Links
-----

* Documentation: https://sphinxcontrib-redoc.readthedocs.io/
* Source: https://github.com/ikalnytskyi/sphinxcontrib-redoc
* Bugs: https://github.com/ikalnytskyi/sphinxcontrib-redoc/issues


.. _Sphinx: https://www.sphinx-doc.org/
.. _OpenAPI: https://openapis.org/
.. _ReDoc: https://github.com/Rebilly/ReDoc
.. _the proof: api/github/
.. _sphinxcontrib-openapi: https://sphinxcontrib-openapi.readthedocs.io/
