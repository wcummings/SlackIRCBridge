from twisted.words.protocols import irc

class IRCUser(irc.IRC):

    def connectionMade(self):
        irc.IRC.connectionMade(self)
        self.factory.connections.append(self)

    def connectionLost(self, reason):
        irc.IRC.connectionLost(self, reason)        
        self.factory.connections.remove(self)
        
    def irc_unknown(self, prefix, command, params):
        print "Unknown command: %s (%s)" % (command, params)
        self.sendCommand(irc.ERR_UNKNOWNCOMMAND, (command, ":Unknown command"))

    def irc_NICK(self, prefix, params):
        import json
        self.nick = params[0]
        self.sendMessage(irc.RPL_WELCOME, self.nick, ":Welcome to the Internet Relay Network %s" % self.nick)
        self.sendMessage(irc.RPL_YOURHOST, ":Your host is IRCSlackBridge, running version alpha")
        self.sendMessage(irc.RPL_CREATED, ":This server always was created on %s" % self.factory.creationTime)
        self.sendMessage(irc.RPL_MYINFO, ":IRCSlackBridge alpha w n")

    def irc_PRIVMSG(self, prefix, params):
        channel = params[0].replace("#", "")
        text = params[1]
        self.factory.slackProtocol.sendChatMessage(text, channel=channel)
        
    def irc_JOIN(self, prefix, params):
        for channel in self.factory.slackProtocol.meta.channels.values():
            if channel['name'] == params[0].replace("#", ""):
                topic = channel['topic']['value']
                self.topic(self.nick, '#' + channel['name'], topic)
                return
    
    def irc_PING(self, prefix, params):
        self.sendLine("PONG %s" % params[-1])        
