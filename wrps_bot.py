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
from redis import Redis
import pottery
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
YAML_FILES = ['commands',]

config = {}
for f in YAML_FILES:
  with open(f'{f}.yaml') as file:
    config[f] = yaml.load(file, Loader=yaml.FullLoader)
cmds = config['commands']

redis = Redis.from_url('redis://localhost:6379')
game = pottery.RedisDict(redis=redis, key='game')
p1 = game['p1'] if 'p1' in game else ''
p2 = game['p2'] if 'p2' in game else ''
p1_score = game['p1_score'] if 'p1_score' in game else 0
p2_score = game['p2_score'] if 'p2_score' in game else 0
game_round = game['round'] if 'round' in game else 0
print(game)

client = discord.Client()
@client.event
async def on_message(message):
  user = message.author
  content = message.content
  channel = message.channel

  async def score_round(n):
    now = game[f'round_{str(n+1)}']
    if now[p1] == rock:
      if now[p2] == 'rock':
        now['winner'] = 'draw'
      elif now[p2] == 'paper':
        now['winner'] = 'p2'
        p2_score += 1
      elif now[p2] == 'scissors':
        now['winner'] = 'p1'
        p1_score += 3
    elif now[p1] == 'paper':
      if now[p2] == 'rock':
        now['winner'] = p1
        p1_score += 1
      elif now[p2] =='paper':
        now['winner'] = 'draw'
      elif now[p2] =='scissors':
        now['winner'] = p2
        p2_score += 2
    elif now[p1] == 'scissors':
      if now[p2] == 'rock':
        now['winner'] = p2
        p2_score += 3
      elif now[p2] == 'scissors':
        now['winner'] = 'draw'
      elif now[p2] == 'paper':
        now['winner'] == p1
        p1_score += 2
    game['round'] += 1
    game[f'round_{str(n+1)}'] = {}
    await display_score()
    if (game['p1_score'] >= 10 or game['p2_score'] >= 10):
      winner = game['p1'] if game['p1_score'] >= 10 else game['p2']
      channel.send(f'We have a **WINNER**! **{winner}** is the **CHAMPION**!')

  async def display_score():
    await channel.send(f'round {game_round + 1}\'s score: [{game["p1"]}] {p1_score} - [{game["p2"]}] {p2_score}')

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
          print(opponent)
          print(opp_id)
          print(game)
          try:
            opponent = await client.fetch_user(opp_id)
            game['state'] = 'challenge'
            game['p1'] = str(user)
            game['p1_id'] = user.id
            game['p2'] = str(opponent)
            game['p2_id'] = opponent.id
            game['p1_score'] = 0
            game['p2_score'] = 0
            game['round'] = 0
            game['round_0'] = {}
            print(f'user: {user}, opponent: {opponent}')
            await channel.send(f'{user.mention} has issued a challenge to {opponent.mention}')
          except:
            await channel.send(f'Invalid user: {opp_id}')

        try:
          await client.wait_for('message', timeout=30.0, check=lambda message: (message.content == '!wrps accept' and str(message.author) == game['p2']))
          game['state'] = 'active'
          await channel.send(f'challenge accepted, mute your opponent!  {game["p1"]} vs {game["p2"]} starting...')
          await display_score()
          return
        except asyncio.TimeoutError:
          await channel.send('Timed out, awaiting new challenge')

      elif cmd == 'history':
        return
      elif cmd in ('rock', 'paper', 'scissors'):
        print('choice detected')
        now = game[f'round_{game["round"]}']
        player = 'p1' if str(user) == game['p1'] else 'p2'
        opponent = 'p1' if player == 'p2' else 'p2'
        print(f'user: {user}, opponent: {opponent}, now: {now}')
        if not (player in now or opponent in now):
          print('no choices detected')
          now[player] = cmd
          try:
            await channel.send(f'{game[player]} made their selection!  Waiting 30 seconds for the other player')
            print(game)
            print(f'{user} {opponent} {now}')
            await client.wait_for('message', timeout=30.0, check=lambda msg: (str(msg.author) == game[opponent] and msg.content in ('!wrps rock' or '!wrps scissor' or '!wrps paper')))
          except asyncio.TimeoutError:
            await channel.send(f'Timed out, {game[opponent]} didn\'t make a selection..')
        if player in now:
          print(f'Changing {player}\'s move to {cmd}')
          now[player] = cmd
        if opponent in now:
          now[player] = cmd
          channel.send(f'{player} made their move.  Both players have made a selection')
          if (player in now and opponent in now):
            score_round(game['round'])
      elif cmd == 'score':
        await display_score()
      elif cmd == 'leaderboard':
        channel.send(players)
      elif cmd == 'about':
        print('about detected')
        await message.channel.send(cmds['about']['description'])

client.run(TOKEN)
