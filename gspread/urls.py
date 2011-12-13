"""
gpread url patterns storage

# General pattern
/feeds/feedType/key/worksheetId/visibility/projection

# Spreadsheet metafeed
/feeds/spreadsheets/private/full
/feeds/spreadsheets/private/full/key

# Worksheet
/feeds/worksheets/key/visibility/projection
/feeds/worksheets/key/visibility/projection/worksheetId

# Cell-based feed
/feeds/cells/key/worksheetId/visibility/projection
/feeds/cells/key/worksheetId/visibility/projection/cellId

"""
import re

from .exceptions import UnsupportedFeedTypeError, UrlParameterMissing


SPREADSHEETS_SERVER = 'spreadsheets.google.com'
SPREADSHEETS_FEED_URL = 'https://%s/%s/' % (SPREADSHEETS_SERVER, 'feeds')


_feed_types = {'spreadsheets': 'spreadsheets/{visibility}/{projection}',
               'worksheets': 'worksheets/{spreadsheet_id}/{visibility}/{projection}',
               'cells': 'cells/{spreadsheet_id}/{worksheet_id}/{visibility}/{projection}',
               'cells_cell_id': 'cells/{spreadsheet_id}/{worksheet_id}/{visibility}/{projection}/{cell_id}'}

_fields_cache = {}


_field_re = re.compile(r'{(\w+)}')
def _extract_fields(patternstr):
    return _field_re.findall(patternstr)

def construct_url(feedtype=None,
                  obj=None,
                  visibility='private',
                  projection='full',
                  batch=None,
                  spreadsheet_id=None,
                  worksheet_id=None,
                  cell_id=None):
    try:
        urlpattern = _feed_types[feedtype]
        fields = _fields_cache.get(feedtype)
        if fields is None:
            fields = _extract_fields(urlpattern)
            _fields_cache[feedtype] = fields
    except KeyError as e:
        raise UnsupportedFeedTypeError(e)

    obj_fields = obj.get_id_fields() if obj is not None else {}

    params = {'visibility': visibility,
                'projection': projection,
                'batch': 'batch' if batch else None,
                'spreadsheet_id': (spreadsheet_id if spreadsheet_id
                                    else obj_fields.get('spreadsheet_id')),
                'worksheet_id': (worksheet_id if worksheet_id
                                    else obj_fields.get('worksheet_id')),
                'cell_id': cell_id}

    params = dict((k, v) for k, v in params.items() if v is not None)

    try:
        return '%s%s' % (SPREADSHEETS_FEED_URL,
                         urlpattern.format(**params))
    except KeyError as e:
        raise UrlParameterMissing(e)
