Source Code Documentation
=========================
NDR Core's Source code documentation.
**Models** describes the database schema and the relationships between the tables.
This is the *configuration database* for the NDR Core instance, not the *data database*.
**Views** are the Django views for the data presentation frontend.
**Forms** mainly contain the search form classes used to construct the configured search forms.
**Admin Views** are the Django admin views for the admin interface.
**Admin Forms** are the Django admin forms for the admin interface.
**Helpers** are utility functions used throughout the codebase.

.. toctree::
   :maxdepth: 1
   :caption: Main Modules

   source_doc/models.rst
   source_doc/views.rst
   source_doc/forms.rst
   source_doc/admin-views.rst
   source_doc/admin-forms.rst
   source_doc/helpers.rst
