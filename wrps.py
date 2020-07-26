#!/usr/bin/python3
"""
Idea by Derrick Song
Initial code by Ben Walther
"""

import cherrypy
from uuid import uuid1

class rps(object):

    players = {}
    games = {}

    
    @cherrypy.expose
    def index(self):
        return """
        What is your name?<br />
        <form action='ready'><input type='text' name='name'/><input type='submit' value='go'/></form>
        """

    
    @cherrypy.expose
    def ready(self, name='nothing'):
        
        output = "You are %s. No? <a href='/'>back</a><br /><br />\n" % name
        cherrypy.session['name'] = name
        if not name in self.players:
            self.players[name] = {}
            self.players[name]['status'] = 'ready'
        else:
            if self.players[name]['status'] == 'matched':
                gameID = self.players[name]['active']
                if self.games[gameID]['p1'] == name:
                    player = self.games[gameID]['p2']
                else:
                    player = self.games[gameID]['p1']
                raise cherrypy.HTTPRedirect('/game?player=' + player, 301)
            else:
                self.players[name]['status'] == 'ready'
        
        count = 0
        for player in self.players.keys():
            if self.players[player]['status'] == 'ready':
                if player != name:
                    count  = count + 1
        output += "Who do you want to play? %s player(s) available<br />\n" % count
        output += "<form action='game'><ul>\n"
        
        for player in self.players.keys():
            if self.players[player]['status'] == 'ready':
                if player != name:
                    output += "<input type='radio' name='player' value='%s'><li>%s</li>\n" % (player, player)
        output += "<input type='submit' value='Go'/></form>"
        
        return output


    @cherrypy.expose
    def game(self, player):
        if self.players[player]['status'] == 'matched':
            # load opponent's game ID
            gameID = self.players[player]['active']
            self.players[cherrypy.session['name']] = gameID
            game = self.games[gameID]
        else:
            # associate player with game
            gameID = self.players[player]['active'] = str(uuid1())
            self.players[player]['status'] = 'matched'
            self.players[cherrypy.session['name']]['status'] = 'matched'
            self.players[cherrypy.session['name']]['active'] = gameID
            # init game
            game = self.games[gameID] = {}
            game['p1'] = cherrypy.session['name']
            game['p2'] = player
            game['status'] = 'active'
            game['p1_score'] = 0
            game['p2_score'] = 0
            game['match_score'] = f'{game["p1"]} {game["p1_score"]} - {game["p2"]} {game["p2_score"]}'
            state = self.games[gameID]['state'] = []

        # game banner
        output = f'Weighted RPS Match Game ID: {gameID}<br />\n'
        output += f'Match Score: {game["match_score"]}<br /><br />\n'
        output += f'What move would you like to select?<br />\n'

        # inputting choices
        output += f'<form action="move"><ul style="list-style-type:none">\n'
        output += f'<input type="hidden" name="gameID" value="{gameID}" />\n'
        for choice in ['rock (3)', 'scissors (2)', 'paper (1)']:
            choice = choice.split(' ')[0]
            output += f'<input type="radio" name="choice" value="{choice}"><li>{choice}<li>\n'
        output += f'</ul>\n<input type="submit" value="Go"/></form>'

        # print history
#        for move in self.state
#            output +=

        return output


    @cherrypy.expose
    def move(self, choice, gameID):
        selected = choice.split(' ')[0]
        self.games[gameID]['state'][-1][self.players['name']] = selected
        raise cherrypy.HTTPRedirect('/game', 301)


cherrypy.quickstart(rps(), script_name="/", config='wrps.conf')
