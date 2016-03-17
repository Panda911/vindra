import socket, MySQLdb, os, commands

from time import strftime

# Checks if $str contains the character sequence supplied as $test.
# Returns Boolean
def contains(str, test):
    for c in range(len(str)-len(test)+1):
        if test == str[c:c+len(test)]:
            return True
    return False

# Detects enter/leave messages from irc-data and parses various variables.
# Void Function
def parse(data):
    # debug(debug_prefix + 'Got Message: ' + str(data)) # echo35 debug
    split = data.split('hacklabto :')
    message = str(data).split("#")
    if (len(message) > 1):
        message = message[1].replace('hacklabto :', '').replace(' has', '').replace(' Classroom.', '').replace(' HackLab.', '').replace(' HackLab', '').replace('\r\n', '')
        if contains(message, "left"):
            debug(debug_prefix + "Got alias leaving: " + message.replace(' left', ''))
            username = message.replace(' left', '')
            date = current_date()
            time = current_time()
            temperature = current_temperature()
            weather = current_weather()
            commit_master(username, "exit", date, time, temperature, weather)

        elif contains(message, "entered"):
            debug(debug_prefix + "Got alias entering: " + message.replace(' entered', ''))
            username = message.replace(' entered', '')
            date = current_date()
            time = current_time()
            temperature = current_temperature()
            weather = current_weather()
            commit_master(username, "enter", date, time, temperature, weather)

# Returns current system time.
# Format defined in vindra.cfg
# Returns String
def current_time():
    global time_format
    return strftime(time_format)

# Returns current system date.
# Format defined in vindra.cfg
# Returns String
def current_date():
    global date_format
    return strftime(date_format)

# Returns current outside temperature (Celcius).
# Region defined in vindra.cfg
# Returns String
def current_temperature():
    global weather_url, absolute_temperature_cmd
    return run_shell(absolute_temperature_cmd % weather_url)

# Returns current outside weather (As Short Sentence)
# Region defined in vindra.cfg
# Returns String
def current_weather():
    global weather_url, weather_cmd
    return run_shell(weather_cmd % weather_url)

# Commits user data to the SQL database.
# Void Function
def commit_master(username, action, date, time, temp, weather):
    global sql_table, db
    query = "INSERT INTO %s (username, action, date, time, temperature, weather) VALUES ('%s', '%s', '%s', '%s', '%s', '%s');" % (sql_table, username, action, date, time, temp, weather)
    debug(query)
    db.cursor().execute(query)
    db.commit()

# Prints $message only if $debug_enabled is True.
# Void Function
def debug(message):
    if debug_enabled:
        print message

# Runs $command under bash and returns output.
# UNIX Systems Only.
# Returns String
def run_shell(command):
    return commands.getstatusoutput(command)[1]

# Creates configuration file if not already done.
# Returns Boolean
def create_config():
    if os.path.exists('vindra.cfg'):
        return False
    file = open('vindra.cfg', 'w+')
    file.writelines(default_config)
    return True

# Parses configuration file and loads values into global constants.
# Void Function
def load_config():
    global date_format, time_format, irc_server, irc_port, irc_channel, irc_alias, sql_server, sql_user, sql_pass, sql_database, sql_table, weather_url
    file = open('vindra.cfg', 'r')
    for line in file:
        try:
            if line[:12] == ('date_format='):
                date_format = line[12:].replace('"', '').replace('\n', '')
            elif line[:12] == ('time_format='):
                time_format = line[12:].replace('"', '').replace('\n', '')
            elif line[:11] == ('irc_server='):
                irc_server = line[11:].replace('"', '').replace('\n', '')
            elif line[:12] == ('irc_channel='):
                irc_channel = line[12:].replace('"', '').replace('\n', '')
            elif line[:9] == ('irc_port='):
                irc_port = int(line[9:].replace('\n', ''))
            elif line[:13] == ('irc_nickname='):
                irc_alias = line[13:].replace('"', '').replace('\n', '')
            elif line[:11] == ('sql_server='):
                sql_server = line[11:].replace('"', '').replace('\n', '')
            elif line[:13] == ('sql_username='):
                sql_user = line[13:].replace('"', '').replace('\n', '')
            elif line[:13] == ('sql_password='):
                sql_pass = line[13:].replace('"', '').replace('\n', '')
            elif line[:13] == ('sql_database='):
                sql_database = line[13:].replace('"', '').replace('\n', '')
            elif line[:10] == ('sql_table='):
                sql_table = line[10:].replace('"', '').replace('\n', '')
            elif line[:12] == ('weather_url='):
                weather_url = line[12:].replace('"', '').replace('\n', '')

        except:
            continue

# The main code. Will operate the actual bot.
# Void Function
def run():
    global db
    if create_config():
        print "Created Configuration File. Please review it and relaunch the bot afterwards."
        exit()
    try:
        print ("Reading Configuration File..."),
        load_config()

        print ("Done!\nConnecting to DB '%s' on server '%s' with user '%s'..." % (sql_database, sql_server, sql_user)),
        db = MySQLdb.connect(sql_server, sql_user, sql_pass, sql_database)


        print "Done!\nConnecting to IRC Server '%s:%d'..." % (irc_server, irc_port),
        irc.connect ( ( irc_server, irc_port ) )

        print "Done!\nSetting nick to '%s'..." % (irc_alias),
        irc.send ('NICK %s\r\n' % irc_alias)
        irc.send ('USER %s %s %s :Python IRC\r\n' % (irc_alias, irc_alias, irc_alias))

        print "Joining channel '%s'..." % (irc_channel),
        irc.send ( 'JOIN %s\r\n' % irc_channel )

        print ("Done!\nVindra Bot is ready!")

        while True:
                data = irc.recv ( 4096 )
                if data.find ( 'PING' ) != -1:
                    irc.send ( 'PONG ' + data.split() [ 1 ] + '\r\n' )
                if data.find ( 'doorbot'):
                    if data.find ( 'HackLab' ):
                        parse(data)
    except:
        print("\nError has occured. Terminating...")
        exit()

# Start: Global Constants

debug_enabled = True
default_config = [('# Vindra Bot Configuration File\n'), '\n', '# Formatting Templates\n', 'date_format="%y-%m-%d"\n', 'time_format="%H:%M:%S"\n', '\n', '# URL Definitions\n', '# Get your local weather_url by searching your city at http://www.accuweather.com and pasting the url into this config.\n', 'weather_url="http://www.accuweather.com/en/ca/toronto/m5g/weather-forecast/55488"\n', '\n', '# IRC Details\n', 'irc_server="chat.freenode.com"\n', 'irc_port=6667\n', 'irc_channel="#irc"\n', 'irc_nickname=""\n', '\n', '# MySQL Server Details\n', 'sql_server="127.0.0.1"\n', 'sql_username="root"\n', 'sql_password=""\n', 'sql_database="vindra"\n', 'sql_table="data"\n', '\n']

date_format = ''
time_format = ''

irc_server = ''
irc_port = 0
irc_channel = ''
irc_alias = ''

sql_server = ''
sql_user = ''
sql_pass = ''
sql_database = ''
sql_table = ''

weather_url = ''
absolute_temperature_cmd = 'URL=\'%s\'; wget -q -O- "$URL" | awk -F\\\' \'/acm_RecentLocationsCarousel\.push/{print ""$10"" }\'| head -1'
perceived_temperature_cmd = 'URL=\'%s\'; wget -q -O- "$URL" | awk -F\\\' \'/acm_RecentLocationsCarousel\.push/{print ""$12"" }\'| head -1'
weather_cmd = 'URL=\'%s\'; wget -q -O- "$URL" | awk -F\\\' \'/acm_RecentLocationsCarousel\.push/{print ""$14"" }\'| head -1'

debug_prefix = '[DEBUG]: '

# End: Global Constants

# Start: Global Variables

db = None
irc = socket.socket (socket.AF_INET, socket.SOCK_STREAM)

# End: Global Variables

run()