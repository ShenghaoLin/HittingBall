import time
import socket
import select
import sys
import string
import indexer
import pickle as pkl
from chat_utils import *
import chat_group as grp

class Server:
    def __init__(self):
        self.new_clients = [] #list of new sockets of which the user id is not known
        self.logged_name2sock = {} #dictionary mapping username to socket
        self.logged_sock2name = {} # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        #start server
        self.server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        #initialize past chat indices
        self.indices={}
        #sonnet indexing
        self.sonnet = indexer.PIndex("AllSonnets.txt")
        
    def new_client(self, sock):
        #add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def login(self, sock):
        #read the msg that should have login code plus username
        msg = myrecv(sock)
        if len(msg) > 0:
            code = msg[0]

            if code == M_LOGIN:
                name = msg[1:]
                if self.group.is_member(name) != True:
                    #move socket from new clients list to logged clients
                    self.new_clients.remove(sock)
                    #add into the name to sock mapping
                    self.logged_name2sock[name] = sock
                    self.logged_sock2name[sock] = name
                    #load chat history of that user
                    if name not in self.indices.keys():
                        try:
                            self.indices[name]=pkl.load(open(name+'.idx','rb'))
                        except IOError: #chat index does not exist, then create one
                            self.indices[name] = indexer.Index(name)
                    print(name + ' logged in')
                    self.group.join(name)
                    mysend(sock, M_LOGIN + 'ok')
                else: #a client under this name has already logged in
                    mysend(sock, M_LOGIN + 'duplicate')
                    print(name + ' duplicate login attempt')
            else:
                print ('wrong code received')
        else: #client died unexpectedly
            self.logout(sock)

    def logout(self, sock):
        #remove sock from all lists
        name = self.logged_sock2name[sock]
        pkl.dump(self.indices[name], open(name + '.idx','wb'))
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()

#==============================================================================
# main command switchboard
#==============================================================================
    def handle_msg(self, from_sock):
        #msg is the string sent by the client state machine: IMPORTANT
        msg = myrecv(from_sock)
        if len(msg) > 0:
            code = msg[0]           
#==============================================================================
#             handle connect request: this is implemented for you
#==============================================================================
            if code == M_CONNECT:
                to_name = msg[1:]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = M_CONNECT + 'hey you'
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = M_CONNECT + 'ok'
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, M_CONNECT + from_name)
                else:
                    msg = M_CONNECT + 'no_user'
                mysend(from_sock, msg)
#==============================================================================
#             handle multicast message exchange; IMPLEMENT THIS    
#==============================================================================
            elif code == M_GAME:
                to_name = msg[1:]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = M_GAME + 'You'
                    print('Game starts..')
                elif self.group.is_member(to_name):
                    b, g = self.group.find_group(to_name)
                    if not b:
                        msg = M_GAME + 'ok'
                        mysend(self.logged_name2sock[to_name], M_GAME_RQ + from_name)
                else:
                    msg = M_GAME + 'gg'
                mysend(from_sock, msg)

            elif code == G_REPLY:
                to_name = msg[2:].strip()
                if msg[1] == 'Y':
                    from_name = self.logged_sock2name[from_sock]
                    self.group.connect(from_name, to_name)
                    to_sock = self.logged_name2sock[to_name]
                    mysend(to_sock, G_HOME + from_name)
                    mysend(from_sock, G_AWAY + to_name)
                    print('Game starts..')
                elif msg[1] == 'N':
                    from_name = self.logged_sock2name[from_sock]
                    to_sock = self.logged_name2sock[to_name]
                    mysend(to_sock, G_DECLINE + from_name)

            elif code == M_EXCHANGE:
                from_name = self.logged_sock2name[from_sock]
                # Finding the list of people to send to
                the_guys = self.group.list_me(from_name)[1:]
                mes = msg[1:]
                self.indices[from_name].add_msg_and_index(mes)
                for g in the_guys:
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, msg)

            elif code == M_INGAME:
                from_name = self.logged_sock2name[from_sock]
                b, g = self.group.find_group(from_name)
                if b:
                    the_guy = self.group.list_me(from_name)[1]
                    mysend(self.logged_name2sock[the_guy], msg)

            elif code == M_QGAME:
                from_name = self.logged_sock2name[from_sock]
                the_guy = self.group.list_me(from_name)[1]
                mysend(self.logged_name2sock[the_guy], msg)
                time.sleep(0.2)
                mysend(self.logged_name2sock[the_guy], msg + from_name)
                mysend(from_sock, msg + from_name)
                self.group.disconnect(from_name)
#==============================================================================
#             listing available peers; IMPLEMENT THIS
#==============================================================================
            elif code == M_LIST:
                from_name = self.logged_sock2name[from_sock]
                msg = self.group.list_all()
                mysend(from_sock, msg)
#==============================================================================
#             retrieve a sonnet; IMPLEMENT THIS
#==============================================================================
            elif code == M_POEM:
                t = msg[1:].strip()
                try:
                    poem_indx = int(t)
                    from_name = self.logged_sock2name[from_sock]
                    poem = self.sonnet.get_poem(poem_indx)
                    msg = ' '
                    for i in poem:
                        msg += i + '\n'
                    mysend(from_sock, M_POEM + msg)
                except:
                    mysend(from_sock, M_POEM)

#==============================================================================
#             retrieve the time; IMPLEMENT THIS
#==============================================================================
            elif code == M_TIME:
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, ctime)

#==============================================================================
#             search handler; IMPLEMENT THIS
#==============================================================================
            elif code == M_SEARCH:
                from_name = self.logged_sock2name[from_sock]
                term = msg[1:].strip()
                search_rslt = self.indices[from_name].search(term)
                msg = ' '
                for i in search_rslt:
                    msg += i[1] + '\n'
                mysend(from_sock, M_SEARCH + msg)

            elif code == M_HISTORY:
                from_name = self.logged_sock2name[from_sock]
                op = msg[1:].strip()
                try:
                    infile = open(from_name + '.dat', 'rb')
                    dic = pkl.load(infile)
                    infile.close()
                    if op in dic.keys():
                        m = ''
                        for i in range(len(dic[op])):
                            tmp = str(dic[op][i][0]) + ' : ' + str(dic[op][i][1])
                            m += tmp + '\n'
                        mysend(from_sock, M_HISTORY + m)
                    else:
                        mysend(from_sock, M_HISTORY + 'You have not yet played with ' + op + '.')
                except IOError:
                    mysend(from_sock, M_HISTORY + 'You have not yet played a game!')

#==============================================================================
#             the "from" guy has had enough (talking to "to")!
#==============================================================================
            elif code == M_DISCONNECT:
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, M_DISCONNECT)
#==============================================================================
#                 the "from" guy really, really has had enough
#==============================================================================
            elif code == M_LOGOUT:
                self.logout(from_sock)
        else:
            #client died unexpectedly
            self.logout(from_sock)   

#==============================================================================
# main loop, loops *forever*
#==============================================================================
    def run(self):
        print ('starting server...')
        while(1):
           read,write,error=select.select(self.all_sockets,[],[])
           print('checking logged clients..')
           for logc in list(self.logged_name2sock.values()):
               if logc in read:
                   self.handle_msg(logc)
           print('checking new clients..')
           for newc in self.new_clients[:]:
               if newc in read:
                   self.login(newc)
           print('checking for new connections..')
           if self.server in read :
               #new client request
               sock, address=self.server.accept()
               self.new_client(sock)
           
def main():
    server=Server()
    server.run()

main()
