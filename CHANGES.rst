1.6.0 (2020-04-17)
``````````````````

- Add support for custom ReDoc templates. [:pr:`27`]
- Drop Python 3.4 support. [:pr:`34`]
- Fix issue when the extension may trigger build failure when other
  than html builders are used (e.g. linkcheck). [:pr:`32`]

1.5.1 (2018-08-05)
``````````````````

- Fix critical issue when relative path to an OpenAPI spec didn't work.

  [:issue:`17`]

1.5.0 (2018-07-28)
``````````````````

- New ``embed`` option. When ``True``, the spec will be embedded into the
  rendered HTML page. Thanks `@etene <https://github.com/etene>`_.

  [:pr:`14`]

- Add ``redoc_uri`` Sphinx option to override default ``redoc.js``.

  [:issue:`13`, :pr:`16`]

1.4.0 (2018-03-24)
``````````````````

- Update ``redoc.js`` to ``1.21.2``. [:pr:`10`]

- Add support for the following ReDoc options:

  - ``hide-loading``
  - ``native-scrollbars``
  - ``untrusted-spec``

  [:pr:`10`]

1.3.0 (2017-05-12)
``````````````````

- Update ``redoc.js`` to ``1.16.0``. [:pr:`8`]

1.2.0 (2017-04-24)
``````````````````

- Update ``redoc.js`` to ``1.14.0``. [:pr:`6`]

- Add support for the following ReDoc options:

  - ``no-auto-auth``
  - ``path-in-middle-panel``

  [:pr:`7`]

1.1.0 (2017-04-12)
``````````````````

- Add support for the following ReDoc options:

  - ``lazy-rendering``
  - ``suppress-warnings``
  - ``hide-hostname``
  - ``required-props-first``
  - ``expand-responses``

  [:issue:`4`, :pr:`5`]

1.0.1 (2017-04-10)
``````````````````

- Do not copy assets (i.e. ``redoc.js``) to output directory if Sphinx build
  was finished with errors. [:issue:`1`]

1.0.0 (2017-04-08)
``````````````````

- First public release.
