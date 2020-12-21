# SPDX-License-Identifier: MIT
from OFS.SimpleItem import SimpleItem
from z3c.sqlalchemy import createSAWrapper
from z3c.sqlalchemy import getSAWrapper
from z3c.sqlalchemy.interfaces import ISQLAlchemyWrapper
from uuid import uuid4


z3c_registry = {}


def register_z3c(name, wrapper):
    """Insert """
    z3c_registry[name] = wrapper


def lookup_entry(name):
    """."""
    da = z3c_registry.get(name)
    if not da:
        raise LookupError("No instance registered under name " + name)
    return da


def clear_sa_wrapper_registry():
    """."""
    global z3c_registry
    z3c_registry = {}


class Wrapper(SimpleItem):
    """."""

    meta_type = "SQLAlchemy Wrapper"
    zmi_icon = "fas fa-database"
    transactional = True
    _isAnSQLConnection = True

    def __init__(self, id, dsn, engine_options=None):
        """."""
        self.id = id
        self.dsn = dsn
        self.engine_options = engine_options and engine_options or ()

        self._new_utilid()
        wrapper = self.get_wrapper()
        if wrapper:
            register_z3c(self.id, wrapper)

    def __call__(self, *args, **kv):
        """."""
        return self

    @property
    def engine_options_dict(self):
        """."""
        engine_options = dict(self.engine_options)
        return engine_options

    def edit(self, dsn, engine_options=None):
        """."""
        if dsn != self.dsn:
            self.dsn = dsn
            self._p_changed = 1

        if engine_options:
            self.engine_options = engine_options
            self._p_changed = 1

        if self._p_changed == 1:
            self._recreate()

        return

    def _recreate(self):
        """."""
        try:
            from zope.component import unregisterUtility
            unregisterUtility(name=self.util_id)
            self._new_utilid()
        except ImportError:
            try:
                from zope.app import zapi
                from zope.component.servicenames import Utilities
                s = zapi.getGlobalServices().getService(Utilities)
                s.register((), ISQLAlchemyWrapper, self.util_id, None)
                self._new_utilid()
            except Exception:
                self._new_utilid()

    def _new_utilid(self):
        """Assign a new unique utility ID."""
        self.util_id = str(uuid4())

    def get_wrapper(self):
        """."""
        wrapper = self._create_sa_wrapper()
        if wrapper is not None:
            return wrapper
        else:
            try:
                return lookup_entry(self.id)
            except LookupError:
                return None

    def _create_sa_wrapper(self):
        """."""
        try:
            wrapper = getSAWrapper(self.util_id)
        except ValueError:
            try:
                if self.util_id is None:
                    self._new_utilid()

                wrapper = createSAWrapper(
                    self.dsn,
                    forZope=True,
                    transactional=True,
                    extension_options={'initial_state': 'invalidated'},
                    engine_options=self.engine_options_dict,
                    name=self.util_id)

                register_z3c(self.id, wrapper)
            except ValueError:
                try:
                    wrapper = getSAWrapper(self.util_id)
                except LookupError:
                    wrapper = lookup_entry(self.id)
                except Exception:
                    wrapper = None

        return wrapper
