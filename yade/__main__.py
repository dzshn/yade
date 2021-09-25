import argparse

from discord.ext import commands

parser = argparse.ArgumentParser()
parser.add_argument("token")

if __name__ == '__main__':
    args = parser.parse_args()
    bot = commands.Bot(commands.when_mentioned)
    bot.load_extension('yade')
    bot.run(args.token)
