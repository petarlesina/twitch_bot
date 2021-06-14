
import socket
import datetime
import pytz
import random
import time
from timeit import default_timer as timer
from collections import namedtuple
import config


Message = namedtuple(
    'Message',
    'prefix user channel irc_command irc_args text text_command text_args',
)



class Bot:
    def __init__(self):
        self.irc_server = 'irc.twitch.tv'
        self.irc_port = 6667
        self.oauth_token = config.OAUTH_TOKEN
        #self.username = 'BOT_NAME'  -- write bot username here

        #self.channels = ['STREAMER1', 'STREAMER2']  -- write names of the streamers here and uncomment
        
        self.custom_commands = {
            '!time': self.reply_with_time,
            'Kappa': self.post_kappa,
            'Mona': self.post_mona,
            
        }
        self.timer_start = timer()
        self.periodic_start = timer()

    def send_privmsg(self, channel, text):
        self.send_command(f'PRIVMSG #{channel} :{text}')

    def send_command(self, command):
        if 'PASS' not in command:
            print(f'< {command}')
        self.irc.send((command + '\r\n').encode())

    def connect(self):
        self.irc = socket.socket()
        self.irc.connect((self.irc_server, self.irc_port))
        self.send_command(f'PASS {self.oauth_token}')
        self.send_command(f'NICK {self.username}')
        for channel in self.channels:
            self.send_command(f'JOIN #{channel}')
        self.loop_for_messages()

    def get_user_from_prefix(self, prefix):
        domain = prefix.split('!')[0]
        if domain.endswith('.tmi.twitch.tv'):
            return domain.replace('.tmi.twitch.tv', '')
        if 'tmi.twitch.tv' not in domain:
            return domain
        return None

    def parse_message(self, received_msg):
        parts = received_msg.split(' ')

        prefix = None
        user = None
        channel = None
        text = None
        text_command = None
        text_args = None
        irc_command = None
        irc_args = None

        if parts[0].startswith(':'):
            prefix = parts[0][1:]
            user = self.get_user_from_prefix(prefix)
            parts = parts[1:]

        text_start = next(
            (idx for idx, part in enumerate(parts) if part.startswith(':')),
            None
        )
        if text_start is not None:
            text_parts = parts[text_start:]
            text_parts[0] = text_parts[0][1:]
            text = ' '.join(text_parts)
            text_command = text_parts[0]
            text_args = text_parts[1:]
            parts = parts[:text_start]

        irc_command = parts[0]
        irc_args = parts[1:]

        hash_start = next(
            (idx for idx, part in enumerate(irc_args) if part.startswith('#')),
            None
        )
        if hash_start is not None:
            channel = irc_args[hash_start][1:]

        message = Message(
            prefix=prefix,
            user=user,
            channel=channel,
            text=text,
            text_command=text_command,
            text_args=text_args,
            irc_command=irc_command,
            irc_args=irc_args,
        )

        return message


    def reply_with_time(self, message):
        formatted_date = datetime.datetime.now().strftime('%H:%M')
        text = f'Time  is {formatted_date}.'
        self.send_privmsg(message.channel, text)

    def post_kappa(self, message):
        text = f'Kappa'
        self.send_privmsg(message.channel, text)

    def post_mona(self, message):
        text = f'Mona is the best cat CoolCat'
        self.send_privmsg(message.channel, text)

    def handle_message(self, received_msg):
        if len(received_msg) == 0:
            return

        message = self.parse_message(received_msg)

        if message.irc_command == 'PING':
            self.send_command('PONG :tmi.twitch.tv')

        if message.irc_command == 'PRIVMSG' and message.user != self.username:

            if message.text_command in self.custom_commands:
                
                timer_end = timer()
                time_elapsed = timer_end - self.timer_start

                if(message.text_command == 'Kappa' and message.channel != 'STREAMER1'): ##change STREAMER1
                    if(time_elapsed > 60):
                        self.timer_start = timer()
                        time.sleep(1)
                        self.custom_commands[message.text_command](message)
                        

                elif(time_elapsed > 45 and message.channel == 'STREAMER1'): ##change STREAMER1
                    self.timer_start = timer()
                    time.sleep(1)
                    self.custom_commands[message.text_command](message)

                if(message.text_command == 'Kappa'):
                    self.periodic_start = timer()
        
        
        periodic_end = timer()
        # print("channel =", message.channel, "end = ", periodic_end, " start = ", self.periodic_start)  --this is just for testing purposes
        if(periodic_end - self.periodic_start > 3600):
            self.periodic_start = timer()
            time.sleep(5)
            text = f'Kappa'
            self.send_privmsg(message.channel, text)
            

    def loop_for_messages(self):

        while True:
            received_msgs = self.irc.recv(2048).decode()
            for received_msg in received_msgs.split('\r\n'):
                self.handle_message(received_msg)


def main():
    bot = Bot()
    bot.connect()

if __name__ == '__main__':
    main()