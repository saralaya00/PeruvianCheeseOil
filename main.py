import codechef
import discord
import os

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('$problem'):
    problem = codechef.scrape('https://www.codechef.com')
    msg = f"**{problem['problem_title']}**\n{problem['link']}"
    await message.channel.send(msg)

client.run(os.getenv('TOKEN'))
