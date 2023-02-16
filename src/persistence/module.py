import injector

from settings import Settings


class DB:
    def __init__(self, settings: Settings):
        # TODO: initialize connection to database
        self.engine = ...
        self.session_source = ...  # sessionmaker(autocommit=False, autoflush=True,
        # bind=self.engine)
        pass

    def session(self):
        return self.session_source()


class PersistenceModule(injector.Module):

    @injector.provider
    def _db(self, settings: Settings) -> DB:
        return DB(settings)
