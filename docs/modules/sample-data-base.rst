######################
Populate Your Database
######################

These steps are only needed if you are populating the data yourself. In this example
we will use a MongoDB. If your data is provided by a third party, you can skip this
section.

It is assumed that you have a MongoDB server running on your localhost or your virtual
machine. Refer to the :doc:`install-on-a-server` for more information on how to install
and run MongoDB. It is also assumed that you have a IIIIF image server running on your
localhost or your virtual machine. Refer to the :doc:`install-on-a-server` for more
information on how to install and run a IIIF image server.

Creating Your Data
==================
How to create your research data is out of scope for this tutorial. However, we will
provide a sample dataset that you can use to follow along with this tutorial. Each
searchable item must be a JSON object. The JSON object must have a unique identifier
field. In this example, we will use the field ``id`` as the unique identifier.

Example Data Item:

.. code-block:: json

    {
        "id": "1",
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "year": 1925,
        "pages": 180,
        "genre": "fiction"
    }

The data item above is a book. It has a unique identifier ``id``. It also has a title,
author, year, pages, and genre. The data item can have any number of fields.

IIIF Images
===========

.. image:: ../_static/samples/gatsby.png
