.. _redoc_directive_doc:

ReDoc Directive
===============

.. versionadded:: 1.7.0

API
---

.. rst:directive:: redoc

   .. rst:directive:option:: name: <name>

      An API (human readable) name that will be used as page title.

   .. rst:directive:option:: spec: <spec_path>
    
      A path to the OpenAPI spec file. The path is relative to the
      document where the directive is used.

   .. rst:directive:option:: embed
      
      *Disabled by default*

      If set, the ``spec`` will be embedded into the rendered HTML page.
      Useful for cases when a browsable API ready to be used without any web
      server is needed.
      The ``spec`` must be an ``UTF-8`` encoded JSON on YAML OpenAPI spec;
      embedding an external ``spec`` is currently not supported.

  .. rst:directive:option:: template: <template_path>

    Path to non-default template to use to render ReDoc HTML page. Must be either
    passed, or omitted. You can also write template in directive body. 

    .. warning::

        When custom template is used, settings such as ``name``, ``embed`` or
        ``opts`` may not work if they are not supported by the template. Use
        custom templates with caution.

  .. rst:directive:option:: opt.lazy-rendering

    *Disabled by default*

    If set, enables lazy rendering mode which is useful for APIs with big
    number of operations (e.g. > 50). In this mode ReDoc shows initial
    screen ASAP and then renders the rest operations asynchronously while
    showing progress bar on the top.

  .. rst:directive:option:: opt.suppress-warnings

    *Disabled by default*

    If set, no warnings are rendered at the top of the document.

  .. rst:directive:option:: opt.hide-hostname

    *Disabled by default*

    If set, both protocol ans hostname are not shown in the operational
    definition.

  .. rst:directive:option:: opt.required-props-firs

    *Disabled by default*

    If set, ReDoc shows required properties first in the same order as in
    ``required`` array. Please note, it may be slow.

  .. rst:directive:option:: opt.expand-responses

    *Empty by default*

    A list of response codes to be expanded by default, separated by comma ``,``.

    Example: ``:opt.expand-responses: 200, 201, 204``

  .. rst:directive:option:: opt.hide-loading

    *Disabled by default*

    Do not show loading animation. Useful for small OpenAPI specs.

  .. rst:directive:option:: opt.native-scrollbars

    *Disabled by default*

    Use native scrollbar for sidemenu instead of perfect-scroll. May
    dramatically improve performance on big OpenAPI specs.

  .. rst:directive:option:: opt.untrusted-spec

    *Disabled by default*

    If set, the spec is considered untrusted and all HTML/markdown is
    sanitized to prevent XSS.



Example
-------

.. code:: rst

    .. redoc::
       :name: GitHub API
       :spec: _specs/github.yml
       :opt.lazy-rendering: true

.. redoc::
   :name: GitHub API
   :spec: _specs/github.yml
   :opt.lazy-rendering:
   :opt.hide-hostname:
