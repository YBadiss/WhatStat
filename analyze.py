import json
from pprint import pprint

from message import Message
from stats import compute_stats
from utils import time_it

# TODO
# FEATURES
# ACTIVITY BY TIME OF DAY at what time were you the most active
# AVERAGES words/letters/messages per message and per day
#
# DONE
# 3. Fast parse of dates (maybe preparse and replace dates with timestamps)
# 1. Combine multi line messages
# 4. Map phone numbers to users
# 2. Extract emojis
# 5. Sentiment analysis
# FILES AND LOCATIONS # of images, videos, voicemessages and locations
#   GIF omitted
#   image omitted
#   video omitted
#   audio omitted
#   ‎Contact card omitted
#   Location: https://maps.google.com/?q=-13.523442,-71.950256
# TIMESPAN: how long did the chat go
# TIMELINE: when and how much you where messaging
# TOTAL NUMBERS days you are chatting, message/word/letter count
# TOPS most active day


if __name__ == "__main__":
    with time_it('Reading'):
        with open('_chat.txt', 'r') as f:
            chat = f.readlines()
        with open('numbers.json', 'r') as f:
            user_number_map = json.load(f)

    with time_it('Parsing'):
        grouped_messages = Message.parse_chat(chat, user_number_map)

    with time_it('Stats'):
        pprint(compute_stats(grouped_messages))
