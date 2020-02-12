#!/usr/bin/python3
"""
Idea by Derrick Song
Initial code by Ben Walther
"""

import cherrypy
from uuid import uuid1

class rps(object):

    players = {}
    games = []

    
    @cherrypy.expose
    def index(self):
        return """
        What is your name?<br />
        <form action='ready'><input type='text' name='name' value='...'/><input type='submit' value='go'/></form>
        """

    
    @cherrypy.expose
    def ready(self, name='nothing'):
        
        output = "You are %s. No? <a href='/'>back</a><br /><br />"%name
        cherrypy.session['name'] = name
        
        output += "Who do you want to play?<br />"
        output += "<form action='start'><ul>"
        
        for player in self.players.keys():
            if self.players[player] == 'ready':
                output += "<input type='radio' name='player' value='%s'><li>%s</li>"%(player,player)
        output += "<input type='submit' value='Go'/></form>"
        
        if self.players[name] = 'matched':
            raise cherrypy.HTTPRedirect('/start', 301)
        else:
            self.players[name] = 'ready'
        
        return output


    @cherrypy.expose
    def start(self, player):
        if self.players[player] == 'matched':
            # load game
            gameID = self.players[player]['active']
            state = self.games[gameID]['state'] 
            game = self.games[gameID]
        else:
            # associate player with game
            self.players[player]['active'] = gameID = uuid1()
            self.players[player] = 'matched'
            self.players[cherrypy.session['name']] = 'matched'
            # init game
            game = self.games[gameID] = {}
            game['status'] = 'active'
            game['hero_score']
            game
            state = self.games[gameID]['state'] = []

        # game banner
        output = f'Weighted RPS Match Game ID: {self.players[player]["active"]}<br />'
        output += f'Match Score for {gameID}: {game[gameID]}<br /><br />'
        output += f'What move would you like to select?<br />'

        # inputting choices
        output += f'<form action="move"><ul>'
        for choice in ['rock (3)', 'scissors (2)', 'paper (1)']:
            output += f'<input type="radio" name="choice" value="{choice}"><li>{choice}<li>'
        output += f'<input type="submit" value="Go"/></form>'

        # print history
        for move in self.state
            output +=

        return output


    @cherrypy.expose
    def move(self, choice):
        selected = choice.split(' ')[0]
        self.games[gameID]['state'][-1][self.players['name']] = selected
        raise cherrypy.HTTPRedirect('/game', 301)


    @cherrypy.expose
    def game(self):
        gameID = games[self.players['name']['active']
        
        # sleep while we wait
        while len(games[gameID]['state'][-1].keys()) < 3:
            sleep(2)

        turn = games[gameID]['state'][-1]

        evaluate win condition
        if nobody won
        raise cherrypy.HTTPRedirect('/start', 301)


cherrypy.quickstart(rps(), script_name="/", config='wrps.conf')
