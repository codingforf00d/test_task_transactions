from aiohttp import web


async def init_db(app: web.Application):
    db = app['db']
    await db.set_bind(app['config'].DATABASE_URI)

    await db.gino.create_all(checkfirst=True)
