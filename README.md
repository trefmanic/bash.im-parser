bash.im parser
==============

> Updated for parsing башорг.рф

Parser for fetching quotes from башорг.рф (an archive of now defunct bash.im)

*Usage*

    python3 parse.py [start_page] [end_page]

*Example*

    python3 parse.py 1 10

*Requirements*

    requests
    sqlite3
    bs4

The quotes are added into a SQLite database. Main table is called “quotes” and contains 3 fields:

* id (INTEGER)
* text (TEXT)
* datetime (INTEGER)

Datetime is stored as Unix Time.

If the DB file (quotes.sqlite3) does not exist, it is created. If a quote with specific ID is already in database, it will be skipped.