import os
import time
import random
import discord
from itertools import cycle
from dotenv import load_dotenv
from discord.ext import commands , tasks
from tic_tac_toe.TicTacToe import TicTacToe

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents = intents)

GAMES = dict()
GAMES_TIME = dict()

def code_string_maker(string:str):
    return "```" + string + "```"

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    game_cleaner.start()
    for guild in bot.guilds:
        print("{}".format(guild.name))
    print("---------")

@tasks.loop(seconds=100)
async def game_cleaner():
    current_time = time.time()
    game_clean_list = list()
    if len(GAMES_TIME) != 0:
        for name in GAMES_TIME:
            time_diff = current_time - GAMES_TIME[name]
            print(name, time_diff)
            if time_diff > 60:
                game_clean_list.append(name)
        for name in game_clean_list:
            GAMES_TIME.pop(name)
            GAMES.pop(name)

# @bot.event
# async def on_message(message):
#     name = message.author.name
#     content = message.content
#     if message.author != bot.user:
#         print(name)
#         print(content)
#     await bot.process_commands(message)

@bot.command(name='rankUs', help='Ranks all of the member of the chat')
async def rankUs(ctx):
    names = list()
    ranks = list()

    for user in ctx.guild.members:
        if (user.name != bot.user.name):
            names.append(user.name)
    random.shuffle(names)
    output = ""

    for i, name in enumerate(names):
        output = output + "{}) {}\n".format(i+1,name)
    await ctx.channel.send(output)


async def winner_print(ctx, game):
    await ctx.channel.send(code_string_maker(game.get_board()))
    # print(game.get_board())
    winner = game.get_winner()
    if (winner == bot.user.name):
        await ctx.channel.send("I have won and you have lost, you fool.\n"\
            "Now leave and take your misrable self away from my gaze")
    else:
        await ctx.channel.send("You have tricked me, but whatever the case.\n"\
            "I crown you the winner for all of time.")

@bot.command()
async def play(ctx, arg1):
    name = ctx.author.name
    content = arg1
    channel = str(ctx.channel)
    if (name != bot.user.name and  
    str(channel) == "Direct Message with {}".format(ctx.author)):
        if name in GAMES:
            if len(content) == 1:
                game = GAMES[name]
                spot = int(content)
                if spot > 0 and spot <10:
                    status = game.play_turn(spot)
                    GAMES_TIME[name] = time.time()
                    if (status == -1):
                        await ctx.channel.send("The spot is already taken")
                    elif status == 1:
                        await winner_print(ctx, game)
                        GAMES.pop(name)
                        GAMES_TIME.pop(name)
                    else:
                        status = bot_play_run(game)
                        GAMES_TIME[name] = time.time()
                        if status == 1:
                            await winner_print(ctx, game)
                            GAMES.pop(name)
                            GAMES_TIME.pop(name)
                        else:
                            await ctx.channel.send(code_string_maker(game.get_board()))
                            # print(game.get_board())
            else:
                await ctx.channel.send("That is not a valid choice. \n"\
                    "The spot must be in between 1 and 9")

        else :
            await ctx.channel.send("There is not game to play 😕")


@bot.command(name="clean-up", pass_context = True)
@commands.has_role('admin')
async def clean_up(ctx, channel_name=None):
    channel = None
    ctx_guild = ctx.guild
    if (channel_name is None):
        channel = ctx.channel
    else:
        for guild_channel in ctx_guild.text_channels:
            if guild_channel.name == channel_name:
                channel = guild_channel
    if channel is None:
        await ctx.channel.send("There is no text channel with that name {}. Please try again".format(channel_name))
    else:
        messages = await channel.history(limit=200).flatten()
        for message in messages:
            if message.author == bot.user:
                await message.delete()
            elif message.content[0] == "$":
                await message.delete()

@bot.command()
async def get_names(ctx):
  names = list()
  for user in ctx.guild.members:
    names.append(user.name)
    
  await ctx.channel.send('\n'.join(names))

def bot_play_run(game:TicTacToe):
    options = [*range(1,11)]
    random.shuffle(options)
    val = options[8]
    status = game.play_turn(val)
    i = 7
    while(status == -1):
        status = game.play_turn(options[i])
        i = i-1
    return status

def game_maker(names):
    player = names[0]
    bot_player = names[1]
    random.shuffle(names)
    game = TicTacToe(names[0], names[1])
    if (names[0] == bot_player):
        bot_play_run(game)
    GAMES[player] = game
    GAMES_TIME[player] = time.time()

@bot.command(name='playme')
async def playme(ctx):
    challenge = "I am the best tictactoe player in all the servers.\n You fool must pay the price for challenge me"
    member = ctx.author
    player_name = ctx.author.name
    names = [ctx.author.name, bot.user.name]
    game_maker(names)
    await member.create_dm()
    await member.send(challenge)
    await member.dm_channel.send(code_string_maker(GAMES[player_name].get_board()))
    print("A Game has been initalized")

bot.run(TOKEN)