from aiohttp import web


async def close_db(app: web.Application) -> None:
    await app['db'].pop_bind().close()
