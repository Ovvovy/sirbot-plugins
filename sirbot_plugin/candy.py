import logging

from sirbot.plugin import Plugin
from sirbot.hookimpl import hookimpl

logger = logging.getLogger('sirbot.candy')


@hookimpl
def plugins(loop):
    return 'candy', CandyPlugin(loop)


class CandyPlugin(Plugin):
    __name__ = 'candy'
    __version__ = '0.0.1'

    def __init__(self, loop):
        super().__init__(loop)
        self._started = False
        self._facades = None

    async def configure(self, config, router, session, facades):
        self._facades = facades

    async def start(self):
        await self._create_db_table()
        self._started = True

    def facade(self):
        return CandyFacade()

    @property
    def started(self):
        return self._started

    async def _create_db_table(self):
        db = self._facades.get('database')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS candy (
            user TEXT PRIMARY KEY NOT NULL,
            candy INT DEFAULT 0
            )
            ''')
        await db.execute('''
            INSERT OR REPlACE INTO metadata (plugin, version) VALUES (?, ?)''', (self.__name__, self.__version__))
        await db.commit()

    async def database_update(self, metadata, db):
        # Example for database update
        #
        # if metadata['version'] == '0.0.1':
        #     await db.execute('''ALTER TABLE candy ADD COLUMN test TEXT''')
        #     metadata['version'] = '0.0.2'
        #
        # return metadata['version']
        pass


class CandyFacade:
    def __init__(self):
        pass

    async def add(self, user, count=1, *, db):
        await db.execute('''SELECT candy FROM candy WHERE user = ? ''', (user, ))
        value = await db.fetchone()
        if value:
            value = value['candy'] + count
        else:
            value = count

        await db.execute('''INSERT OR REPLACE INTO candy (user, candy) VALUES (?, ?)''', (user, value))
        return value

    async def top(self, count, *, db):
        await db.execute('''SELECT * FROM candy ORDER BY candy DESC LIMIT ?''', (count, ))
        data = await db.fetchall()
        return data