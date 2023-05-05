import aiosqlite

async def db_create():
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('CREATE TABLE IF NOT EXISTS main (channel_id INTEGER , guild_id INTEGER)')
        await db.commit()

async def get_guild_ids():
    guild_ids = []
    async with aiosqlite.connect('main.db') as db:
        async with db.execute('SELECT guild_id, channel_id FROM main WHERE channel_id IS NOT NULL') as cursor:
            async for row in cursor:
                guild_ids.append((row[0], row[1]))
    return guild_ids

async def add_guild(guild_id: int): 
    async with aiosqlite.connect('main.db') as db:
        async with db.execute('SELECT guild_id FROM main WHERE guild_id = ?', (guild_id.id,)) as cursor:
            result = await cursor.fetchone()
            if result is None:
                await db.execute('INSERT INTO main(guild_id, channel_id) VALUES(?, ?)', (guild_id.id, None))
            await db.commit()

async def get_channel_id(guild_id):
    if isinstance(guild_id, tuple):
        guild_id = str(guild_id[0])
    else:
        guild_id = str(guild_id)
    async with aiosqlite.connect('main.db') as db:
        async with db.execute('SELECT channel_id FROM main WHERE guild_id = ?', (guild_id,)) as cursor:
            result = await cursor.fetchone()
            if result is None:
                return None
            else:
                return result[0]
