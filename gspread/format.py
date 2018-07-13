# -*- coding: utf-8 -*-

import re

def _props_to_component(class_alias, value):
    if class_alias not in _CLASSES:
        raise ValueError("No format component named '%s'" % class_alias)
    kwargs = {}
    for k, v in value.items():
        if isinstance(v, dict):
            v = _props_to_component(k, v)
        kwargs[k] = v
    return _CLASSES[class_alias](**kwargs)

def _ul_repl(m):
    return '_' + m.group(1).lower()

def _underlower(name):
    return name[0].lower() + name[1:]

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
    _FIELDS = ()

    @classmethod
    def from_props(cls, props):
        return _props_to_component(_underlower(cls.__name__), props)

    def __repr__(self):
        return '<' + self.__class__.__name__ + ' ' + str(self) + '>'

    def __str__(self):
        p = []
        for a in self._FIELDS:
            v = getattr(self, a)
            if v is not None:
                if isinstance(v, CellFormatComponent):
                    p.append( (a, "(" + str(v) + ")") )
                else:
                    p.append( (a, str(v)) )
        return ";".join(["%s=%s" % (k, v) for k, v in p])

    def to_props(self):
        p = {}
        for a in self._FIELDS:
            if getattr(self, a) is not None:
                p[a] = _extract_props(getattr(self, a))
        return p

    def affected_fields(self, prefix):
        fields = []
        for a in self._FIELDS:
            if getattr(self, a) is not None:
                fields.extend( _extract_fieldrefs(a, getattr(self, a), prefix) )
        return fields

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        for a in self._FIELDS:
            self_v = getattr(self, a, None)
            other_v = getattr(other, a, None)
            if self_v != other_v:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def add(self, other):
        new_props = {}
        for a in self._FIELDS:
            self_v = getattr(self, a, None)
            other_v = getattr(other, a, None)
            if isinstance(self_v, CellFormatComponent):
                this_v = self_v.add(other_v)
            elif other_v is not None:
                this_v = other_v
            else:
                this_v = self_v
            if this_v is not None:
                new_props[a] = _extract_props(this_v)
        return self.__class__.from_props(new_props)

    __add__ = add

    def intersection(self, other):
        new_props = {}
        for a in self._FIELDS:
            self_v = getattr(self, a, None)
            other_v = getattr(other, a, None)
            this_v = None
            if isinstance(self_v, CellFormatComponent):
                this_v = self_v.intersection(other_v)
            elif self_v == other_v:
                this_v = self_v
            if this_v is not None:
                new_props[a] = _extract_props(this_v)
        return self.__class__.from_props(new_props) if new_props else None

    __and__ = intersection

    def difference(self, other):
        new_props = {}
        for a in self._FIELDS:
            self_v = getattr(self, a, None)
            other_v = getattr(other, a, None)
            this_v = None
            if isinstance(self_v, CellFormatComponent):
                this_v = self_v.difference(other_v)
            elif other_v != self_v:
                this_v = self_v
            if this_v is not None:
                new_props[a] = _extract_props(this_v)
        return self.__class__.from_props(new_props) if new_props else None

    __sub__ = difference

class CellFormat(CellFormatComponent):
    _FIELDS = (
        'numberFormat', 'backgroundColor', 'borders', 'padding', 
        'horizontalAlignment', 'verticalAlignment', 'wrapStrategy', 
        'textDirection', 'textFormat', 'hyperlinkDisplayType', 'textRotation'
    )

    def __init__(self, 
        numberFormat=None,
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
        self.numberFormat = numberFormat
        self.backgroundColor = backgroundColor
        self.borders = borders
        self.padding = padding
        self.horizontalAlignment = _parse_string_enum('horizontalAlignment', horizontalAlignment, set(['LEFT', 'CENTER', 'RIGHT']))
        self.verticalAlignment = _parse_string_enum('verticalAlignment', verticalAlignment, set(['TOP', 'MIDDLE', 'BOTTOM']))
        self.wrapStrategy = _parse_string_enum('wrapStrategy', wrapStrategy, set(['OVERFLOW_CELL', 'LEGACY_WRAP', 'CLIP', 'WRAP']))
        self.textDirection = _parse_string_enum('textDirection', textDirection, set(['LEFT_TO_RIGHT', 'RIGHT_TO_LEFT']))
        self.textFormat = textFormat
        self.hyperlinkDisplayType = _parse_string_enum('hyperlinkDisplayType', hyperlinkDisplayType, set(['LINKED', 'PLAIN_TEXT']))
        self.textRotation = textRotation

class NumberFormat(CellFormatComponent):
    _FIELDS = ('type', 'pattern')

    TYPES = set(['TEXT', 'NUMBER', 'PERCENT', 'CURRENCY', 'DATE', 'TIME', 'DATE_TIME', 'SCIENTIFIC'])

    def __init__(self, type, pattern=None):
        if type.upper() not in TYPES:
            raise ValueError("NumberFormat.type must be one of: %s" % TYPES)
        self.type = type.upper()
        self.pattern = pattern

class Color(CellFormatComponent):
    _FIELDS = ('red', 'green', 'blue', 'alpha')

    def __init__(self, red=None, green=None, blue=None, alpha=None):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

class Borders(CellFormatComponent):
    _FIELDS = ('top', 'bottom', 'left', 'right')

    def __init__(self, top=None, bottom=None, left=None, right=None):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

class Border(CellFormatComponent):
    _FIELDS = ('style', 'color')

    STYLES = set(['DOTTED', 'DASHED', 'SOLID', 'SOLID_MEDIUM', 'SOLID_THICK', 'NONE', 'DOUBLE'])

    def __init__(self, style, color):
        if style.upper() not in STYLES:
            raise ValueError("Border.style must be one of: %s" % STYLES)
        self.style = style.upper()
        self.color = color

class Padding(CellFormatComponent):
    _FIELDS = ('top', 'right', 'bottom', 'left')

    def __init__(self, top=None, right=None, bottom=None, left=None):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

class TextFormat(CellFormatComponent):
    _FIELDS = ('foregroundColor', 'fontFamily', 'fontSize', 'bold', 'italic', 'strikethrough', 'underline')

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

class TextRotation(CellFormatComponent):
    _FIELDS = ('angle', 'vertical')

    def __init__(self, angle=None, vertical=None):
        if len([expr for expr in (angle is not None, vertical is not None) if expr]) != 1:
            raise ValueError("Either angle or vertical must be specified, not both or neither")
        self.angle = angle
        self.vertical = vertical

# provide camelCase aliases for all component classes.

_CLASSES = {}
for _c in [ obj for name, obj in locals().items() if isinstance(obj, type) and issubclass(obj, CellFormatComponent) ]:
    _k = _underlower(_c.__name__)
    _CLASSES[_k] = _c
    locals()[_k] = _c
_CLASSES['foregroundColor'] = Color
_CLASSES['backgroundColor'] = Color

