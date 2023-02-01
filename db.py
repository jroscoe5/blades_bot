import aiosqlite
import matplotlib.pyplot as plt
import uuid

DB_PATH = './timers.sqlite'

class Timer():
    def __init__(self, attributes) -> None:
        self.id = attributes[0]
        self.message_id = attributes[1]
        self.guild_id = attributes[2]
        self.title = attributes[3]
        self.slices = attributes[4]
        self.color = attributes[5]
        self.progress = attributes[6]
    
    def increment(self):
        if self.progress + 1 > self.slices: return
        self.progress += 1

    def decrement(self):
        if self.progress - 1 < 0: return
        self.progress -= 1

    def plot(self):
        sizes   = [float(100 / self.slices) for _ in range(self.slices)]
        colors  = ['white' for _ in range(self.slices)]
        
        for i in range(self.progress): colors[-1 - i] = self.color
        
        plt.rcParams["figure.figsize"] = [3.5, 3.5]
        plt.rcParams["figure.autolayout"] = True

        fig1, ax = plt.subplots()
        wedges, texts = ax.pie(sizes, startangle=90, colors=colors)
        for w in wedges:
            w.set_linewidth(2)
            w.set_edgecolor('black')

        ax.axis('equal')
        plt.title(self.title, fontdict=
            {
            'family': 'serif',
            'color':  'black',
            'weight': 'bold',
            'size': 12,
            }
        )
        filename = f'{uuid.uuid4()}.png'
        plt.savefig(filename)

        return filename


async def initialize():
    """
    Initializes the db with the champions table
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS timers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    message_id INTEGER UNIQUE, 
                    guild_id INTEGER,
                    title TEXT,
                    slices INTEGER,
                    color TEXT,
                    progress INTEGER
                    )
                '''
            )
        await db.commit()


async def update_timer(timer):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                ("UPDATE timers SET color = ?, progress = ? WHERE id = ?"),
                (timer.color, timer.progress, timer.id)
            )
        await db.commit()


async def create_timer(attributes):
    """
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                ("INSERT INTO timers (message_id, guild_id, title, slices, color, progress) VALUES(?,?,?,?,?,?)"),
                (attributes[1], attributes[2], attributes[3], attributes[4], attributes[5], attributes[6])
            )
        await db.commit()
    return True


async def get_timer(message_id, guild_id):
    """
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT * FROM timers WHERE message_id = ? AND guild_id = ?', (message_id, guild_id))
            row = await cursor.fetchone()
            if row: 
                return Timer(row)
            else:
                return None
