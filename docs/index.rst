Stack.PY
========

Stack.PY provides a simple and intuitive set of classes for accessing the `Stack Exchange API <http://api.stackexchange.com/>`__.

Contents:

.. toctree::
   :maxdepth: 2

Features
--------

Stack.PY aims to provide the following set of features:

* complete implementation of version 2.1 of the Stack Exchange API
* partial support for version 2.2 of the API, which includes the ability to post questions and answers
* support for caching API responses using a number of different backends (Redis, MySQL, etc.)
* automatic rate limiting according to the published specification
* transparent support for pagination

Organization
------------

All API routes are divided into two distinct categories:

* global routes and
* site specific routes

The global routes are typically used to perform authentication or enumerate sites and are accessed using a method of the API class. In order to use the site specific routes, you will need to create an instance of the Site class.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

