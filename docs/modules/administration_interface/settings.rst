Settings
========
The settings section is used to configure various settings of the website. It features 7
subsections: Page Settings, Language Settings, HTML Header Settings, Search Settings,
Contact Form/Mail Settings, Social Media and Custom Settings. See the table below
for a description of the settings. This section also lets you change the password of the
admin user and set the website to read-only or under-construction mode.
If you activate the read-only mode, the admin interface will be set to read-only and only the
maintenance section will be available in the administration interface. If you activate the
under-construction mode, the website will display a message that the website is under
construction and no pages will be available to the users in the frontend. These settings
can be done by anyone with access to the administration interface and are not meant to
be security but convenience features.

.. list-table:: Page Settings
   :widths: 30 70
   :header-rows: 1

   * - Setting
     - Description
   * - Page is under construction
     - If checked, the website will display a message that the website is under construction.
       No pages will be available to the users in the frontend. Can be yes or no.
   * - Under construction text
     - The text that is displayed when the website is under construction.
       Can be any string; is translatable.
   * - Project Title
     - The title of the project. This is used to create download file names and such and is
       part of each page’s HTML metadata. Can be any string; is translatable.
   * - Default header title
     - The title of the header, that means what is displayed in the browser tab.
       Can be any string; is translatable.

.. list-table:: Language Settings
    :widths: 30 70
    :header-rows: 1

    * - Setting
      - Description
    * - Base language
      - The language in which the content is written. It is strongly recommended to use English
        as the base language. Can be one of the translated languages.
    * - Additional languages
      - The languages in which the content is translated.
        Can be none, one or more of the translated languages

.. list-table:: HTML Header Settings
    :widths: 30 70
    :header-rows: 1

    * - Setting
      - Description
    * - Description
      - The description of the website. Use a comma separated list of keywords or
        describe the project in a few words
    * - Author
      - The author of the website. This can be an institution,
        a person or any other string.

.. list-table:: Search Settings
    :widths: 30 70
    :header-rows: 1

    * - Setting
      - Description
    * - Allow single download
      - If checked, the search results will feature a download button to download a single
        result entry as a JSON file. Can be yes or no.
    * - Allow json list download
      - If checked, the search results will feature a download button to download the maximum
        number of result entries as a JSON file. Can be yes or no.
    * - Allow csv list download
      - If checked, the search results will feature a download button to download the maximum
        number of result entries as a CSV file. Can be yes or no.
    * - Maximum of results to download
      - The maximum number of results that can be downloaded as a list. It is not the idea that
        users download the whole database. This can be done via the long term repository and the
        results feature a link to the source. But it allows for the download of filtered results
        and can be very useful when looking for a specific subset of the data. Can be any integer.

.. list-table:: Contact Form/Mail Settings
    :widths: 30 70
    :header-rows: 1

    * - Setting
      - Description
    * - Message Forwarding Option
      - Can be “Keep messages on server” (default) or “Forward messages”. If “Forward messages” is
        selected, the messages sent via the contact form will be forwarded to the email address
        specified in the settings below. Default subject The default subject of the contact form.
        Can be any string; is translatable.
    * - E-Mail host
      - The host of the email server to send the messages from. Authentication is not supported at
        the moment.
    * - E-Mail to address
      - The email address to forward the messages to. E-Mail from address The email address to
        send the messages from. This can be any string but should be a valid email address. Be
        aware that some email servers will reject emails from invalid email addresses.
    * - Use Captcha
      - If checked, the contact form will feature a captcha. In order for this to work,
        you have to obtain an API key from google and enter it in your settings.py file.

.. list-table:: Social Media
    :widths: 30 70
    :header-rows: 1

    * - Setting
      - Description
    * - Twitter
      - The twitter handle of the project.
        This is used to create a link to the twitter account in the footer.
    * - Instagram
      - The instagram handle of the project.
        This is used to create a link to the instagram account in the footer.
    * - Facebook
      - The facebook handle of the project.
        This is used to create a link to the facebook account in the footer.
    * - Mastodon
      - The mastodon handle of the project.
        This is used to create a link to the mastodon account in the footer.

**Custom Settings** can be added and used in the templates.
