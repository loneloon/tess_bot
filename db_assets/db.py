from sqlalchemy import create_engine, Table, Column, Integer, \
    String, MetaData, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


class WebsiteDB:

    def __init__(self, db_name, model_class, preload=None):
        self.db_engine = create_engine(db_name, echo=False, pool_recycle=7200)

        self.metadata = MetaData()

        Base = declarative_base()

        for model in model_class.get_inner_classes():
            self.create_db_table(model)
            self.map_model(Base, model)

        self.metadata.create_all(self.db_engine)

        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()
        self.session.commit()

        self.preload = True if preload else False

        if self.preload:
            self.preload_objects()

    @staticmethod
    def compose_table(model_name, model_attrs, metadata):
        columns = []

        for key in model_attrs:

            if key == 'id':
                columns.append(Column(key, Integer, primary_key=True))
            elif key == 'email' or \
                    key == 'cookie':
                columns.append(Column(key, String, unique=True))
            elif 'parent' in key:
                columns.append(Column(key, Integer, default=None))
            elif 'is_' in key:
                columns.append(Column(key, Boolean, default=True))
            elif 'date' in key:
                columns.append(Column(key, DateTime))
            elif 'fk' in key:
                columns.append(Column(key,
                                      ForeignKey(key.split("_")[0].capitalize() + ".id")))
            else:
                columns.append(Column(key, String))
        return Table(model_name, metadata, *columns)

    def create_db_table(self, model):
        self.__setattr__(model.__name__.lower() + '_table',
                         self.compose_table(model.__name__, model.__slots__, self.metadata))

    def map_model(self, class_base, model):
        self.__setattr__(
            model.__name__.lower() + "_class",
            type(model.__name__.lower(), (class_base,),
                 {"__table__": self.__getattribute__(model.__name__.lower() + '_table'),
                  "preloaded": []}))

    def create_object(self, model, **kwargs):
        try:
            obj_model = self.__getattribute__(model.__name__.lower() + '_class')

            instance = obj_model(**kwargs)
            self.session.add(instance)
            self.session.commit()

            if self.preload:
                obj_model.preloaded.append(self.session.query(obj_model).filter_by(**kwargs).first())
            return True
        except Exception as e:
            print(e)
            return False

    def get_object(self, model, all=None, **kwargs):
        try:
            obj_model = self.__getattribute__(model.__name__.lower()+'_class')
            result = self.session.query(obj_model).filter_by(**kwargs)
            if result.count():
                if not all:
                    return result.first()
                else:
                    return result.all()
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def update_object(self, instance):
        try:
            self.session.add(instance)
            self.session.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def delete_object(self, model, **kwargs):
        try:
            result = self.get_object(model, **kwargs)
            self.session.delete(result)

            self.session.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def preload_objects(self):
        for key, val in self.__dict__.items():
            if key.endswith('_class'):
                val.preloaded.extend(self.session.query(val).all())

    def get_preloaded(self, model):
        result = []

        try:
            obj_model = self.__getattribute__(model.__name__.lower() + '_class')
            result = obj_model.preloaded
        except Exception as e:
            print(e)

        return result
