######################
Example Database Setup
######################

These steps are only needed if you are populating the data yourself. In this example
we will use a MongoDB. If your data is provided by a third party, you can skip this
section.

It is assumed that you have a MongoDB server running on your localhost or your virtual
machine. Refer to the :doc:`install-on-a-server` for more information on how to install
and run MongoDB. It is also assumed that you have a IIIIF image server running on your
localhost or your virtual machine. Refer to the :doc:`install-on-a-server` for more
information on how to install and run a IIIF image server.

The whole example dataset is to be found here: :download:`example_data.zip <../_static/samples/example_data.zip>`
The example data is a collection of 8 books. Each book has a cover image and data about it.

Example Data
============
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
            "source": {
                "info": "http://localhost:8182/iiif/3/gatsby.jpg/info.json",
                "cover": "http://localhost:8182/iiif/3/gatsby.jpg/full/max/0/default.jpg",
                "title_fragment": "http://localhost:8182/iiif/3/gatsby.jpg/0,0,200,200/max/0/default.jpg"
            },
            "year": 1925,
            "pages": 180,
            "genre": "fiction",
            "language": "en",
            "places": [
                {
                    "name": "New York",
                    "geonames": "5128581"
                },
                {
                    "name": "Long Island",
                    "geonames": "5128638"
                }
            ],
          "wikidata": "Q168384"
        },

        [...]
    ]

The example is pretty self-explanatory. The ``source`` field contains links to the IIIF image
server. Because, for this example, we have stored the images on the same server as the NDR Core
server, we can use the localhost address. This is not recommended. You should store your images
in long term repository. The ``title_fragment`` field is a link to a fragment of the cover,
showing only the title of the book. The ``places`` field contains a list of places that are
identified by their geonames id. The ``wikidata`` field contains a link to the Wikidata entry
for this book.

Add Data to MongoDB
-------------------
The following steps will add the example data to your MongoDB. If you are using your own data,
you can skip this section.

.. note::

    The following steps assume that you have a MongoDB server running on your localhost or your
    virtual machine. Refer to the :doc:`install-on-a-server` for more information on how to
    install and run MongoDB.

1. Download the example data: :download:`example_data.zip <../_static/samples/example_data.zip>`
2. Unzip the example data
3. Open a terminal and navigate to the folder where you unzipped the example data
4. Run the following command to import the data into your MongoDB:

    .. code-block:: bash

        mongoimport --db ndr --collection books --file data.json

    This will create a database called ``ndr`` and a collection called ``books``. The data
    will be imported into the ``books`` collection.


IIIF Images
===========
The following randomly collected images are used in this example:

.. list-table:: Images
    :widths: 25 25 25 25
    :header-rows: 0

    * - .. image:: ../_static/samples/gatsby.jpg
          :align: center
          :alt: The Great Gatsby
      - .. image:: ../_static/samples/grapes.jpg
          :align: center
          :alt: The Grapes of Wrath
      - .. image:: ../_static/samples/catcher.jpg
          :align: center
          :alt: The Catcher in the Rye
      - .. image:: ../_static/samples/verwandlung.jpg
          :align: center
          :alt: Die Verwandlung

    * - .. image:: ../_static/samples/lamant.jpg
          :align: center
          :alt: L'Amant
      - .. image:: ../_static/samples/origin.jpg
          :align: center
          :alt: On the Origin of Species
      - .. image:: ../_static/samples/ansichten.jpg
          :align: center
          :alt: Ansichten der Natur
      - .. image:: ../_static/samples/emile.jpg
          :align: center
          :alt: Emile ou De l'éducation

Add Images to IIIF Image Server
-------------------------------
The following steps will add the example images to your IIIF image server. If you are using your
own images, you can skip this section.

.. note::

    The following steps assume that you have a IIIF image server running on your localhost or your
    virtual machine. Refer to the :doc:`install-on-a-server` for more information on how to
    install and run a IIIF image server.

1. Download the example data:  :download:`example_data.zip <../_static/samples/example_data.zip>`
2. Unzip the example data
3. Open a terminal and navigate to the folder where you unzipped the example data
4. Move the images to the IIIF image directory. The exact path depends on your configuration.

    .. code-block:: bash

        mv *.jpg /var/www/<project_root>/images

Next Steps
==========
If you followed the Installation and Setup instructions and this guide, you should now have
a running NDR Core installation, a MongoDB with example data and a IIIF image server with
example images. You can now start to use NDR Core.

You either can follow the :doc:`sample-setup` guide or access the administration interface at
``http://<your-domain>/ndr_core``. The default username is ``ndr_core_admin`` and the default
password is ``ndr_core``. You should change the password as soon as possible.
