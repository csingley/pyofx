# vim: set fileencoding=utf-8
""" Extended SQLAlchemy column types """

# stdlib imports
import decimal

# 3rd party imports
import sqlalchemy

# local imports
import ofxtools.types


class Numeric(sqlalchemy.types.TypeDecorator):
    """
    Stores Decimal as String on sqlite, which doesn't have a NUMERIC type
    and by default stores Decimal as float, leading to rounding errors
    """
    impl = sqlalchemy.types.Numeric

    def load_dialect_impl(self, dialect):
        if dialect.name == 'sqlite':
            return dialect.type_descriptor(sqlalchemy.types.CHAR(32))
        else:
            return dialect.type_descriptor(sqlalchemy.types.Numeric)

    def process_bind_param(self, value, dialect):
        if dialect.name == 'sqlite':
            if value:
                return str(value)
            else:
                return ''
        elif value:
            # Handle Euro-style decimal separators (comma)
            try:
                value = decimal.Decimal(value)
            except decimal.InvalidOperation:
                if isinstance(value, basestring):
                    value = decimal.Decimal(value.replace(',', '.'))
                else:
                    raise

            return value

    def process_result_value(self, value, dialect):
        if value == 0:
            return decimal.Decimal('0')
        elif value:
            return decimal.Decimal(value)


class OFXDateTime(sqlalchemy.types.TypeDecorator):
    """ """
    impl = sqlalchemy.types.DateTime

    def process_bind_param(self, value, dialect):
        return ofxtools.types.DateTime.convert(value)

    def process_result_param(self, value, dialect):
        pass


class OFXBoolean(sqlalchemy.types.TypeDecorator):
    """ """
    impl = sqlalchemy.types.Boolean
    mapping = {'Y': True, 'N': False}
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return self.mapping[value]

    def process_result_param(self, value, dialect):
        pass
