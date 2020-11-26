# SPDX-License-Identifier: MIT
from sqlalchemy import types, bindparam
from sqlalchemy.sql import text
from OFS.SimpleItem import SimpleItem
from zope.sqlalchemy import mark_changed
from collections import UserList


class Query(SimpleItem):
    """."""

    def __init__(self, id, get_wrapper, template, max_rows=0, arguments=None):
        """."""
        self.id = id
        self._get_wrapper = get_wrapper
        self._template = text(template)
        self._arguments = arguments and arguments or []
        self._max_rows = max_rows
        self._types = ['string', 'int', 'float']
        self._types_query = {'string': types.String, 'int': types.Integer,
                             'float': types.Float}
        self.__proc_arguments()

    def __call__(self, **kwargs):
        """."""
        params = {}
        for key, value in kwargs.items():
            params[key] = self.__check_type(key=key, value=value)

        session = self._get_wrapper().session
        mark_changed(session)
        response = session.execute(self._template, params)

        if response.returns_rows:
            fields = response.keys()

            if self._max_rows:
                rows = response.fetchmany(self._max_rows)
            else:
                rows = response.fetchall()

            response.close()

            return Results([Row(zip(fields, i)) for i in rows])
        else:
            return Results()

    def __check_type(self, key, value):
        """."""
        _attr = getattr(self, key, None)
        if _attr is None:
            raise QueryParamaterError("Received unexpected argument.")

        if _attr[1] is True:
            _r = []
            if _attr[0] == 'float':
                for i in value:
                    _p = self.__test_float(value=i)
                    if _p is False:
                        raise QueryTypeError(
                            "Invalid value for type %s on %s" % (_attr[0], key)
                        )
                    _r.append(_p)
            elif _attr[0] == 'int':
                for i in value:
                    _p = self.__test_int(value=i)
                    if _p is False:
                        raise QueryTypeError(
                            "Invalid value for type %s on %s" % (_attr[0], key)
                        )
                    _r.append(_p)
            else:
                for i in value:
                    _p = self.__test_string(value=i)
                    if _p is False:
                        raise QueryTypeError(
                            "Invalid value for type %s on %s" % (_attr[0], key)
                        )
                    _r.append(_p)

            return tuple(_r)
        else:
            if _attr[0] == 'float':
                _p = self.__test_float(value=value)
            elif _attr[0] == 'int':
                _p = self.__test_int(value=value)
            else:
                _p = self.__test_string(value=value)

            if _p is False:
                raise QueryTypeError(
                    "Invalid value for type %s on %s" % (_attr[0], key))

            return _p

    def __proc_arguments(self):
        """."""
        for item in self._arguments:
            _type = str(item.get('type', None)).lower()
            _mult = bool(item.get('multiple', None))

            if not _type:
                raise QueryTypeError(
                    "Missing type on '%s'" % item['key'])

            if _type not in self._types:
                raise QueryTypeError(
                    "Invalid type on '%s'" % item['key'])

            self.__setattr__(str(item['key']), (_type, _mult))

            self.__bind(key=str(item['key']), dtype=_type)

    def __bind(self, key, dtype):
        """."""
        _tmp = bindparam(key, type_=self._types_query[dtype])
        self._template = self._template.bindparams(_tmp)

    def __test_int(self, value):
        """."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return False

    def __test_float(self, value):
        """."""
        try:
            return float(value)
        except (ValueError, TypeError):
            return False

    def __test_string(self, value):
        """."""
        try:
            return str(value)
        except (ValueError, TypeError):
            return False


class QueryTypeError(Exception):
    """Type error."""

    def __init__(self, message):
        """."""
        self.message = message

        super(QueryTypeError, self).__init__(self.message)


class QueryParamaterError(Exception):
    """Paramater error."""

    def __init__(self, message):
        """."""
        self.message = message

        super(QueryParamaterError, self).__init__(self.message)


class Results(UserList):
    """."""

    def dictionaries(self):
        """."""
        from copy import copy
        return tuple([copy(i.__dict__) for i in self.data])


class Row(SimpleItem):
    """."""

    def __init__(self, row):
        """."""
        self.__dict__.update(row)
