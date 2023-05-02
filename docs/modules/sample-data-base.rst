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

    [
        {
            "id": "1",
            "title": "The Great Gatsby",
            "author": {
                "name": "F. Scott Fitzgerald",
                "gnd": "118540004"
            },
            "year": 1925,
            "pages": 180,
            "genre": "fiction",
            "language": "en"
        },
        {
            "id": "2",
            "title": "The Grapes of Wrath",
            "author": {
                "name": "John Steinbeck",
                "gnd": "118614798"
            },
            "year": 1939,
            "pages": 464,
            "genre": "fiction",
            "language": "en"
        },
        {
            "id": "3",
            "title": "The Catcher in the Rye",
            "author": {
                "name": "J. D. Salinger",
                "gnd": "118610110"
            },
            "year": 1951,
            "pages": 277,
            "genre": "fiction",
            "language": "en"
        },
        {
            "id": "4",
            "title": "Die Verwandlung",
            "author": {
                "name": "Franz Kafka",
                "gnd": "118559086"
            },
            "year": 1915,
            "pages": 55,
            "genre": "fiction",
            "language": "de"
        },
        {
            "id": "5",
            "title": "L'Amant",
            "author": {
                "name": "Marguerite Duras",
                "gnd": "118530707"
            },
            "year": 1984,
            "pages": 117,
            "genre": "fiction",
            "language": "fr"
        },
        {
            "id": "6",
            "title": "On the Origin of Species",
            "author": {
                "name": "Charles Darwin",
                "gnd": "118527579"
            },
            "year": 1859,
            "pages": 502,
            "genre": "non-fiction",
            "language": "en"
        },
        {
            "id": "7",
            "title": "Ansichten der Natur",
            "author": {
                "name": "Alexander von Humboldt",
                "gnd": "118554471"
            },
            "year": 1808,
            "pages": 448,
            "genre": "non-fiction",
            "language": "de"
        },
        {
            "id": "8",
            "title": "Emile ou De l'éducation",
            "author": {
                "name": "Jean-Jacques Rousseau",
                "gnd": "118607915"
            },
            "year": 1762,
            "pages": 432,
            "genre": "non-fiction",
            "language": "fr"
        }
    ]

The data item above is a book. It has a unique identifier ``id``. It also has a title,
author, year, pages, and genre. The data item can have any number of fields.

IIIF Images
===========

.. list-table:: Images
    :widths: 25 25 25 25
    :header-rows: 0

    * - .. image:: ../_static/samples/gatsby.jpg
          :width: 100%
          :align: center
          :alt: The Great Gatsby
      - .. image:: ../_static/samples/grapes.jpg
          :align: center
          :alt: The Grapes of Wrath
      - .. image:: ../_static/samples/catcher.jpg
          :width: 200px
          :align: center
          :alt: The Catcher in the Rye
      - .. image:: ../_static/samples/verwandlung.jpg
          :width: 200px
          :align: center
          :alt: Die Verwandlung

    * - .. image:: ../_static/samples/lamant.jpg
          :width: 200px
          :align: center
          :alt: L'Amant
      - .. image:: ../_static/samples/origin.jpg
          :width: 200px
          :align: center
          :alt: On the Origin of Species
      - .. image:: ../_static/samples/ansichten.jpg
          :width: 200px
          :align: center
          :alt: Ansichten der Natur
      - .. image:: ../_static/samples/emile.jpg
          :width: 200px
          :align: center
          :alt: Emile ou De l'éducation
