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
  sources = [
    {
      "name" : "leetcode",
      "problem_source" : "https://raw.githubusercontent.com/fishercoder1534/Leetcode/master/README.md", # md source, backup in https://github.com/saralaya00/Leetcode
      "problem_dest" : "https://leetcode.com/problems/", # Not required for now
      "msg_template" : "**Leetcode - Random daily**\n{problem_num} - {problem_title} ||**{difficulty}**||\n{link}"
    },
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
      "msg_template" : "**Codeforces - Random daily**\n{problem_title}\n||{tags}||\n{link}"
    }
  ]

  HELP_MSG_STRING = """
*BigBrainBot* is a discord bot made to replace warwolf.
Automatically drops daily coding problems every three hours.

Use **bot :get** command with any source (leetcode, codechef, codeforces) to get problems.
Use **bot :solution** followed by a github.com link to get a point.
Use **bot :mypoints** command to get your Bigbrain points.
Use **bot :deletepoints** command to delete your Bigbrain points.
**bot :help** displays this message."""

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

    author_id = f"{message.author.id}"
    message_content = message.content.lower()

    if "bot" in message_content:
      if ":help" in message_content:
        await message.channel.send(self.HELP_MSG_STRING)
        return 

      if ":mypoints" in message_content:
        if author_id in db.keys():
          points = db[author_id]
        else:
          points = 0
        await message.channel.send(f"Your have {points} points.")
        return

      if ":deletepoints" in message_content:
        if author_id in db.keys():
          del db[author_id]
        await message.channel.send("points deleted.")
        return

      if ":solution" and "github.com" in message_content:
        if not author_id in db.keys():
          db[author_id] = 1
        else:
          db[author_id] += 1

        messages_str = ['⊂(・▽・⊂)', 'mah man!', 'ayy', 'geng geng']
        reply = random.choice(messages_str)
        await message.channel.send(reply)
        return

      if ":get" in message_content:
        source_name_list = ["leetcode", "codechef", "codeforces"]
        for source_name in source_name_list:
          if source_name in message_content:
            index = source_name_list.index(source_name)
            source = self.sources[index]
            problem = helper.scrape_daily_problem(source)
            msg = problem['msg']
            await message.channel.send(msg)
            return

      if any(element in message_content for element in ["thank you", "thanks", "arigato", "good"]):
        await message.channel.send(":D")
        return

      if any(element in message_content for element in ["bad"]):
        await message.channel.send(":(")
        return

      await message.channel.send("Use *bot :help* to get bot info.")
      return

keep_alive()
client = DiscordClient()
client.run(os.getenv('TOKEN'))