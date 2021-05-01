from discord.ext import commands
from lxml import html
from difflib import SequenceMatcher
import subprocess
import threading
import aiofiles
import discord
import asyncio
import aiohttp
import random
import ctypes
import re
import os

ctypes.windll.kernel32.SetConsoleTitleW('Aprendiz')
token = 'ODMzMjA1MDc2MDIwODIyMDI2.YHu8sg.hF1LE4aDSqxc6BHxemx1End8uk0'
prefix = '/'

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=prefix, case_insensitive=True, intents=intents)
bot.remove_command('help')

administrators = [823013342099537941]
chat_channel = 831329292293111855
bots_channel = 829292055649189908

queue = []

blacklisted = []

def followsv2():
    while True:
        try:
            task, arg1, arg2 = queue.pop(0).split('-')
            subprocess.run([f'{task}', f'{arg1}', f'{arg2}'])
        except:
            pass

threading.Thread(target=followsv2).start()

@bot.event
async def on_ready():
    blacklisted.clear()
    with open('blacklisted.txt', 'r') as f:
        for x in f.readlines():
            blacklisted.append(x.replace('\n', ''))
    print(f'Servers: {len(bot.guilds)}')
    for guild in bot.guilds:
        print(guild.name)
    print()
    # bot.loop.create_task(status())
    while True:
        members = sum([guild.member_count for guild in bot.guilds])
        activity = discord.Activity(type=discord.ActivityType.watching, name=f'{members} users!')
        await bot.change_presence(activity=activity)
        await asyncio.sleep(60)

@bot.event
async def on_member_join(member):
    channel = await bot.fetch_channel(bots_channel)
    await channel.send(f'Welcome to **Twitch Followers v2**, {member.mention}.\nType `/help` to get started!')

@bot.event
async def on_command_error(ctx, error: Exception):
    if ctx.channel.id == bots_channel:
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(color=1376511, description=f'{error}')
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(color=1376511, description='You are missing arguments required to run this command!')
            await ctx.send(embed=embed)
            ctx.command.reset_cooldown(ctx)
        elif 'You do not own this bot.' in str(error):
            embed = discord.Embed(color=1376511, description='You do not have permission to run this command!')
            await ctx.send(embed=embed)
        else:
            print(str(error))
    else:
        try:
            await ctx.message.delete()
        except:
            pass

@bot.command()
async def help(ctx):
    if ctx.channel.type != discord.ChannelType.private:
        embed = discord.Embed(color=1376511)
        
        embed.add_field(name='1 | Help', value='`/help`', inline=True)
        embed.add_field(name='2 | Open Ticket', value='`/ticket`', inline=True)
        embed.add_field(name='3 | Close Ticket', value='`/close`', inline=True)
        embed.add_field(name='4 | Tasks', value='`/tasks`', inline=True)
        embed.add_field(name='5 | Twitch Followers', value='`/tfollow (channel)`', inline=True)
        embed.add_field(name='6 | Twitch Spam', value='`/tspam (channel) (message)`', inline=True)
        embed.set_thumbnail(url='https://media.discordapp.net/attachments/828799355556593685/831184357112283166/image0.jpg?width=449&height=449')
        embed.set_author(name=f'{ctx.guild.name} | Commands', icon_url='https://media.discordapp.net/attachments/828799355556593685/831184357112283166/image0.jpg?width=449&height=449')
        embed.add_field(name='Twitch Friend Requests', value='`/tfriend (channel)`', inline=True)
        await ctx.channel.send(embed=embed)

@bot.command()
async def ticket(ctx):
    if ctx.channel.type != discord.ChannelType.private:
        channels = [str(x) for x in bot.get_all_channels()]
        if f'ticket-{ctx.author.id}' in str(channels):
            embed = discord.Embed(color=1376511, description='You already have a ticket open!')
            await ctx.send(embed=embed)
        else:
            ticket_channel = await ctx.guild.create_text_channel(f'ticket-{ctx.author.id}')
            await ticket_channel.set_permissions(ctx.guild.get_role(ctx.guild.id), send_messages=False, read_messages=False)
            await ticket_channel.set_permissions(ctx.author, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)
            embed = discord.Embed(color=1376511, description='Please enter the reason for this ticket, type **/close** if you want to close this ticket.')
            await ticket_channel.send(f'{ctx.author.mention}', embed=embed)
            await ctx.message.delete()

@bot.command()
async def close(ctx):
    if ctx.channel.type != discord.ChannelType.private:
        if ctx.channel.name == f'ticket-{ctx.author.id}':
            await ctx.channel.delete()
        elif ctx.author.id in administrators and 'ticket' in ctx.channel.name:
            await ctx.channel.delete()
        elif discord.utils.get(ctx.guild.roles, name='Closer') in ctx.author.roles:
            await ctx.channel.delete()
        else:
            embed = discord.Embed(color=1376511, description=f'You do not have permission to run this command!')
            await ctx.send(embed=embed)

@bot.command()
async def tasks(ctx):
    if ctx.channel.type != discord.ChannelType.private:
        if ctx.channel.id == bots_channel:
            embed = discord.Embed(color=1376511, description=f'`{len(queue)}` tasks in the queue!')
            await ctx.send(embed=embed)
        else:
            await ctx.message.delete()

tfollow_cooldown = []

@bot.command()
@commands.cooldown(1, 120, type=commands.BucketType.user)
async def tfollow(ctx, channel, amount: int=None):
    if ctx.channel.type != discord.ChannelType.private:
        if ctx.channel.id == bots_channel or ctx.author.id in administrators:
            try:
                if '-' in str(channel):
                    raise Exception
                if str(channel).lower() in blacklisted and ctx.author.id not in administrators:
                    embed = discord.Embed(color=16379747, description=f"**{channel}** is blacklisted")
                    await ctx.channel.send(embed=embed)
                    return
                max_amount = 0
                if ctx.author.id in administrators:
                    tfollow.reset_cooldown(ctx)
                    max_amount += 10000000000
                premium = discord.utils.get(ctx.guild.roles, name='Premium')
                if premium in ctx.author.roles:
                    max_amount += 1000
                diamond = discord.utils.get(ctx.guild.roles, name='Diamond')
                if diamond in ctx.author.roles:
                    max_amount += 800
                gold = discord.utils.get(ctx.guild.roles, name='Gold')
                if gold in ctx.author.roles:
                    max_amount += 600
                silver = discord.utils.get(ctx.guild.roles, name='Silver')
                if silver in ctx.author.roles:
                    max_amount += 350
                bronze = discord.utils.get(ctx.guild.roles, name='Bronze')
                if bronze in ctx.author.roles:
                    max_amount += 100
                booster = discord.utils.get(ctx.guild.roles, name='Sexy Bitch')
                if booster in ctx.author.roles:
                    max_amount += 10000
                _75 = discord.utils.get(ctx.guild.roles, name='Premium +')
                if _75 in ctx.author.roles:
                    max_amount += 2500
                _25 = discord.utils.get(ctx.guild.roles, name='Server Booster')
                if _25 in ctx.author.roles:
                    max_amount += 300
                _10 = discord.utils.get(ctx.guild.roles, name='+10')
                if _10 in ctx.author.roles:
                    max_amount += 10
                _5 = discord.utils.get(ctx.guild.roles, name='+5')
                if _5 in ctx.author.roles:
                    max_amount += 5
                max_amount += 100
                if amount is None:
                    amount = max_amount
                elif amount > max_amount:
                    amount = max_amount
                if amount <= max_amount:
                    position = len(queue) + 1
                    embed = discord.Embed(color=1376511, description=f'Sending **{amount}** followers to **{channel}** 🔥')
                    await ctx.send(embed=embed)
                    queue.append(f'tfollow-{channel}-{amount}')
            except:
                embed = discord.Embed(color=1376511, description='An error has occured while attempting to run this command')
                await ctx.send(embed=embed)
                tfollow.reset_cooldown(ctx)
        else:
            await ctx.message.delete()
            tfollow.reset_cooldown(ctx)

tfriend_cooldown = []

@bot.command()
@commands.cooldown(1, 60, type=commands.BucketType.user)
async def tfriend(ctx, channel, amount: int=None):
    if ctx.channel.type != discord.ChannelType.private:
        if ctx.channel.id == bots_channel or ctx.author.id in administrators:
            if discord.utils.get(ctx.guild.roles, name='Premium') in ctx.author.roles or discord.utils.get(ctx.guild.roles, name='Premium') in ctx.author.roles or ctx.author.id in administrators:
                try:
                    if '-' in str(channel):
                        raise Exception
                    if str(channel).lower() in blacklisted and ctx.author.id not in administrators:
                        embed = discord.Embed(color=16379747, description=f"**{channel}** is blacklisted")
                        await ctx.channel.send(embed=embed)
                        return
                    max_amount = 0
                    if ctx.author.id in administrators:
                        tfriend.reset_cooldown(ctx)
                        max_amount += 10000000
                    premium = discord.utils.get(ctx.guild.roles, name='Premium')
                    if premium in ctx.author.roles:
                        max_amount += 100
                    _75 = discord.utils.get(ctx.guild.roles, name='Premium +')
                    if _75 in ctx.author.roles:
                        max_amount += 200
                    if amount is None:
                        amount = max_amount
                    elif amount > max_amount:
                        amount = max_amount
                    if amount <= max_amount:
                        position = len(queue) + 1
                        embed = discord.Embed(color=1376511, description=f'Sending **{amount}** friend requests to **{channel}** :zap:')
                        await ctx.send(embed=embed)
                        queue.append(f'tfriend-{channel}-{amount}')
                except:
                    embed = discord.Embed(color=1376511, description='An error has occured while attempting to run this command!')
                    await ctx.send(embed=embed)
                    tfriend.reset_cooldown(ctx)
            else:
                embed = discord.Embed(color=1376511, description='Only **Premium** can use this!')
                await ctx.send(embed=embed)
        else:
            await ctx.message.delete()
            tfriend.reset_cooldown(ctx)

_delay = 600

@bot.command()
async def trivia(ctx):
    if ctx.channel.type != discord.ChannelType.private:
        if ctx.author.id in administrators:
            await ctx.message.delete()
            async with aiohttp.ClientSession() as session:
                while True:
                    try:
                        # question, answer = random.choice(list(questions.items()))
                        while True:
                            async with session.get('https://opentdb.com/api.php?amount=1&type=multiple') as r:
                                r = await r.json()
                                question = html.fromstring(str(r['results'][0]['question'])).text_content()
                                answer = r['results'][0]['correct_answer']
                                if 'which' in question.lower():
                                    pass
                                else:
                                    break
                        embed = discord.Embed(color=1376511, description=f'**{question}**\n\nReward: **250 twitch followers**')
                        await ctx.send(embed=embed)
                        eembed = discord.Embed(color=1376511, description=f'**{answer}** | The current trivia answer')
                        await ctx.guild.get_channel(logs_channel).send(embed=eembed)
                        def check(message: discord.Message):
                            # return str(message.content).lower() == str(answer).lower()
                            return SequenceMatcher(None, str(answer).lower(), str(message.content).lower()).ratio() > float(0.5) and message.channel.id == chat_channel
                        _answer = await bot.wait_for('message', check=check, timeout=120.0)
                        try:
                            embed = discord.Embed(color=1376511, description=f'{_answer.author.mention} has answered the question correctly!\n\nAnswer: **{answer}**')
                            await ctx.send(embed=embed)
                            embed = discord.Embed(color=1376511, description=f'{_answer.author.mention} send your twitch channel to claim the reward!')
                            await ctx.send(embed=embed)
                            def _check(message: discord.Message):
                                return message.author.id == _answer.author.id and message.channel.id == chat_channel
                            _channel = await bot.wait_for('message', check=_check, timeout=300.0)
                            queue.append(f'tfollow-{_channel.content}-250')
                        except asyncio.TimeoutError:
                            pass
                    except asyncio.TimeoutError:
                        embed = discord.Embed(color=1376511, description=f'Nobody answered the question correctly.\n\nCorrect Answer: **{answer}**')
                        await ctx.send(embed=embed)
                    except:
                        pass
                    await asyncio.sleep(_delay)
        else:
            await ctx.message.delete()

@bot.command()
async def delay(ctx, seconds):
    if ctx.channel.type != discord.ChannelType.private:
        if ctx.author.id in administrators:
            global _delay
            _delay = int(seconds)
            embed = discord.Embed(color=1376511, description=f'Set trivia delay to **{seconds}** seconds!')
            await ctx.send(embed=embed)
        else:
            await ctx.message.delete()

@bot.command()
@commands.cooldown(1, 600, type=commands.BucketType.user)
async def tspam(ctx, channel, *, msg):
    if ctx.channel.type != discord.ChannelType.private:
        if discord.utils.get(ctx.guild.roles, name='Premium') in ctx.author.roles or discord.utils.get(ctx.guild.roles, name='Premium +') in ctx.author.roles or ctx.author.id in administrators:
            if ctx.channel.id == bots_channel or ctx.author.id in administrators:
                try:
                    max_amount = 0
                    if ctx.author.id in administrators:
                        tspam.reset_cooldown(ctx)
                        max_amount += 48
                    max_amount += 5
                    amount = None
                    if amount is None:
                        amount = max_amount
                    if amount <= max_amount:
                        position = len(queue) + 1
                        embed = discord.Embed(color=1376511, description=f'Spamming **{channel}** with **{msg}** :zap:')
                        await ctx.send(embed=embed)
                        queue.insert(0, f'tspam-{channel}-{msg}')
                except:
                    embed = discord.Embed(color=16379747, description='An error has occured while attempting to run this command!')
                    await ctx.send(embed=embed)
                    tspam.reset_cooldown(ctx)
            else:
                await ctx.message.delete()
                tspam.reset_cooldown(ctx)
        else:
            embed = discord.Embed(color=1376511, description='Only **Premium** can use this!')
            await ctx.send(embed=embed)

@bot.command()
async def rget(ctx, asset_id):
    print(f'{ctx.author} | {ctx.author.id} -> /rget {asset_id}')
    if ctx.channel.type != discord.ChannelType.private:
        if ctx.channel.id == bots_channel:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'https://assetdelivery.roblox.com/v1/asset?id={asset_id}') as r:
                        r = await r.text()
                    async with session.get(f'https://assetdelivery.roblox.com/v1/asset?id=' + re.search('id=(.*)</url>', r).group(1)) as r:
                        r = await r.read()
                try:
                    f = await aiofiles.open(f'{asset_id}.png', mode='wb')
                    await f.write(r)
                    await f.close()
                    embed = discord.Embed(color=16379747)
                    file = discord.File(f'{asset_id}.png')
                    embed.set_image(url=f'attachment://{asset_id}.png')
                    await ctx.send(embed=embed, file=file)
                finally:
                    try:
                        os.remove(f'{asset_id}.png')
                    except:
                        pass
            except:
                embed = discord.Embed(color=1376511, description='An error has occured while attempting to run this command!')
                await ctx.send(embed=embed)
        else:
            await ctx.message.delete()

@bot.command()
async def blacklist(ctx, *, channel):
    if ctx.author.id in administrators:
        try:
            global blacklisted
            blacklisted.append(str(channel).lower())
            with open('blacklisted.txt', 'w') as f:
                for x in blacklisted:
                    f.write(f'{x}' + '\n')
            f.close()
            embed = discord.Embed(color=1376511, description=f'**{channel}** has been blacklisted from twitch commands.')
            await ctx.send(embed=embed)
        except:
            embed = discord.Embed(color=1376511, description='An error has occurred while attempting to run this command!')
            await ctx.send(embed=embed)
    else:
        await ctx.message.delete()

bot.run("ODMzMjA1MDc2MDIwODIyMDI2.YHu8sg.hF1LE4aDSqxc6BHxemx1End8uk0")
