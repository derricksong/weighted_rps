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
from redisworks import Root
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
description = '''Weighted Rock, Paper, Scissors (!wrps)
An improved version of rock, paper scissors
Winning with different choices scores varying amounts of points
Rock: 3, Scissors: 2, Paper: 1
Type '!wrps challenge <opponent>' to begin
'''
commands = [
  'about',
  'challenge',
  'score'
]
moves = [
  'rock',
  'paper',
  'scissors'
]

class game(Root):
  pass

game = game()
game.flush()
gr = game['round'] = 0
rounds = game['rounds'] = {gr: {'winner': 'n/a'}}
game['p1'] = {
  'name': 'n/a',
  'id': 1,
  'score': 0
}
game['p2'] = {
  'name': 'n/a',
  'id': 2,
  'score': 0
}
p1 = game['p1']['name']
p2 = game['p2']['name']
p1_sc = game['p1']['score'] = 0
p2_sc = game['p2']['score'] = 0
p1_id = game['p1']['id'] = 0
p2_id = game['p2']['id'] = 1
state = game['state'] = 'idle'
players = game['players'] = {'foo': 'bar'}
client = discord.Client()
timer = 3

@client.event
async def on_message(message):
  global p1
  global p2
  global p1_sc
  global p2_sc
  global gr
  global rounds
  global p1_id
  global p2_id
  user = message.author
  content = message.content
  channel = message.channel

  async def score_round(now):
    global p1_sc
    global p2_sc
    global gr
    global rounds

    if now['p1'] == 'rock':
      if now['p2'] == 'rock':
        now['winner'] = 'draw'
      elif now['p2'] == 'paper':
        now['winner'] = 'p2'
        p2_sc += 1
      elif now['p2'] == 'scissors':
        now['winner'] = 'p1'
        p1_sc += 3
    elif now['p1'] == 'paper':
      if now['p2'] == 'rock':
        now['winner'] = 'p1'
        p1_sc += 1
      elif now['p2'] =='paper':
        now['winner'] = 'draw'
      elif now['p2'] =='scissors':
        now['winner'] = 'p2'
        p2_sc += 2
    elif now['p1'] == 'scissors':
      if now['p2'] == 'rock':
        now['winner'] = 'p2'
        p2_sc += 3
      elif now['p2'] == 'scissors':
        now['winner'] = 'draw'
      elif now['p2'] == 'paper':
        now['winner'] == 'p1'
        p1_sc += 2
    await channel.send(f'round {gr} completed!  next round starting')
    gr += 1
    rounds[gr] = {'winner': 'n/a'}
    await display_score()
    if (p1_sc >= 10 or p2_sc >= 10):
      winner = p1 if p1_sc >= 10 else p2
      winner_id = p1_id if p1_sc >= 10 else p2_id
      state = 'idle'
      await channel.send(f'We have a **WINNER**! <@!{winner_id}> is the **CHAMPION**!')

  async def display_score():
    await channel.send(f'round {gr}\'s score: [{p1}] {p1_sc} - [{p2}] {p2_sc}')

  async def start_game():
    global rounds
    now = rounds[gr]
    player = 'p1' if str(user) == p1 else 'p2'
    opponent = 'p2' if player == 'p1' else 'p1'
    print(f'p1: {p1} p2: {p2} user: {player}, opponent: {opponent}, now: {now}')

    async def play_round(now):
      await channel.send(f'round {gr} started! wait {timer} seconds to think about your move')
      await asyncio.sleep(timer)
      await channel.send(f'{p1}: react to this message with an emoji containing your move in the name')
      await channel.send(f'{p2}: react to this message with an emoji containing your move in the name')

      p1_wait = client.wait_for(
        'reaction_add', 
        timeout = 19.0, 
        check = lambda reaction, user: str(user) == p1
      )
      p2_wait = client.wait_for(
        'reaction_add', 
        timeout = 19.0, 
        check = lambda reaction, user: str(user) == p2
      )

#      try:
      await asyncio.gather(p1_wait, p2_wait)
#      except asyncio.TimeoutError:
#        await message.delete() 

      await score_round(now)

    while (p1_sc < 10 and p2_sc < 10):
      await play_round(now)

  if content.startswith('!wrps'):
    full_cmd = content.split('!wrps ')[1]
    cmd = full_cmd.split(' ')[0]
    if cmd in commands:
      if cmd == 'challenge':
        if len(full_cmd.split(' ')) > 1:
          opponent = full_cmd.split(' ')[1]
          opp_id = re.findall(r'\d+', opponent)[0]
          try:
            opponent = await client.fetch_user(opp_id)
            state = 'challenge'
            p1 = str(user)
            p1_id = user.id
            p2 = str(opponent)
            p2_id = opponent.id
            p1_sc = 0
            p2_sc = 0
            gr = 1
            rounds = {gr: {'winner': 'n/a'}}
            await channel.send(f'{user.mention} has issued a challenge to {opponent.mention}')
          except:
            await channel.send(f'Invalid user: {opp_id}')

        try:
          await client.wait_for('message', timeout=30.0, check=lambda msg: (msg.content == '!wrps accept' and str(msg.author) == p2))
          state = 'active'
          await channel.send(f'challenge accepted!  {p1} vs {p2} starting...')
        except asyncio.TimeoutError:
          await channel.send('Timed out, awaiting new challenge')
        await display_score()
        await start_game()
      elif cmd == 'score':
        await display_score()
      elif cmd == 'leaderboard':
        await channel.send(players)
      elif cmd == 'about':
        print('about detected')
        await message.channel.send(description)

@client.event
async def on_reaction_add(reaction, user):
  print(f'reaction: {reaction.emoji.name}, user {user}')
  global rounds
  if (str(user) in [p1, p2] and 'containing your move' in reaction.message.content):
    player = 'p1' if p1 == str(user) else 'p2'
    emoji = reaction.emoji
    now = rounds[gr]

    for move in moves:
      if emoji.name.find(move) != -1:
        now[player] = move
        try:
          print(f'now: {now} player {player} move {move}')
          await reaction.message.delete()
        except Exception as e:
          print(e)

client.run(TOKEN)
