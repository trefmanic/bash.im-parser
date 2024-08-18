#!/usr/bin/env python

import sys
import errno
import requests
import sqlite3
import time
import datetime

from bs4 import BeautifulSoup

class Parser:
    db_file = "quotes.sqlite3"
    user_agent = (
        "Mozilla/5.0 "
        "(X11; Ubuntu; Linux x86_64; rv:30.0) "
        "Gecko/20100101 Firefox/30.0"
    )

    def __init__(self, start_page, end_page):
        self.start_page = start_page
        self.end_page = end_page
        self.db = sqlite3.connect(self.db_file)
        self.create_table()

    def create_table(self):
        cursor = self.db.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS quotes "
            "(id INTEGER, text TEXT, datetime INTEGER)"
        )
        self.db.commit()

    def get_url(self, page_number):
        return "https://башорг.рф/index/%s" % page_number

    def fetch_page(self, page_number):
        req = requests.get(
            self.get_url(page_number),
            headers={"User-Agent": self.user_agent},
            timeout=120
        )
        return req.content

    def parse_all_pages(self):
        for page_number in range(self.start_page, self.end_page + 1):
            self.parse_quotes(page_number)
            #We are polite
            time.sleep(5)

    def parse_quotes(self, page_number):
        html = self.fetch_page(page_number)
        soup = BeautifulSoup(html, "lxml")
        quote_divs = soup.find_all("div", class_="quote__frame")
        for quote_div in quote_divs:
            quote = {}

            text_div = quote_div.find("div", class_="quote__body")

            # Skipping advertisement
            if not text_div:
                continue

            # The quote text divs contain strings of text and
            # <br> elements. Here all contents of a text div
            # are joined with any elements replaced by \n.
            quote["text"] = "".join(
                map(
                    lambda x: x if isinstance(x, str) else "\n",
                    text_div.contents
                )
            )

            quote["text"] = quote["text"].strip()


            header_div = quote_div.find("header")

            quote["datetime"] = header_div.find("div",class_="quote__header_date").contents[0].strip()

            quote["id"] = header_div.find(
                "a",
                class_="quote__header_permalink"
            ).contents[0][1:]

            self.write_quote(quote)

    def write_quote(self, quote):
        cursor = self.db.cursor()

        same_id_quotes = cursor.execute(
            "SELECT * FROM quotes WHERE id=?",
            (quote["id"],)
        ).fetchall()

        if len(same_id_quotes):
            sys.stdout.write(
                "Skipping quote #%s as it is already in the DB\n"
                %
                quote["id"]
            )
            return
        # Verbose log
        sys.stdout.write("Writing quote #%s\n" % quote["id"])
        dt = datetime.datetime.strptime(quote["datetime"], "%d.%m.%Y в %H:%M")
        timestamp = (dt - datetime.datetime(1970, 1, 1)).total_seconds()

        cursor.execute(
            "INSERT INTO quotes (id, text, datetime) VALUES (?,?,?)",
            (quote["id"], quote["text"], timestamp)
        )

        self.db.commit()

if __name__ == "__main__":
    arguments = sys.argv
    if (
        len(arguments) == 3
        and arguments[1].isdigit()
        and arguments[2].isdigit()
    ):
        start_page = int(arguments[1])
        end_page = int(arguments[2])

        if start_page > 0 and end_page >= start_page:
            p = Parser(start_page, end_page)
            p.parse_all_pages()
        else:
            sys.stderr.write("Please check the page numbers\n")
            sys.exit(errno.EINVAL)
    else:
        sys.stderr.write("Invalid arguments\n")
        sys.exit(errno.EINVAL)
