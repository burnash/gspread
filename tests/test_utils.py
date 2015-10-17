"""Testing utilities
"""

from textwrap import dedent
from xml.etree import ElementTree


def to_rfc3339(a_datetime):
    # TODO(msuozzo)
    raise NotImplementedError


class SpreadsheetFeed(object):
    """A helper class for constructing XML spreadsheet feed responses.

    :param updated_dt: The datetime at which there was an update to some
        element of the spreadsheet feed.
    :param dev_email: The @developer.gserviceaccount.com address used to
        access the spreadsheets API.
    """

    SPREADSHEET_FEED = dedent("""
        <?xml version="1.0" encoding="UTF-8"?>
        <ns0:feed xmlns:ns0="http://www.w3.org/2005/Atom"
            xmlns:ns1="http://a9.com/-/spec/opensearchrss/1.0/">
          <ns0:id>https://spreadsheets.google.com/feeds/spreadsheets/private/full</ns0:id>
          <ns0:updated>{updated}</ns0:updated>
          <ns0:category scheme="http://schemas.google.com/spreadsheets/2006"
              term="http://schemas.google.com/spreadsheets/2006#spreadsheet" />

          <ns0:title type="text">Available Spreadsheets - {dev_email}</ns0:title>
          <ns0:link href="http://docs.google.com" rel="alternate" type="text/html" />
          <ns0:link
              href="https://spreadsheets.google.com/feeds/spreadsheets/private/full"
              rel="http://schemas.google.com/g/2005#feed" type="application/atom+xml" />
          <ns0:link
              href="https://spreadsheets.google.com/feeds/spreadsheets/private/full"
              rel="self" type="application/atom+xml" />
          <ns1:totalResults>{num_results}</ns1:totalResults>
          <ns1:startIndex>1</ns1:startIndex>

        {entries}

        </ns0:feed>
    """)

    ENTRY = dedent("""
      <ns0:entry>
        <ns0:id>https://spreadsheets.google.com/feeds/spreadsheets/private/full/{key}</ns0:id>
        <ns0:updated>{updated}</ns0:updated>
        <ns0:category scheme="http://schemas.google.com/spreadsheets/2006"
            term="http://schemas.google.com/spreadsheets/2006#spreadsheet" />
        <ns0:title type="text">{title}</ns0:title>
        <ns0:content type="text">{title}</ns0:content>
        <ns0:link
            href="https://spreadsheets.google.com/feeds/worksheets/{key}/private/full"
            rel="http://schemas.google.com/spreadsheets/2006#worksheetsfeed"
            type="application/atom+xml" />
        <ns0:link href="https://docs.google.com/spreadsheets/d/{key}/edit"
            rel="alternate" type="text/html" />
        <ns0:link
            href="https://spreadsheets.google.com/feeds/spreadsheets/private/full/{key}"
            rel="self" type="application/atom+xml" />
        <ns0:author>
          <ns0:name>{name}</ns0:name>
          <ns0:email>{email}</ns0:email>
        </ns0:author>
      </ns0:entry>
    """)

    def __init__(self, updated_dt, dev_email):
        self.updated = to_rfc3339(updated_dt)
        self.dev_email = dev_email
        self.entries = []

    def add_entry(self, sheet_id, sheet_title, sheet_owner_name,
                  sheet_owner_email, updated_dt):
        """Adds a spreadsheet entry to the feed.

        :param sheet_id: The Base64-encoded sheet ID
        :param sheet_title: The title of the sheet
        :param sheet_owner_name: The name of the sheet owner. This will be the
            full name attached to the Google account.
        :param sheet_owner_email: The email of the sheet owner. This will be
            the email address attached to the Google account (will probably
            end in @gmail.com).
        :param updated_dt: The datetime at which the spreadsheet was last
            updated.
        """
        self.entries.append({
            'key': sheet_id,
            'title': sheet_title,
            'updated': to_rfc3339(updated_dt),
            'name': sheet_owner_name,
            'email': sheet_owner_email,
        })

    def to_xml(self):
        return ElementTree.parse(str(self))

    def __str__(self):
        entry_strs = [self.ENTRY.format(**entry_dict)
                      for entry_dict in self.entries]
        return self.SPREADSHEET_FEED.format({
            'updated': self.updated,
            'dev_email': self.dev_email,
            'num_results': len(self.entries),
            'entries': '\n\n'.join(entry_strs),
        })
