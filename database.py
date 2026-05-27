import aiosqlite

class Database:
    def __init__(self, db_file="bot_database.db"):
        self.db_file = db_file

    async def create_tables(self):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    name TEXT
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS preview (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    photo_file_id TEXT,
                    order_index INTEGER
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS wishlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    photo_file_id TEXT,
                    caption_text TEXT,
                    order_index INTEGER
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT,
                    photo_file_id TEXT
                )
            ''')
            await db.commit()

    async def add_user(self, user_id, name):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)", (user_id, name))
            await db.commit()

    async def get_user(self, user_id):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                return await cursor.fetchone()

    async def add_review(self, text, photo_file_id):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("INSERT INTO reviews (text, photo_file_id) VALUES (?, ?)", (text, photo_file_id))
            await db.commit()

    async def get_random_review(self):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT text, photo_file_id FROM reviews ORDER BY RANDOM() LIMIT 1") as cursor:
                return await cursor.fetchone()

    async def add_preview(self, photo_file_id, order_index):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("INSERT INTO preview (photo_file_id, order_index) VALUES (?, ?)", (photo_file_id, order_index))
            await db.commit()

    async def get_all_preview(self):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT photo_file_id, order_index FROM preview ORDER BY order_index") as cursor:
                return await cursor.fetchall()

    async def delete_preview(self, order_index):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("DELETE FROM preview WHERE order_index = ?", (order_index,))
            await db.commit()

    async def add_wishlist(self, photo_file_id, caption_text, order_index):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("INSERT INTO wishlist (photo_file_id, caption_text, order_index) VALUES (?, ?, ?)", (photo_file_id, caption_text, order_index))
            await db.commit()

    async def get_all_wishlist(self):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT photo_file_id, caption_text, order_index FROM wishlist ORDER BY order_index") as cursor:
                return await cursor.fetchall()

    async def delete_wishlist(self, order_index):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("DELETE FROM wishlist WHERE order_index = ?", (order_index,))
            await db.commit()

    async def get_max_order_index(self, table_name):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute(f"SELECT MAX(order_index) FROM {table_name}") as cursor:
                row = await cursor.fetchone()
                return row[0] if row[0] is not None else 0
