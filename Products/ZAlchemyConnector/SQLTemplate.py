# -*- coding: utf-8 -*-
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS import SimpleItem
from OFS.Folder import Folder
from .Query import Query


class SQLTemplate(SimpleItem.SimpleItem, Folder):
    """Template for SQLs w/ PageTemplate."""

    def __init__(
            self, path, id, get_wrapper=None, args=None, id_macros=None,
            count=None, debug=0):
        """Constructor.

        var path: PATH to the SQL file.
        var id: ID to the SQL file for rendering and Query execution.
        var get_wrapper: AlchemyConnectors' Wrapper for execute query.

        var args: Arguments to be sent to Query for execution.
        Also set arg as an attribute in class escope to be able to
        make conditions with PageTemplate.
        Example:
            - Expects a list of args with which argument in a dictionary.
            {
                "type": "int",
                "key": "argument_1",
                "value": 1,
                "ignore_alchemy": False

                // ignore_alchemy: ignore arg in both methods:
                    - get_args_as_to_query
                    - get_args_as_to_exec
            }

        Optionals:
        var macros: ZPT instance with macros for SQL. (Optional)
        var  count: Define if query is to be groupped by COUNT or not.
        var  debug: Simply prints query before rendering.
        """
        self.id = id
        self.path = path
        self._get_wrapper = get_wrapper

        self.count = count
        self.debug = debug
        self.id_macros = id_macros
        self.args = {}

        if args:
            self.set_args(args)

    def is_debug(self):
        """Check if debug flag is on."""
        if self.debug:
            return True
        return False

    def _guess_type(self, val):
        if isinstance(val, int):
            return "int"
        elif isinstance(val, float):
            return "float"
        elif isinstance(val, str):
            return "string"

    def set_args(self, argumentos=None):
        """Set arguments into class escope as variables."""
        if argumentos and isinstance(argumentos, list):
            for arg in argumentos:
                if arg["key"] not in list(self.args.keys()):
                    if arg["type"] == "list":

                        # If list, add in args dictionary and iterate each
                        # item from the list to also add it in args so it is
                        # possible to check, render and pass it to Query as
                        # an individual argument.
                        self.args[arg["key"]] = arg

                        if arg["value"] and isinstance(arg["value"], list):
                            for index, item_l in enumerate(arg["value"]):
                                for item_d in item_l.items():
                                    key = item_d[0]
                                    val = item_d[1]

                                    _key_fmt = "{}_{}".format(key, index)
                                    self.args[_key_fmt] = {
                                        "type": self._guess_type(val),
                                        "key": _key_fmt,
                                        "value": val
                                    }
                    else:
                        self.args[arg["key"]] = arg

    def get_args_as_to_query(self):
        """Return args formatted in a list of dictionaries."""
        if self.args:
            return [
                v for v in list(self.args.values())
                if v["value"] is not None and
                v["type"] not in ('list',) and
                v.get("ignore_alchemy", False) is False
            ]

    def get_args_as_to_exec(self):
        """Return args formatted in dictionary to Query for execution."""
        if self.args:
            return {k: v["value"] for k, v in list(self.args.items())
                    if v["value"] is not None and
                    v["type"] not in ('list',) and
                    v.get("ignore_alchemy", False) is False}
        return None

    def get(self, arg):
        """Return args' value from list of args."""
        return self.args.get(arg)['value']

    def check(self, arg):
        """Check arg.

        Verify as an argument from args or as attribute in class' escope.
        """
        # First verify if is an argument by looking in args list.
        # Then verify if value is anything different from None.
        if self.args:
            if self.args.get(arg) and arg in list(self.args.keys()):
                if self.args[arg].get('value', None):
                    return True
                else:
                    return False

        # If not found in args list, verifies if it's a condition
        # in a referenced attribute in class escope.
        if hasattr(self, arg):
            return self._check_condition(arg)

        return False

    def render(self, arg):
        """Verify arg to render."""
        if self.args:
            if self.args.get(arg) and arg in list(self.args.keys()):
                _value = self.args[arg].get('value', None)
                if _value:
                    return """{}""".format(_value)
                else:
                    return """"""

        # If not found in args list, verifies if it's a condition
        # in a referenced attribute in class' escope.
        if hasattr(self, arg):
            _cond = self._check_condition(arg)
            if type(_cond) == bool:
                return """{}""".format(int(_cond))

            return """{}""".format(_cond)

        return """"""

    def set_condition(self, id, instance):
        """Set condition in class' escope."""
        if not hasattr(self, id):
            setattr(self, id, instance)
        else:
            raise Exception('condition already exists.')

    def _check_condition(self, id):
        """Return condition."""
        if hasattr(self, id):
            cond = getattr(self, id)
            if callable(cond):
                return cond()
            return cond

        return False

    def get_macro(self, id):
        """Return macro if exists."""
        if self.id_macros:
            self._sql_macros = PageTemplateFile(
                self.path + self.id_macros, globals())
            return self._sql_macros.macros[id]

        return

    def count(self):
        """Verify if query should group by count."""
        if self.count:
            return True
        return False

    def not_count(self):
        """Verify if query should NOT group by count."""
        if not self.count:
            return True
        return False

    def render_template(self):
        """Render PageTemplate."""
        # re.sub(r'--\s+.*', '', file)

        self._page_template = PageTemplateFile(self.path + self.id, globals())
        sql_rendered = self._page_template()
        sql_rendered = sql_rendered.strip()

        if self.is_debug():
            print(sql_rendered)

        return sql_rendered

    def query(self):
        """Execute Query."""
        if not self._get_wrapper:
            raise Exception('Wrapper not configured.')

        _query = Query(
            id=self.id,
            get_wrapper=self._get_wrapper,
            template=self.render_template(),
            arguments=self.get_args_as_to_query()
        )

        return _query(**self.get_args_as_to_exec()).dictionaries()
