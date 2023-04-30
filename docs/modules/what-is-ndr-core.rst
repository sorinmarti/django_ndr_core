#################
What is NDR Core?
#################

NDR Core is a system to help you build a project website to present your research data. Modern science and humanities
projects often produce data they want to make accessible. The data should be stored in a FAIR environment and
thus saved for long term use. Repositories with this functionality (such as Zenodo or InvenioRDM) do a great job storing
the data and ensuring FAIR principles (Findable, Accessible, Interoperable, Reusable) and providing important functionalities
such as providing persistent identifiers. What these repositories don't do is showcase your data and present it with a
pretty website. After a research project you want to present data with context, maybe you want to publish studies alongside
and you want to rapidly search it. NDR Core helps you to do just that.

Who should use it?
==================
NDR Core is aimed at project groups who want their data published in a modern responsive website without having to deal
to much with the hassle of building one. Think of NDR Core as a very specialized CMS (Content Management System) which is
tailored to enable you to display search results and static website content.

Check out sites which were built with NDR Core: https://ndrcore.org


How does it work?
=================
NDR Core is built with the Django Framework. It is basically a module which helps you build your own Django app. NDR
Core takes care of creating a basic webpage and provides you with an administration UI that lets you manage your pages
and configure the access to your search API. It lets you configure search forms and helps you take care of the basic
elements most project websites need such as Contact forms, About Pages, File downloads, etc.

What do you need?
=================
NDR Core needs to be installed as a Django installation. You'll need a database to store your data. You'll need a search
engine to index your data and provide search results. You'll need a webserver to serve your page. You'll need a domain
to serve your page from.

- NDR Core takes care of most of the django installation. It also provides a default built-in database configuration.
- NDR Core provides access to multiple types of data sources over API implementations. Ideally you'll have a search engine
  which provides access your data. If you need to store the searchable data yourself, you can, for example, use mongodb.

How to start?
=============
Read this documentation, download NDR Core and follow the step by step instructions to get you started.
Start with :doc:`how-to-get-started`