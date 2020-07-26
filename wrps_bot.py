#!/usr/bin/env python3
"""
name: user-helper.py
date: 7/18/20
description: discord bot for performing user management tasks
author: root@derricksong.com
"""

import os
import discord
import asyncio
import yaml
import json
import re
import redis
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
game = redis.Redis(host='localhost', port=6379 db=0)
YAML_FILES = ['commands','game']
config = {}
for f in YAML_FILES:
  with open(f'{f}.yaml') as file:
    config[f] = yaml.load(file, Loader=yaml.FullLoader)

cmds = config['commands']

client = discord.Client()
@client.event
async def on_message(message):
  user = message.author
  content = message.content
  channel = message.channel

  print(f'user: {user}, content: {content}')

  async def status():
      await channel.send(f'currently {game.get("p1_name")} is playing {game.get("p2_name")}')
      await channel.send(f'score is {game.get("p1_score")} ({game.get("p1_name")}) - {game.get("p2_score")} ({game.get("p2_name")})')

  if content.startswith('!wrps'):
    print('!wrps match detected')
    full_cmd = content.split('!wrps ')[1]
    cmd = full_cmd.split(' ')[0]
    print(f'full cmd: {full_cmd}')
    print(f'cmd: "{cmd}"')
    if cmd in cmds.keys():
      if cmd == 'challenge':
        print(f'challenge detected by {user}')
        if len(full_cmd.split(' ')) > 1:
          opponent = full_cmd.split(' ')[1]
          opp_id = re.findall(r'\d+', opponent)[0]
          try:
            opponent = await client.fetch_user(opp_id)
            game.set('state', 'challenge')
            game.set('p1', str(user))
            game.set('p2', str(opponent))
            print(f'user: {user}, opponent: {opponent}')
            await channel.send(f'{user.mention} has issued a challenge to {opponent.mention}')
          except:
            await channel.send(f'Invalid user: {opponent}')
 
        try:
          message = await client.wait_for('message', timeout=30.0, check=lambda message: str(message.author) == str(game.get('p2')) and message.content == '!wrps accept')
          game.set('state', 'active')
          await channel.send(f'challenge accepted!  weighted rps: {game.get("p1")} vs {game.get("p2")} starting...')
          await status()
        except asyncio.TimeoutError:
          await channel.send('Timed out, awaiting new challenge')

      elif cmd == 'history':
        return
      elif cmd == 'score':
        await status()
      elif cmd == 'leaderboard':
        channel.send(players)
      elif cmd == 'about':
        print('about detected')
        await message.channel.send(cmds['about']['description'])

client.run(TOKEN)
