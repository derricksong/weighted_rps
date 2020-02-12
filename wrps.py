#!/usr/bin/python3
"""
Idea by Derrick Song
Initial code by Ben Walther
"""

import cherrypy


class rps(object):

    cherrypy.server.socket_host = '0.0.0.0'
    players = {}
    games = []

    
    @cherrypy.expose
    def index(self):
        return """
        "What is your name?<br />
        <form action=ready><input type='text' name='name' value='...'/><input type='submit' value='go'/></form>"
        """

    
    @cherrypy.expose
    def ready(self,name='nothing'):
        output = "You are %s. No? <a href='/'>back</a><br /><br />"%name
        cherrypy.session['name'] = name
        output += "Who do you want to play?<br />"
        output += "<form method=start><ul>"
        for player in self.players.keys():
            if self.players[player] == 'ready':
                output += "<input type='radio' name='player' value='%s'><li>%s</li>"%(player,player)
        output += "<input type='submit' value='Go'/></form>"
        self.players[name] = 'ready'
        return output

    
    def start(self,player):
        moves = []
        pass

cherrypy.quickstart(rps())
