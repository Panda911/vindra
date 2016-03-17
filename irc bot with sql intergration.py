import socket, MySQLdb
from time import strftime

def contains(str, test):
    for c in range(len(str)-len(test)+1):
        if test == str[c:c+len(test)]:
            return True
    return False

def debug(message):
    if debug:
        print message

debug = True
network = 'chat.freenode.net'
port = 6667
irc = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
username = ''
door = 0
debug_prefix = '[DEBUG]: '

# db = MySQLdb.connect('localhost', 'root', 'toor', 'vindra')
db = MySQLdb.connect('localhost', 'root', 'toor', 'vindra')
cursor = db.cursor()

print ("Starting up...")
irc.connect ( ( network, port ) )
#print irc.recv ( 4096 )
irc.send ( 'NICK vindra\r\n' )
irc.send ( 'USER vindra vindra vindra :Python IRC\r\n' )
irc.send ( 'JOIN #hacklabto\r\n' )
print ("Connected!")

while True:
    data = irc.recv ( 4096 )
    debug("baud: 4096")
    if data.find ( 'PING' ) != -1:
        irc.send ( 'PONG ' + data.split() [ 1 ] + '\r\n' )
    if data.find ( 'doorbot'):
        debug(debug_prefix + 'Got Message: ' + str(data)) # echo35 debug
        if data.find ( 'HackLab' ):
            split = data.split('hacklabto :')
            message = str(data).split("#")
            if (len(message) > 1):
                message = message[1].replace('hacklabto :', '').replace(' has', '').replace(' Classroom.', '').replace(' HackLab.', '').replace(' HackLab', '').replace('\r\n', '')
                if contains(message, "left"):
                    debug(debug_prefix + "Got alias leaving: " + message.replace(' left', ''))
                    username = message.replace(' left', '')
                    query = "INSERT INTO test(username, str) VALUES('%s', '%s')" % (username, "EXIT") #FINISH WRITING PROPER MYSQL QUERY - ECHO35
                    cursor.execute(query)
                    db.commit()
                elif contains(message, "entered"):
                    debug(debug_prefix + "Got alias entering: " + message.replace(' entered', ''))
                    username = message.replace(' entered', '')
                    query = "INSERT INTO test(username, str) VALUES('%s', '%s')" % (username, "ENTER")
                    cursor.execute(query)
                    db.commit()

