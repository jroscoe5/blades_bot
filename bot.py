from discord.ext import commands
import discord
import db
import os

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(intents=intents, command_prefix='!')

async def change_image(message, filepath):
    await message.edit(attachments=[discord.File(filepath)])
    os.remove(filepath)

@client.event
async def on_ready():
    await db.initialize()
    print("initialized db")

@client.event
async def on_raw_reaction_add(payload):
    if payload.member.bot: return

    emoji = payload.emoji.name.strip()
    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    guild_id = payload.guild_id

    timer = await db.get_timer(payload.message_id, guild_id)

    if not timer: return

    if emoji == '⬆️':
        timer.increment()
    if emoji == '⬇️':
        timer.decrement()
    if emoji == '🔴':
        timer.color = 'red'
    if emoji == '🟠':
        timer.color = 'orange'
    if emoji == '🟡':
        timer.color = 'yellow'
    if emoji == '🟢':
        timer.color = 'green'
    if emoji == '🔵':
        timer.color = 'blue'
    if emoji == '🟣':
        timer.color = 'purple'
    if emoji == '🔄':
        timer.progress = 0

    await db.update_timer(timer)

    await change_image(message, timer.plot())


@client.command()
async def create(ctx, slices, *title):
    control_emojis = ['⬆️', '⬇️', '🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '🔄']
    try:

        slices = int(slices)
        title = ' '.join(title)
        attributes = ['', '', '', title, slices, 'red', 0]
        timer = db.Timer(attributes)

        filepath = timer.plot()

        created_msg = await ctx.send('', file=discord.File(filepath))
        os.remove(filepath)

        attributes[1] = created_msg.id
        attributes[2] = created_msg.guild.id
        await db.create_timer(attributes)

        for emoji in control_emojis:
            await created_msg.add_reaction(emoji)

    except Exception as exc:
        await ctx.send(str(exc), delete_after=10)
    
    await ctx.message.delete()

token = input('token: ')
client.run(token)