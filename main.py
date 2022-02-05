import discord
import helper
import os
import random

from replit import db
from discord.ext import tasks
from keep_alive import keep_alive
from datetime import date

class DiscordClient(discord.Client):
  #big-brain-coding channel id
  CHANNEL_ID = 938668885316628502

  # db[source.name] = todate
  sources = [
    {
      "name" : "codechef",
      "problem_source" : "https://www.codechef.com",
      "problem_dest" : "https://www.codechef.com",
      "msg_template" : "**Codechef - Problem of the Day**\n{problem_title}\n{link}"
    },
    {
      "name" : "codeforces",
      "problem_source" : "https://codeforces.com/api/problemset.problems", # API Source where we can get the problemset json (manually used for now)
      "problem_dest" : "https://codeforces.com/problemset/problem",
      "msg_template" : "**Codeforces - Random daily**\nTitle: {problem_title}\nTags: ||{tags}||\n{link}"
    }
  ]

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # start the task to run in the background
    self.write_daily_question.start()

  async def on_ready(self):
    print(f'{self.user} has logged in.')

  @tasks.loop(minutes=60 * 3)
  async def write_daily_question(self):
    todate = f"{date.today()}"

    for source in self.sources:
      source_name = source["name"]
      if not source_name in db.keys():
        db[source_name] = "False"

      if not db[source_name] == todate:
        problem = helper.scrape_daily_problem(source)
        msg = problem['msg']
        
        channel = self.get_channel(self.CHANNEL_ID)
        print(f"Sending {source_name} message {todate}")
        db[source_name] = todate
        await channel.send(msg)
        break
      else:
        print(f"DB entry for {source_name} is present [{db[source_name]}], skipping post.")
  
  @write_daily_question.before_loop
  async def before_my_task(self):
    await self.wait_until_ready() # wait until the bot logs in
  
  async def on_message(self, message):
    # we do not want the bot to reply to itself
    if message.author.id == self.user.id:
      return

    if "bot" in message.content.lower():
      if any(element in message.content.lower() for element in ["thank you", "thanks", "arigato", "good"]):
        await message.channel.send(":D")
      elif any(element in message.content.lower() for element in ["bad", "stupid"]):
        await message.channel.send(":(")
      else:
        await message.channel.send("Let's go to the mall, today!")

    if "solution" and "github.com" in message.content.lower():
      messages_str = ['⊂(・▽・⊂)', 'mah man!', 'ayy', 'geng geng']
      reply = random.choice(messages_str)
      await message.channel.send(reply)

keep_alive()
client = DiscordClient()
client.run(os.getenv('TOKEN'))