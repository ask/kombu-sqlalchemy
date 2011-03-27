===================================================
kombu-sqlalchemy - Kombu transport using SQLAlchemy
===================================================

:version: 1.0.0

Introduction
============

This package enables you to use SQLAlchemy as the message store
for `Kombu`_.


``kombu-sqlalchemy`` contains a single transport,
``sqlakombu.transport.Transport``, which is used like this::

    >>> from kombu.connection import BrokerConnection
    >>> c = BrokerConnection(transport="sqlakombu.transport.Transport")


.. _`Kombu`: http://pypi.python.org/pypi/kombu

Installation
============

You can install ``kombu-sqlalchemy`` either via the Python Package Index (PyPI)
or from source.

To install using ``pip``,::

    $ pip install kombu-sqlalchemy


To install using ``easy_install``,::

    $ easy_install kombu-sqlalchemy


If you have downloaded a source tarball you can install it
by doing the following,::

    $ python setup.py build
    # python setup.py install # as root

License
=======

This software is licensed under the ``New BSD License``. See the ``LICENSE``
file in the top distribution directory for the full license text.

.. # vim: syntax=rst expandtab tabstop=4 shiftwidth=4 shiftround

