Resources
=========
The resources section is used to manage the resources of the project. It features four
subsections: Images, User Interface elements, Uploads and Translations. The images
section lets users upload images and manage them. All images have a type which determines what they are used for. Page Logos are logos to display on the website. Depending on the User Interface style, they are by default displayed in the navigation bar
or in the footer. There is only a single page logo but one can add “translations” to it.
So if the project logo features text, one can add a translation for every language. Figure
Images are images that can be used in page content. NDR Core features a simple template language to insert the images in a styled way.15 Figure images can also be used in
the creation of User Interface elements. Partner Images are images of logos of project
partners. Most research projects have at least an affiliation with a university and most
likely a funding partner. It is common to display the logos of the project partners on the
website. Simply adding the images (and links to the partner websites) in this section
generates a list of logos at the bottom of your website. This can be changed in the pages
section under the manage footer subsection. Person Images are images of project members. Names, roles and links to the person’s website can be added to the image. Users
can now create an “About Us” page and add the images will be added and displayed
as cards in a grid. Background Images can be used as the background of pages and
for the creation of User Interface elements. They should be large enough to cover the
whole page but optimized for the web and not too large in file size. Slideshow Images
can be used to create a number of slideshow-like User Interface elements. They should
optimally be roughly the same dimensions in order to ensure smooth transitions and
rendering of the slideshow.

The User Interface elements section lets users create User Interface elements. There
are currently seven types of elements. The NDR Core data model features a model for
User Interface elements and on for its elements. Some elements only have one child (for
example a figure), others can have multiple children (for example a slideshow). Each
child can have an image, title, text, url and an order index. The parent element (what
is called the User Interface element) has a type which determines how the element is
rendered and a name which is used to use it in the content. These elements mostly
consist of Bootstrap components and are rendered as such. They can be called within
the static page text via a simple markup language.

Card elements are used to display an image with a title and a caption.17 This lets
you choose an image and add a title and a text. This element is only needed if you want
to override the default figure rendering of the image. Otherwise, you can display the
image as a figure ( [[figure|image-number]] ).

Slideshow elements are used to display a slideshow of images (See Figure 4.9) The
slideshow works the same as a carousel, but it does not allow for the display of titles
and text.

Carousel elements are used to display a carousel of images.19 Currently 10 slides
are supported but this more of a limitation of the administration interface than of the
element itself. Each slide can have an image, a title and a text. You can choose to
autoplay the component and to display the controls (back/forward).

Jumbotron and Banner elements are used to display a large banner with an image
as background. The jumbotron element lets you add title and text, while the banner is a
plain image.

The Iframe element lets you embed an iframe. This is useful to display content from
other sources such as videos, map renderings, interactive graphs or similar elements
from other providers. A user can copy the embed code of a service into this element,
and it will be rendered as an iframe.

The latest addition to the list of elements (which - like most structures in NDR Core
- is meant to be extendable) is the Manifest Viewer element. It lets you choose a group
of IIIF manifests21 and displays them in a IIIF viewer.22 This allows research projects to
display their source material or part of it to create a peak into the data. It is also possible
to refer to a viewer element from search results, offering the possibility to display the
source material of a search result. These elements were created when they were needed
for projects but this list is not exhaustive and can be extended if needed. The rich text
editor of the CkEditor allows users to insert an array of elements including images,
links, tables and lists. This is enough for most use cases but if a project needs a more
complex element, User Interface elements are good solution to that problem.

The file uploads section lets users upload files to the server. The files can be of any
type and are stored in the media directory of the project. Each upload can be referred
to via the before mentioned markup language ( [[file|file-number]] ) and be displayed as a download link. This works well for PDF files but also for images, videos
or other files. The upload size is limited by the configuration of the web server but can
be changed if needed. The filename is kept intact if possible and each upload can have
a title. A special type of uploads are IIIF manifests. If they need to be displayed in a
viewer, they cannot stem from another server because of CORS restrictions.23 After creating a manifest group, users can upload manifests to the group and use the group in a
manifest viewer User Interface element. The manifest viewer creates a searchable dropdown menu to select the manifest to display. On the pages that use a manifest viewer
element, “manifest” and “page” can be used as attributes to directly jump to a page of
a manifest. This functionality can be used when pointing a search result to a manifest
viewer element.

The translations section lets users create translations for searches, images and User
Interface elements. The translation of the static page content can be done via the page
edit form but all other translations are managed in this section. During the installation
process, a base language was selected and you should enter all your data in that language when creating new objects in the administration interface. It is strongly recommended to use English as the base language. Not only is it the most common language
in academia, it is also the language of the web and it is NDR Core’s default language.
NDR Core is designed to be multilingual and has implemented this functionality to a
certain degree. Theoretically all languages could be supported but the content that is
created and translated by the user is not the only text in NDR Core. Automatically generated search forms and result displays feature text elements which are injected into the
HTML code by NDR Core. Internationalization (i18n) is a common problem in software
development and there are many solutions to it. NDR Core uses the Django i18n system
to translate the text elements. This relies on Gettext and PO files. This allows the source
code to be written in English and all text elements are marked for translation. Django
can extract these texts and creates PO files for all languages that are translated in NDR
Core. Currently, NDR Core supports English and German and has automated translations into
French and Italian. The process of adding and translating into a new language
is a well documented process and can be done by anyone with the appropriate language
skills. The translation has be done for the frontend. The administration interface of NDR
Core will only be available in English. This has several reasons but the most important
one ist, that it is not worth the considerable effort to translate the administration
interface and maintain an updated translation during an agile development process. The
Gettext system needs compiling in order to work and is thus no option for the dynamically
changeable content the users add to the website. Instead, NDR Core’s data model
features a translation model which can be linked to all translatable field in the other
model classes.

First, a language has to be activated in the settings section. Select the languages you
want to use and save the settings. There are seven subsections in the translations section:
Page Titles, Forms, Form Fields, Result Fields, Image Texts, UI Elements and Settings.
Whenever a subsection is selected, a list of the available languages is displayed. When a
language is selected, a list of all objects of the selected type is displayed. The Page Titles
section is needed to translate the page titles and their navigation labels (See Figure 4.10).
The Forms section translates the form name which is displayed as a tab title above the
search form. The Form Fields section translates the labels of the search form fields and
their help text. The Result Fields are rich text fields which mix dynamic and static content.
You can translate the static text which is mixed into the dynamic result data fields.

TODO Image

The Image Texts section translates the titles and captions of images. The UI Elements
section translates the titles and texts of the User Interface elements and their children.
There are translatable Settings such as default header texts or copyright notices which
can be translated.
