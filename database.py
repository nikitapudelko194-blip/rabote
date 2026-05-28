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
            
            # === Новые таблицы ===
            await db.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    user_id INTEGER,
                    item_type TEXT CHECK(item_type IN ('preview', 'wishlist')),
                    item_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, item_type, item_id)
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS support_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    message_text TEXT,
                    photo_file_id TEXT,
                    is_from_admin BOOLEAN DEFAULT 0,
                    reply_to_message_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_read BOOLEAN DEFAULT 0
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS referral_codes (
                    user_id INTEGER PRIMARY KEY,
                    code TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER NOT NULL,
                    referred_id INTEGER NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_id) REFERENCES users(user_id),
                    FOREIGN KEY (referred_id) REFERENCES users(user_id)
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS referral_bonuses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    bonus_type TEXT DEFAULT 'signup',
                    amount INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

    async def get_all_reviews(self):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT text, photo_file_id FROM reviews ORDER BY id") as cursor:
                return await cursor.fetchall()

    async def add_preview(self, photo_file_id, order_index):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("INSERT INTO preview (photo_file_id, order_index) VALUES (?, ?)", (photo_file_id, order_index))
            await db.commit()

    async def get_all_preview(self):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT photo_file_id, order_index FROM preview ORDER BY order_index") as cursor:
                return await cursor.fetchall()
                
    async def get_all_preview_with_id(self):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT id, photo_file_id, order_index FROM preview ORDER BY order_index") as cursor:
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
                
    async def get_all_wishlist_with_id(self):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT id, photo_file_id, caption_text, order_index FROM wishlist ORDER BY order_index") as cursor:
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

    # === FAVORITES ===
    async def add_favorite(self, user_id, item_type, item_id):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("INSERT OR IGNORE INTO favorites (user_id, item_type, item_id) VALUES (?, ?, ?)", (user_id, item_type, item_id))
            await db.commit()

    async def remove_favorite(self, user_id, item_type, item_id):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("DELETE FROM favorites WHERE user_id = ? AND item_type = ? AND item_id = ?", (user_id, item_type, item_id))
            await db.commit()

    async def is_favorite(self, user_id, item_type, item_id):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT 1 FROM favorites WHERE user_id = ? AND item_type = ? AND item_id = ?", (user_id, item_type, item_id)) as cursor:
                return await cursor.fetchone() is not None

    async def get_user_favorites(self, user_id, limit, offset):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT item_type, item_id FROM favorites WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?", (user_id, limit, offset)) as cursor:
                return await cursor.fetchall()

    async def count_user_favorites(self, user_id):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT COUNT(*) FROM favorites WHERE user_id = ?", (user_id,)) as cursor:
                return (await cursor.fetchone())[0]

    async def get_preview_by_id(self, item_id):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT photo_file_id FROM preview WHERE id = ?", (item_id,)) as cursor:
                return await cursor.fetchone()

    async def get_wishlist_by_id(self, item_id):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT photo_file_id, caption_text FROM wishlist WHERE id = ?", (item_id,)) as cursor:
                return await cursor.fetchone()

    # === SUPPORT ===
    async def save_support_message(self, user_id, text, photo_id):
        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.execute("INSERT INTO support_messages (user_id, message_text, photo_file_id) VALUES (?, ?, ?)", (user_id, text, photo_id))
            await db.commit()
            return cursor.lastrowid

    async def save_admin_reply(self, user_id, text, reply_to_id):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("INSERT INTO support_messages (user_id, message_text, is_from_admin, reply_to_message_id) VALUES (?, ?, 1, ?)", (user_id, text, reply_to_id))
            await db.commit()

    async def get_unread_messages_for_admin(self):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT id, user_id, message_text, photo_file_id FROM support_messages WHERE is_from_admin = 0 AND is_read = 0 ORDER BY created_at") as cursor:
                return await cursor.fetchall()

    async def get_conversation_with_user(self, user_id):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT is_from_admin, message_text, created_at FROM support_messages WHERE user_id = ? ORDER BY created_at", (user_id,)) as cursor:
                return await cursor.fetchall()

    async def mark_messages_as_read(self, msg_id):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("UPDATE support_messages SET is_read = 1 WHERE id = ?", (msg_id,))
            await db.commit()

    async def get_anonymous_id(self, message_id):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT user_id FROM support_messages WHERE id = ?", (message_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    # === REFERRAL ===
    async def generate_referral_code(self, user_id, code):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("INSERT OR IGNORE INTO referral_codes (user_id, code) VALUES (?, ?)", (user_id, code))
            await db.commit()

    async def get_referral_code(self, user_id):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT code FROM referral_codes WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def validate_referral_code(self, code):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT user_id FROM referral_codes WHERE code = ?", (code,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def save_referral(self, referrer_id, referred_id):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("INSERT OR IGNORE INTO referrals (referrer_id, referred_id) VALUES (?, ?)", (referrer_id, referred_id))
            await db.commit()

    async def is_already_referred(self, user_id):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT 1 FROM referrals WHERE referred_id = ?", (user_id,)) as cursor:
                return await cursor.fetchone() is not None

    async def get_referral_count(self, user_id):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,)) as cursor:
                return (await cursor.fetchone())[0]

    async def get_recent_referrals(self, user_id):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT r.created_at, u.name FROM referrals r JOIN users u ON r.referred_id = u.user_id WHERE r.referrer_id = ? ORDER BY r.created_at DESC LIMIT 5", (user_id,)) as cursor:
                return await cursor.fetchall()

    async def get_top_referrers(self):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT u.name, COUNT(r.id) as ref_count FROM referrals r JOIN users u ON r.referrer_id = u.user_id GROUP BY r.referrer_id ORDER BY ref_count DESC LIMIT 10") as cursor:
                return await cursor.fetchall()

    async def add_bonus(self, user_id, amount, bonus_type='signup'):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("INSERT INTO referral_bonuses (user_id, amount, bonus_type) VALUES (?, ?, ?)", (user_id, amount, bonus_type))
            await db.commit()

    async def get_bonus_balance(self, user_id):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT SUM(amount) FROM referral_bonuses WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row[0] is not None else 0
