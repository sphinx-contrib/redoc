sphinxcontrib-redoc
===================

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
          },
          {
              'name': 'Example API',
              'page': 'example/index',
              'spec': 'http://example.com/openapi.yml',
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

* Documentation: https://sphinxcontrib-redoc.readthedocs.org/
* Source: https://github.com/ikalnytskyi/sphinxcontrib-redoc
* Bugs: https://github.com/ikalnytskyi/sphinxcontrib-redoc/issues


.. _Sphinx: https://www.sphinx-doc.org/
.. _OpenAPI: https://openapis.org/
.. _ReDoc: https://github.com/Rebilly/ReDoc
.. _the proof: api/github/
