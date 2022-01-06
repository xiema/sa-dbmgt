from typing import MutableSequence
from textwrap import dedent

from sqlalchemy.engine import Engine
from .models import Base, TableDefinition, create_base

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base, DeferredReflection, DeclarativeMeta
from sqlalchemy.orm.decl_api import registry
from typing import Union, Optional


class DatabaseHandler:
    def __init__(self, filename: str, model_base: DeferredReflection = None, autoconnect: bool = True):
        self.filename = filename
        self.model_base: Union[registry, DeferredReflection] = model_base
        self.engine: Optional[Engine] = None
        self.session: Optional[scoped_session] = None
        self.connected = False
        if autoconnect:
            self.connect()
        else:
            self.connected = False

    def connect(self):
        self.engine = create_engine(self.filename)
        self.session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))
        self.connected = True
        if self.model_base is not None:
            self.model_base.metadata.create_all(bind=self.engine)
            self.model_base.query = self.session.query_property()
            self.model_base.prepare(self.engine)

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def close(self):
        self.engine.dispose()
        self.session.remove()
        self.engine = None
        self.session = None
        self.connected = False

    def __enter__(self):
        if not self.connected:
            self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.connected:
            self.close()


def load_tabledefs(db_name: str):
    with DatabaseHandler(db_name, Base) as db:
        tds: MutableSequence[TableDefinition] = TableDefinition.query.all()
    return tds


def load_models(tabledefs: MutableSequence[TableDefinition] = None, db_name: str = None):
    if tabledefs is None:
        tabledefs = load_tabledefs(db_name)
    ret = {}
    model_base = create_base(declarative_base())
    ret[model_base.__name__] = model_base
    for td in tabledefs:
        model = td.to_model(model_base)
        ret[model.__name__] = model
    return ret


def generate_class_definition(tabledef: TableDefinition):
    s = f"""\


    class {tabledef.classname}(Base):
        pass
    """
    return dedent(s)
