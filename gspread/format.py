import re

def _ul_repl(m):
    return '_' + m.group(1).lower()

def _underlower(name):
    return name[0].lower() + name[1:]
    #return name[0].lower() + re.sub(r'([A-Z])', _ul_repl, name[1:])

def _parse_string_enum(name, value, set_of_values, required=False):
    if value is None and required:
        raise ValueError("%s value is required" % name)
    if value is not None and value.upper() not in set_of_values:
        raise ValueError("%s value must be one of: %s" % (name, set_of_values))
    return value.upper() if value is not None else None

def _extract_props(value):
    if hasattr(value, 'to_props'):
        return value.to_props()
    return value

def _extract_fieldrefs(name, value, prefix):
    if hasattr(value, 'affected_fields'):
        return value.affected_fields(".".join([prefix, name]))
    elif value is not None:
        return [".".join([prefix, name])]
    else:
        return []

class CellFormatComponent(object):
    pass

class CellFormat(CellFormatComponent):
    def __init__(self, 
        number_format=None,
        backgroundColor=None,
        borders=None,
        padding=None,
        horizontalAlignment=None,
        verticalAlignment=None,
        wrapStrategy=None,
        textDirection=None,
        textFormat=None,
        hyperlinkDisplayType=None,
        textRotation=None
        ):
        self.number_format = number_format
        self.backgroundColor = backgroundColor
        self.borders = borders
        self.padding = padding
        self.horizontalAlignment = _parse_string_enum('horizontalAlignment', horizontalAlignment, {'LEFT', 'CENTER', 'RIGHT'})
        self.verticalAlignment = _parse_string_enum('verticalAlignment', verticalAlignment, {'TOP', 'MIDDLE', 'BOTTOM'})
        self.wrapStrategy = _parse_string_enum('wrapStrategy', wrapStrategy, {'OVERFLOW_CELL', 'LEGACY_WRAP', 'CLIP', 'WRAP'})
        self.textDirection = _parse_string_enum('textDirection', textDirection, {'LEFT_TO_RIGHT', 'RIGHT_TO_LEFT'})
        self.textFormat = textFormat
        self.hyperlinkDisplayType = _parse_string_enum('hyperlinkDisplayType', hyperlinkDisplayType, {'LINKED', 'PLAIN_TEXT'})
        self.textRotation = textRotation

    def to_props(self):
        p = {}
        for a in (
            'number_format', 'backgroundColor', 'borders', 'padding', 
            'horizontalAlignment', 'verticalAlignment', 'wrapStrategy', 
            'textDirection', 'textFormat', 'hyperlinkDisplayType', 'textRotation'):
            if getattr(self, a) is not None:
                p[a] = _extract_props(getattr(self, a))
        return p

    def affected_fields(self, prefix):
        fields = []
        for a in (
            'number_format', 'backgroundColor', 'borders', 'padding', 
            'horizontalAlignment', 'verticalAlignment', 'wrapStrategy', 
            'textDirection', 'textFormat', 'hyperlinkDisplayType', 'textRotation'):
            if getattr(self, a) is not None:
                fields.extend( _extract_fieldrefs(a, getattr(self, a), prefix) )
        return fields


class NumberFormat(CellFormatComponent):
    TYPES = {'TEXT', 'NUMBER', 'PERCENT', 'CURRENCY', 'DATE', 'TIME', 'DATE_TIME', 'SCIENTIFIC'}

    def __init__(self, type, pattern=None):
        if type.upper() not in TYPES:
            raise ValueError("NumberFormat.type must be one of: %s" % TYPES)
        self.type = type.upper()
        self.pattern = pattern

    def to_props(self):
        p = { 'type': self.type }
        if self.pattern:
            p['pattern'] = self.pattern
        return p

    def affected_fields(self, prefix):
        fields = []
        fields.extend( _extract_fieldrefs('type', self.type, prefix) )
        fields.extend( _extract_fieldrefs('pattern', self.pattern, prefix) )
        return fields

class Color(CellFormatComponent):
    def __init__(self, red, green, blue, alpha=None):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    def to_props(self):
        p = { 'red': self.red, 'blue': self.blue, 'green': self.green }
        if self.alpha is not None:
            p['alpha'] = self.alpha
        return p

    def affected_fields(self, prefix):
        fields = []
        for a in ('red', 'green', 'blue', 'alpha'):
            if getattr(self, a) is not None:
                fields.extend( _extract_fieldrefs(a, getattr(self, a), prefix) )
        return fields

class Borders(CellFormatComponent):
    def __init__(self, top=None, bottom=None, left=None, right=None):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    def to_props(self):
        p = {}
        for a in ('top', 'bottom', 'left', 'right'):
            if getattr(self, a) is not None:
                p[a] = _extract_props(getattr(self, a))
        return p

    def affected_fields(self, prefix):
        fields = []
        for a in ('top', 'bottom', 'left', 'right'):
            if getattr(self, a) is not None:
                fields.extend( _extract_fieldrefs(a, getattr(self, a), prefix) )
        return fields

class Border(CellFormatComponent):
    STYLES = {'DOTTED', 'DASHED', 'SOLID', 'SOLID_MEDIUM', 'SOLID_THICK', 'NONE', 'DOUBLE'}

    def __init__(self, style, color):
        if style.upper() not in STYLES:
            raise ValueError("Border.style must be one of: %s" % STYLES)
        self.style = style.upper()
        self.color = color

    def to_props(self):
        p = { 'style': self.style }
        if self.color:
            p['color'] = _extract_props(self.color)
        return p

    def affected_fields(self, prefix):
        fields = []
        for a in ('style', 'color'):
            if getattr(self, a) is not None:
                fields.extend( _extract_fieldrefs(a, getattr(self, a), prefix) )
        return fields

class Padding(CellFormatComponent):
    def __init__(self, top=None, right=None, bottom=None, left=None):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

    def to_props(self):
        p = {}
        for a in ('top', 'right', 'bottom', 'left'):
            if getattr(self, a) is not None:
                p[a] = getattr(self, a)
        return p

    def affected_fields(self, prefix):
        fields = []
        for a in ('top', 'right', 'bottom', 'left'):
            if getattr(self, a) is not None:
                fields.extend( _extract_fieldrefs(a, getattr(self, a), prefix) )
        return fields

class TextFormat(CellFormatComponent):
    def __init__(self, 
        foregroundColor=None, 
        fontFamily=None, 
        fontSize=None, 
        bold=None, 
        italic=None, 
        strikethrough=None, 
        underline=None
        ):
        self.foregroundColor = foregroundColor
        self.fontFamily = fontFamily
        self.fontSize = fontSize
        self.bold = bold
        self.italic = italic
        self.strikethrough = strikethrough
        self.underline = underline

    def to_props(self):
        p = {}
        for a in ('foregroundColor', 'fontFamily', 'fontSize', 'bold', 'italic', 'strikethrough', 'underline'):
            if getattr(self, a) is not None:
                p[a] = _extract_props(getattr(self, a))
        return p

    def affected_fields(self, prefix):
        fields = []
        for a in ('foregroundColor', 'fontFamily', 'fontSize', 'bold', 'italic', 'strikethrough', 'underline'):
            if getattr(self, a) is not None:
                fields.extend( _extract_fieldrefs(a, getattr(self, a), prefix) )
        return fields

class TextRotation(CellFormatComponent):
    def __init__(self, angle=None, vertical=None):
        if len([expr for expr in (angle is not None, vertical is not None) if expr]) != 1:
            raise ValueError("Either angle or vertical must be specified, not both or neither")
        self.angle = angle
        self.vertical = vertical

    def to_props(self):
        return { 'angle': self.angle } if self.angle is not None else { 'vertical': self.vertical }

    def affected_fields(self, prefix):
        fields = []
        for a in ('angle', 'vertical'):
            if getattr(self, a) is not None:
                fields.extend( _extract_fieldrefs(a, getattr(self, a), prefix) )
        return fields

for _c in [ obj for name, obj in locals().items() if isinstance(obj, type) and issubclass(obj, CellFormatComponent) ]:
    locals()[_underlower(_c.__name__)] = _c

