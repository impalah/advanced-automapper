================
User Guide
================

Object autommaper based on type hints.

Installation
============

Using pip:

.. code-block:: bash

   pip install advanced-automapper

Using poetry

.. code-block:: bash

   poetry add advanced-automapper

Get started
===========

It is important to note that PyAutomapper requieres that both origin and destination classes have have type hints to define the type for every field.

Let's say you have a Pydantic model called Person, and you need to map it to a SqlAlchmey model to save it to a database:

.. code-block:: python

   # Python code here

To create a PersonAlchemy object:

.. code-block:: python

   from automapper import mapper

   mapped_person = mapper.map(person, PersonAlchemy)

   print(mapped_person)

Add custom mapping
==================

PyAutomapper allows to map fields with different names between them using custom mapping.

Imagine that, in the previous SqlAlchemy class the gender field is called "genero":

.. code-block:: python

   # Python code here

The solution is to add a cutom mapping in the Mapper relating the field "gender", in the source class, with "genero" in the target.

.. code-block:: python

   from automapper import mapper

   mapper.add_custom_mapping(PersonPydantic, "gender", "genero")

   mapped_person = mapper.map(person, PersonAlchemy)

   print(mapped_person)

More examples
=============

The tests folder in the code repository contains examples of mapping between different python objects.