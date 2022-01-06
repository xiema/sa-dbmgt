import json

from sqlalchemy.ext.declarative import DeferredReflection, declared_attr, declarative_base
from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy import types
from .config import TABLENAME_OVERRIDES


def create_base(model_base=None):
    if model_base is None:
        model_base = declarative_base()

    class _Base(DeferredReflection, model_base):
        __abstract__ = True
        __reprstr__ = None

        def __init__(self, **kwargs):
            for key, column in type(self).__table__.columns.items():
                assert isinstance(column, Column)
                if key in kwargs:
                    if isinstance(kwargs[key], column.type.python_type) or kwargs[key] is None:
                        setattr(self, key, kwargs[key])
                    else:
                        raise TypeError(f"{key} is not of type {column.type.python_type} (is {kwargs[key]})")

        def __repr__(self):
            reprstr = getattr(type(self), '__reprstr__', f"<{type(self).__name__} {self.get_primary_key_value()}>")
            return reprstr.format_map(self.to_dict())

        def to_dict(self):
            d = {}
            for key in self.__table__.columns.keys():
                d[key] = self.__dict__.get(key, None)
            return d

        def update(self, **kwargs):
            changes = {}
            for key, column in type(self).__table__.columns.items():
                assert isinstance(column, Column)
                if key in kwargs:
                    if isinstance(kwargs[key], column.type.python_type) or (kwargs[key] is None and column.nullable):
                        oldval = getattr(self, key)
                        if oldval != kwargs[key]:
                            changes[key] = (oldval, kwargs[key])
                            setattr(self, key, kwargs[key])
                    else:
                        raise TypeError(f"{key} is not of type {column.type.python_type} (is {kwargs[key]})")
            if changes:
                self.query.filter_by(**{self.get_primary_key(): self.get_primary_key_value()})\
                    .update({k: v[1] for k, v in changes.items()})
            return changes

        def get_primary_key(self):
            for key, column in type(self).__table__.columns.items():
                if column.primary_key:
                    return key

        def get_primary_key_value(self):
            return getattr(self, self.get_primary_key())

    return _Base


Base = create_base(declarative_base())


class TableDefinition(Base):
    _type_map = {n: getattr(types, n) for n in types.__all__}

    __tablename__ = TABLENAME_OVERRIDES.get(__name__.rpartition('.')[2], 'table_definitions')
    id = Column(Integer, primary_key=True)
    tablename = Column(String, nullable=False)
    classname = Column(String, nullable=False)
    columns = Column(JSON, nullable=False)
    reprstr = Column(String, nullable=True)

    def __repr__(self):
        return f"<TableDefinition {self.id}: {self.tablename} {self.classname} {self.columns}>"

    def to_model(self, model_base=None):
        ns = {
            '__tablename__': self.tablename,
            '__reprstr__': self.reprstr,
        }
        for k, v in self.columns.items():
            ns[k] = TableDefinition.create_column(**v)
        cls = type(self.classname, (model_base or Base,), ns)
        return cls

    @staticmethod
    def create_column(**args):
        return Column(
            TableDefinition._type_map[args['type']],
            primary_key=args.get('primary_key', False),
            nullable=args['nullable']
        )

    @staticmethod
    def from_model(model: Base):
        d = {}
        for k, v in model.__table__.columns.items():
            assert (isinstance(v, Column))
            d[k] = {
                'type': type(v.type).__name__,
                'primary_key': v.primary_key,
                'nullable': v.nullable,
            }
        return TableDefinition(
            tablename=model.__tablename__,
            classname=model.__name__,
            columns=d,
            reprstr=model.__reprstr__,
        )
