Maintenance
===========
The maintenance section is used to manage interactions with users and view search
statistics.24 The Contact Messages subsection displays all messages sent via the contact
form. NDR Core can be set up to forward all messages to an email address but in order
for this to work, an email server has to be configured. The easiest way is to store the
messages in the database and provide the with a web interface to view them and process
them. Messages can be archived, deleted and exported for further processing.

The Corrections subsection displays all correction suggestions made by users of the
configured database. This is a feature which allows users to suggest that a certain data
entry is wrong or has errors. The feature can be deactivated in this subsection; when
activated, each search result entry features a small button to mark it incorrect. Currently,
this requires only a click but in the future, a ReCAPTCHA or similar will be added to
prevent abuse. All marked entries are displayed in this subsection with their respective
id. The entries can be exported as a CSV file and processed further. This functionality is
preliminary and will be improved in the future.

The Search Statistics subsection displays the search statistics of the configured search
configuration. If the feature is enabled, every time a user searches for something, the
search term, the time of the search and the number of results is stored in the database.
The statistic option is disabled by default. NDR Core uses a simple file database (SQLite)
by default which is not made for large amounts of data and will considerably slow down
your system if a lot of searches are made. You might consider switching to MySQL or
PostgreSQL before enabling this feature when your site expects a lot of traffic. NDR
Core tries to pinpoint the location of the user via the IP address and the GeoIP service.
This is not always possible and is not very reliable, but it allows for a crude overview
from where the users access your database. At the same time, no user data is stored and
the GeoIP service is not used to track users. The IPs themselves are not stored and the
django session cookie does not store any user data.

The last maintenance subsection is Search Engine Optimization. This subsection is
used to configure the SEO of the website. SEO is a complex topic and there are many
ways to optimize a website for search engines. NDR Core provides two ways to optimize
the visibility of the website. First, it creates Robots.txt and Sitemap.xml files which
are used by search engines to index the website.25 Second, it allows for the NDR Core
installation to be connected with ndrcore.org. This is the website of the NDR Core project
and is used to display a list of all NDR Core installations which have been connected to
it. This is useful for users to find other projects and for the NDR Core project to get an
overview of the usage of the software.
