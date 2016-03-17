import socket

def contains(str, test):
    for c in range(len(str)-len(test)+1):
        if test == str[c:c+len(test)]:
            return True
    return False

network = 'chat.freenode.net'
port = 6667
irc = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
username = ''
door = 0
debug_prefix = '[DEBUG]: '
irc.connect ( ( network, port ) )
#print irc.recv ( 4096 )
irc.send ( 'NICK vindra\r\n' )
irc.send ( 'USER vindra vindra vindra :Python IRC\r\n' )
irc.send ( 'JOIN #hacklabto\r\n' )
while True:
    data = irc.recv ( 4096 )
    if data.find ( 'PING' ) != -1:
        irc.send ( 'PONG ' + data.split() [ 1 ] + '\r\n' )
    if data.find ( 'doorbot'):

        # print 'Data: ' + str(data) # echo35 debug

        if data.find ( 'HackLab' ):
            split = data.split('hacklabto :')
            message = str(data).split("#")
            if (len(message) > 1):
                message = message[1].replace('hacklabto :', '').replace(' has', '').replace(' Classroom.', '').replace(' HackLab.', '').replace(' HackLab', '').replace('\r\n', '')
                if contains(message, "left"):
                    print debug_prefix + " Got alias leaving: " + message.replace(' left', '')
                elif contains(message, "entered"):
                    print debug_prefix + " Got alias entering: " + message.replace(' entered', '')

