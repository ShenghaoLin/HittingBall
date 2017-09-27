# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import game

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.game_peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s

    def set_state(self, state):
        self.state = state
        
    def get_state(self):
        return self.state
    
    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me
        
    def connect_to(self, peer):
        msg = M_CONNECT + peer
        mysend(self.s, msg)
        response = myrecv(self.s)
        if response == (M_CONNECT+'ok'):
            self.peer = peer
            self.out_msg += 'You are connected with ' + self.peer + '\n'
            return (True)
        elif response == (M_CONNECT + 'busy'):
            self.out_msg += 'User is busy. Please try again later\n'
        elif response == (M_CONNECT + 'hey you'):
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def game_connect(self, peer):
        msg = M_GAME + peer
        mysend(self.s, msg)
        response = myrecv(self.s)
        if response == (M_GAME + 'ok'):
            self.game_peer = peer
            return True
        elif response == (M_GAME + 'You'):
            self.game_peer = ''
            return True
        else:
            return False

    def disconnect(self):
        msg = M_DISCONNECT
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_code, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:
                
                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg[0] == 'g':
                    peer = my_msg[1:].strip()
                    if self.game_connect(peer):
                        if self.game_peer == '':
                            self.out_msg += "\nYou are playing the game offline!\nGaming...\nYou left the game.\n"
                            gaming = game.GAME(self.s, False, True, self.me, self.me)
                            gaming.start()
                        else:
                            self.out_msg += "Waiting for the other player's response..."
                    else:
                        self.out_msg += "Sorry, cannot connect to " + peer

                elif my_msg[0:2].lower() == 'no':
                    self.game_peer = my_msg[2:].strip()
                    msg = G_REPLY + 'N' + self.game_peer
                    mysend(self.s, msg)

                elif my_msg[0:3].lower() == 'yes':
                    self.game_peer = my_msg[3:].strip()
                    msg = G_REPLY + 'Y' + self.game_peer
                    mysend(self.s, msg)

                elif my_msg[0] == 'h':
                    self.game_peer = my_msg[1:].strip()
                    msg = M_HISTORY + self.game_peer
                    mysend(self.s, msg)
                    history = myrecv(self.s)
                    self.out_msg += history[1:].strip()
                    
                elif my_msg == 'time':
                    mysend(self.s, M_TIME)
                    time_in = myrecv(self.s)
                    self.out_msg += "Time is: " + time_in
                            
                elif my_msg == 'who':
                    mysend(self.s, M_LIST)
                    logged_in = myrecv(self.s)
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in
                            
                elif my_msg[0] == 'c':
                    peer = my_msg[1:].strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'
                        
                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, M_SEARCH + term)
                    search_rslt = myrecv(self.s)[1:].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'
                        
                elif my_msg[0] == 'p':
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, M_POEM + poem_idx)
                    poem = myrecv(self.s)[1:].strip()
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'
                        
                else:
                    self.out_msg += menu
                    
            if len(peer_msg) > 0:

                if peer_code == M_CONNECT:
                    self.peer = peer_msg
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer 
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING

                elif peer_code == G_AWAY:
                    self.game_peer = peer_msg
                    self.out_msg += '\nYou are playing with ' + self.game_peer + '.\n' + \
                                    "Gaming..."
                    gaming = game.GAME(self.s, True, False, self.me, self.game_peer)
                    gaming.start()

                elif peer_code == G_HOME:
                    self.game_peer = peer_msg
                    self.out_msg += '\n' + self.game_peer + ' accepted your request.\n'
                    self.out_msg += '\nYou are playing with ' + self.game_peer + '.\n' + \
                                    "Gaming..."
                    gaming = game.GAME(self.s, True, True, self.me, self.game_peer)
                    gaming.start()

                elif peer_code == G_DECLINE:
                    self.out_msg += 'Your game request is refused.'

                elif peer_code == M_QGAME:
                    if peer_msg == self.me:
                        self.out_msg += 'You left the game.\n'
                    else:
                        self.out_msg += peer_msg + " left the game.\n"

                elif peer_code == M_GAME_RQ:
                    self.game_peer = peer_msg
                    self.out_msg += self.game_peer + " invites you to play the game together!\n " + \
                                                       "(Reply 'Yes " + self.game_peer + "' to accept. " + \
                                                       "Reply 'No " + self.game_peer + "' to decline.)"
                    
#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # My stuff, going out
                mysend(self.s, M_EXCHANGE + "[" + self.me + "] " + my_msg)
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:   # Peer's stuff, coming in
                # New peer joins
                if peer_code == M_CONNECT:
                    self.out_msg += "(" + peer_msg + " joined)\n"
                else:
                    self.out_msg += peer_msg

            # I got bumped out
            if peer_code == M_DISCONNECT:
                self.state = S_LOGGEDIN

            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#==============================================================================
# invalid state                       
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)
            
        return self.out_msg