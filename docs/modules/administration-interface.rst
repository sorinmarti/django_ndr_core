########################
Administration interface
########################

For this introduction, we assume that you have your django framework installed locally and can access it via
`localhost:8000 <localhost:8000>`_ You can access the NDR Core administration interface via `localhost:8000/ndr_core/ <localhost:8000/ndr_core>`_.
You will need to login, in order to access the administration interface. When initializing your NDR Core installation,
a user named *ndr_core_admin* was created. The initial password is *ndr_core*.

**It is highly recommended that you change your password!**

Dashboard
=========
TODO

Create, Delete And Edit Pages
=============================
NDR Core lets you create, delete and edit pages. Each page has a number of common parameters and a type which provides a
specialized functionality.

Common Parameters
-----------------
- **Page Title**: This is the page's title, eg. its <h1> heading.
- **Label**: The page's label is used in the navigation
- **Page Type**: Type of the page (see below)
- **View Name**: The views name (for reference and URL construction)

Template Page
-------------
Template pages show static content. You can provide HTML in the generated template or use the Rich Text Editor to
provide content.

Simple Search
-------------
Creates a page with a catch-all simple search. It features a single search field and an AND/OR option.

Custom Search
-------------
Creates a page with one or multiple configured search forms.

Combined Search
---------------
Creates a page with a tabulated search form, showing a simple or a custom search.

Filterable List
---------------
Shows a filterable list of data.

Contact Form
------------
Shows a contact form to send the project members a message.

Manage Your Setting Values
==========================
TODO

Create A Search Configuration
=============================
TODO
