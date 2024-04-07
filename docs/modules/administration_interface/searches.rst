Searches
========
NDR Core does not store your data, it accesses it via an API.
The configuration of an API access, its search forms and result displays is called a search configuration.
Each search configuration can be associated with a number of search and result fields by composing them into search forms and result displays.
First a search configuration must be created and the connection details must be configured.
Then a user can create search fields and result fields.
These fields are used to create search forms and result displays.

In the search section, users can create search configurations and manage them. A
search configuration has a name which is used as primary key and to prefix all associated search and result fields. It has a label which is used to display the search configuration in the web interface and as a tab title if you use multiple search configurations on
a page. Most importantly, your search configuration has an API Type which determines
how the data is fetched. This also defines the format of the Connection URL. If the API
implementation supports it and the connection needs it, an access can be configured by
adding a Username and Password or an Access Token. In order for the search mechanism to work,
some more information is needed. An Id field, a Sort field and a Sort
order must be configured. One can select if the search has a compact result view (on
top of normal result view) and how the results are paginated.
It is possible (and recommended) to add a repository URL to link to the FAIR dataset and a citation expression
to cite the dataset.
Next, a user can specify if there is a Simple Search for this configuration.
A simple search is a search form with a single text field that can search the value
of multiple data fields. This is useful if you want to provide a catch-all search for users
who just want to browse the data or want to know if certain keywords are present in
the data. Multiple Searches on one page are organized in tabs. One can select if they
want to display the simple search first or last and specify values for the field label and
the help text of the search form. If the simple search is activated, the query field(s) must
be specified.

After creating a search configuration, a user can create search fields and result fields.
Search fields have a label which is used in the search form, a name which is used in
the HTML request and an api parameter which is used to query the API. They have a
type which determines how the field is rendered and how it is queried. Consider the
following example: A user wants to create a search form to search for persons. Typical
fields for a list of persons would be "Last Name", "Gender" or "Professions". The first
one would be a string field which renders a text field and queries the API with a string.
The second one would be a choice field which renders a dropdown menu and queries
the API with key which corresponds to the selected value. The third one would be a
multiple choice field which renders a Select2 dropdown menu and queries the API with
a list of keys which correspond to the selected values. Additionally, a help text can be
added, the field can be marked as mandatory and several other options can be applied
depending on the field type.

.. list-table:: Field Types
   :widths: 25 75
   :header-rows: 1

   * - Field Type
     - Description
   * - String
     - Searches for a String Regular Expressions can be used.
   * - Number
     - Creates a field which only allows for numbers. A lowest and highest possible value can be specified.
   * - Dropdown List
     - Renders a dropdown menu depending on the supplied list choices.
   * - Multi Select List
     - Renders a Select2 dropdown menu depending on the supplied list choices.
   * - Boolean
     - Renders a slider component (on/off) and queries the API with a boolean.
   * - Date
     - Renders a date picker and queries the API with a date.
   * - Date Range
     - Renders two date range pickers and queries the API with a date range.
   * - Number Range
     - Renders a text field which can be used to enter a printer-like range (e.g. 1,2,4-8,21) and queries the API with a list of valid numbers.
   * - Hidden
     - Does not render a visible field but can be used to apply a static value to the query.
   * - Info Text
     - Renders a box with Info text. This can be used to help users enter their values if the help text under the fields is not enough.

The choices for dropdown lists and multi select lists can be configured in the search
field. For the moment, the contents of a CSV file can be copied into the configuration.
As a mechanism this is good enough as the first line defines the keys and the following
lines define the values. This allows to store all the information needed and also store
the translation in these CSV-formatted lines. This way of entering the choices does not
seem very user-friendly but my experience has shown that these curated lists are prepared
by researches in spreadsheet programs which can easily export the data in a CSV
format. Consider the following example: A user wants to create the before mentioned
dropdowns for “Gender” and "Professions".
For the "Gender" dropdown, the list-choice field of the search field configuration
would look like this:

::

    key,value,value_de
    m,Male,Männlich
    f,Female,Weiblich
    d,Diverse,Divers

The key is used to query the API and the value is displayed in the dropdown menu.
If the selected language is German, the value_de is displayed instead.
The second example shows the power of this mechanism.

::

    key,value,value_de,info,info_de,printable,searchable
    prof-phys-1,Physician,Arzt,Someone who practices medicine,Jemand der Medizin praktiziert,true,true
    prof-edu-1,Teacher,Lehrer,Someone who teaches,Jemand der unterrichtet,true,true
    prof-spec-1,Unemployed,Arbeitslos,Someone who is unemployed,Jemand der arbeitslos ist,false,false
    prof-manu-35,Coat button manufacturer,Knopfhersteller,Someone who [...],Jemand der [...],true,false

The first two lines are normal values; they have a key, a label and its translation and
info texts which are displayed when hovering over the data in the result display. The
last two values in the line (printable and searchable) are used to determine if the value
shows up in the result display and if it can be searched for (that means if it shows up in
the dropdown menu). Because - in this example - the research team has decided not to
list "Unemployed" as a profession it doesn't let users search for it and doesn't display it
in the result display. The last line in the example shows a very specific profession that is
only listed once in the dataset and the researchers have also tagged it with the general
profession “Manufacturer”. In order to make the search easier, they have decided to not
display it in the dropdown menu but to allow users to search for it, but they want it to
show up in the result display.
The CSV string can take additional columns and the order doesn't matter as long as
the first lines defines the proper keys. Refer to the following table for a list of basic keys. You can
access additional values when rendering the result display. For instance, you can add a
column "color" and use it to color the result display.

.. list-table:: Keys of Search Field Options
   :widths: 25 75
   :header-rows: 1

   * - Column
     - Description
   * - key
     - The key of the choice. This field is mandatory and will be searched for in the data.
   * - value
     - The value of the choice. This field is mandatory and will be displayed in the dropdown menu. This value will be displayed as a default value if no translation is found in this list.
   * - value\_[lang]
     - The translation of the value. This field is optional and will be displayed in the dropdown menu if the selected language is [lang].
   * - printable
     - Determines if the value is displayed in the result display. You always can display values if you want to, but if you have a list of values (e.g. professions) you can decide to only display the values that are relevant to your project.
   * - searchable
     - Determines if the value is displayed in the dropdown menu.
   * - info
     - The info text of the value. This field is optional and will be displayed when hovering over the value in the result display
   * - info\_[lang]
     - The translation of the info text. This field is optional and will be displayed when hovering over the value in the result display if the selected language is [lang].

According to our example, three search fields have been created: a text field to search
for a last name, a single-selection dropdown to specify a gender and a multi-selection
dropdown to specify one or multiple professions. Now these fields can be added to a
search form. Every field is placed in a grid with 12 columns; it has a row number, a
column number and a width.11 The administration interface shows you a preview of
the search form and lets you add, remove and move the before created search fields.

Technically, the search is now usable. The search configuration can be added to a
search page and the configured search form will be displayed. Depending on whether
you have configured a simple search, the search form will be displayed in a tab or as a
standalone form. The result display will - while functional - not be very appealing. The
data will be displayed as pretty-printed JSON and the whole dataset will be shown. In
the described example, one dataset would be a person and might look like this as raw
JSON data.

TODO: IMAGE

The result display can be configured to display the data in a more appealing way.
In very much the same fashion as search fields, result fields can be created. A result
field has a **label** which is used for internal reference and an **expression** which is used to
render the data. Additionally, CSS **field classes** can be applied to the whole field. The
expression is a string which can contain markup tags to render the data in a certain way.
There are a lot of possibilities to style values with NDR Core’s markup language and
it is described in the next section. To complete the example, a result field called "Title"
could be added and the expression could be set to ``{name.last_name}`` . This would
extract the value of the last_name key from the data and this string can now be styled
with the CkEditor. This expression can also be mixed with static text and other markup
tags.

TODO: IMAGE

Just as with search fields, the result fields can be added to a result display in the
same manner. They are placed in a grid with 12 columns and can be moved, added and
removed. Now the search is fully functional and the result display is styled.
Now the described search example is fully functional and the result display is styled.
There are some other options which can be applied which are not essential in
understanding how the search works.
For a full list of options, refer to the documentation.