from sqlalchemy import TypeDecorator, UnicodeText, String
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.dialects import postgresql  # INET
import json


class JSONEncodedDict(TypeDecorator):
    impl = UnicodeText

    def process_bind_param(self, value, dialect):
        if value:
            return json.dumps(value)
        else:
            return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        else:
            return dict()


class MutableDict(Mutable, dict):
    @classmethod
    def coerce(cls, key, value):
        "Convert plain dictionaries to MutableDict."

        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        "Detect dictionary set events and emit change events."

        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        "Detect dictionary del events and emit change events."

        dict.__delitem__(self, key)
        self.changed()


class INETWrapper(TypeDecorator):
    impl = String

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.INET())
        else:
            return dialect.type_descriptor(String())

