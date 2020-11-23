# SPDX-License-Identifier: MIT
from OFS.SimpleItem import SimpleItem
from z3c.sqlalchemy import createSAWrapper
from z3c.sqlalchemy import getSAWrapper
from z3c.sqlalchemy.interfaces import ISQLAlchemyWrapper
from uuid import uuid4


_wrapper_registry = {}


def register_sa_wrapper(name, wrapper):
    """."""
    _wrapper_registry[name] = wrapper


def deregister_sa_wrapper(name):
    """."""
    _wrapper_registry.pop(name, None)


def lookup_sa_wrapper(name):
    """."""
    da = _wrapper_registry.get(name)
    if not da:
        raise LookupError(
            "No SAWrapper instance registered under name " + name)
    return da


def clear_sa_wrapper_registry():
    """Completely empty out the registry of `SAWrapper` instances."""
    global _wrapper_registry
    _wrapper_registry = {}


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
        wrapper = self.sa_zope_wrapper()
        if wrapper:
            register_sa_wrapper(self.id, wrapper)

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

    def sa_zope_wrapper(self):
        """."""
        wrapper = self._supply_z3c_sa_wrapper()
        if wrapper is not None:
            return wrapper
        else:
            try:
                return lookup_sa_wrapper(self.id)
            except LookupError:
                return None

    def _supply_z3c_sa_wrapper(self):
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

                register_sa_wrapper(self.id, wrapper)
            except ValueError:
                try:
                    wrapper = getSAWrapper(self.util_id)
                except LookupError:
                    wrapper = lookup_sa_wrapper(self.id)
                except Exception:
                    wrapper = None

        return wrapper

    def get_wrapper(self):
        """."""
        return self.sa_zope_wrapper()
