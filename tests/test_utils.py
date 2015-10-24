"""Testing utilities
"""

from textwrap import dedent
from xml.etree import ElementTree
import time
import datetime
import calendar


def to_utc(a_datetime):
    timestamp = time.mktime(a_datetime.timetuple())
    return datetime.datetime.utcfromtimestamp(timestamp)


def to_rfc3339(a_datetime):
    utc_dt = to_utc(a_datetime)
    ms = utc_dt.microsecond / 10000
    return utc_dt.strftime('%Y-%m-%dT%H:%M:%S') + '.%02dZ' % ms


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
    """).strip('\n')

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
    """).strip('\n')

    def __init__(self, updated_dt, dev_email):
        self.updated = to_rfc3339(updated_dt)
        self.dev_email = dev_email
        self.entries = []

    def add_entry(self, sheet_key, sheet_title, sheet_owner_name,
                  sheet_owner_email, updated_dt):
        """Adds a spreadsheet entry to the feed.

        :param sheet_key: The unique spreadsheet key consisting of 44 Base64
            characters.
        :param sheet_title: The title of the sheet.
        :param sheet_owner_name: The name of the sheet owner. This will be the
            full name attached to the Google account.
        :param sheet_owner_email: The email of the sheet owner. This will be
            the email address attached to the Google account (will probably
            end in @gmail.com).
        :param updated_dt: The datetime at which the spreadsheet was last
            updated.
        """
        self.entries.append({
            'key': sheet_key,
            'title': sheet_title,
            'updated': to_rfc3339(updated_dt),
            'name': sheet_owner_name,
            'email': sheet_owner_email,
        })

    def to_xml(self):
        return ElementTree.fromstring(str(self))

    def __str__(self):
        entry_strs = [self.ENTRY.format(**entry_dict)
                      for entry_dict in self.entries]
        return self.SPREADSHEET_FEED.format(**{
            'updated': self.updated,
            'dev_email': self.dev_email,
            'num_results': len(self.entries),
            'entries': '\n\n'.join(entry_strs),
        })


class WorksheetFeed(object):
    """A helper class for constructing XML worksheet feed responses.

    :param updated_dt: The datetime at which there was an update to some
        element of the spreadsheet feed.
    :param user_name: The name associated with the
        @developer.gserviceaccount.com account used to access the spreadsheets
        API.
    :param user_email: The @developer.gserviceaccount.com address used to
        access the spreadsheets API.
    :param title: The title of the spreadsheet.
    :param key: The unique spreadsheet key consisting of 44 Base64 characters.
    """

    WORKSHEET_FEED = dedent("""
    <?xml version="1.0" encoding="UTF-8"?>
    <ns0:feed xmlns:ns0="http://www.w3.org/2005/Atom" xmlns:ns1="http://a9.com/-/spec/opensearchrss/1.0/" xmlns:ns2="http://schemas.google.com/spreadsheets/2006">
      <ns0:id>https://spreadsheets.google.com/feeds/worksheets/{key}/private/full</ns0:id>
      <ns0:updated>{updated}</ns0:updated>
      <ns0:category scheme="http://schemas.google.com/spreadsheets/2006" term="http://schemas.google.com/spreadsheets/2006#worksheet" />
      <ns0:title type="text">{title}</ns0:title>
      <ns0:link href="https://docs.google.com/spreadsheets/d/{key}/edit" rel="alternate" type="application/atom+xml" />
      <ns0:link href="https://spreadsheets.google.com/feeds/worksheets/{key}/private/full" rel="http://schemas.google.com/g/2005#feed" type="application/atom+xml" />
      <ns0:link href="https://spreadsheets.google.com/feeds/worksheets/{key}/private/full" rel="http://schemas.google.com/g/2005#post" type="application/atom+xml" />
      <ns0:link href="https://spreadsheets.google.com/feeds/worksheets/{key}/private/full" rel="self" type="application/atom+xml" />
      <ns0:author>
        <ns0:name>{name}</ns0:name>
        <ns0:email>{email}</ns0:email>
      </ns0:author>
      <ns1:totalResults>{num_results}</ns1:totalResults>
      <ns1:startIndex>1</ns1:startIndex>

      {entries}

    </ns0:feed>
    """).strip('\n')

    ENTRY = dedent("""
      <ns0:entry>
        <ns0:id>https://spreadsheets.google.com/feeds/worksheets/{key}/private/full/{ws_key}</ns0:id>
        <ns0:updated>{updated}</ns0:updated>
        <ns0:category
            scheme="http://schemas.google.com/spreadsheets/2006"
            term="http://schemas.google.com/spreadsheets/2006#worksheet" />
        <ns0:title type="text">{ws_title}</ns0:title>
        <ns0:content type="text">{ws_title}</ns0:content>
        <ns0:link
            href="https://spreadsheets.google.com/feeds/list/{key}/{ws_key}/private/full"
            rel="http://schemas.google.com/spreadsheets/2006#listfeed"
            type="application/atom+xml" />
        <ns0:link
            href="https://spreadsheets.google.com/feeds/cells/{key}/{ws_key}/private/full"
            rel="http://schemas.google.com/spreadsheets/2006#cellsfeed"
            type="application/atom+xml" />
        <ns0:link
            href="https://docs.google.com/spreadsheets/d/{key}/gviz/tq?gid={ws_id}"
            rel="http://schemas.google.com/visualization/2008#visualizationApi"
            type="application/atom+xml" />
        <ns0:link
            href="https://docs.google.com/spreadsheets/d/{key}/export?gid={ws_id}&amp;format=csv"
            rel="http://schemas.google.com/spreadsheets/2006#exportcsv"
            type="text/csv" />
        <ns0:link
            href="https://spreadsheets.google.com/feeds/worksheets/{key}/private/full/{ws_key}"
            rel="self" type="application/atom+xml" />
        <ns0:link
            href="https://spreadsheets.google.com/feeds/worksheets/{key}/private/full/{ws_key}/{ws_version}"
            rel="edit" type="application/atom+xml" />
        <ns2:colCount>{num_cols}</ns2:colCount>
        <ns2:rowCount>{num_rows}</ns2:rowCount>
      </ns0:entry>
    """).strip('\n')

    def __init__(self, updated_dt, user_name, user_email, title, key):
        self.updated = to_rfc3339(updated_dt)
        self.user_name = user_name
        self.user_email = user_email
        self.title = title
        self.key = key
        self.entries = []

    def add_entry(self, ws_key, ws_title, ws_id, ws_version, num_cols,
            num_rows, updated_dt):
        """Adds a worksheet entry to the feed.

        :param ws_key: The worksheet identifier consisting of 7 Base64
            characters.
        :param ws_title: The worksheet title.
        :param ws_id: The numeric worksheet identifier.
        :param ws_version: The current worksheet version identifier consisting
            of 5-7 (?) Base64 characters.
        :param num_cols: The number of columns in the worksheet.
        :param num_rows: The number of rows in the worksheet.
        :param updated_dt: The datetime at which the worksheet was last
            updated.
        """
        self.entries.append({
            'key': self.key,
            'ws_key': ws_key,
            'ws_title': ws_title,
            'ws_id': ws_id,
            'ws_version': ws_version,
            'num_cols': num_cols,
            'num_rows': num_rows,
            'updated': to_rfc3339(updated_dt),
        })

    def to_xml(self):
        return ElementTree.fromstring(str(self))

    def __str__(self):
        entry_strs = [self.ENTRY.format(**entry_dict)
                      for entry_dict in self.entries]
        return self.WORKSHEET_FEED.format(**{
            'updated': self.updated,
            'name': self.user_name,
            'email': self.user_email,
            'title': self.title,
            'key': self.key,
            'num_results': len(self.entries),
            'entries': '\n\n'.join(entry_strs),
        })
