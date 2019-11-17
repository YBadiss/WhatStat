from collections import defaultdict
import re
from typing import Dict, List

import pendulum


class User:
    # '\u202a+33\xa06\xa040\xa011\xa083\xa032\u202c'
    PHONE_NUMBER_REGEX = re.compile(r'.(\+\d+).(\d+).(\d+).(\d+).(\d+).(\d+)')

    def __init__(self, name, user_number_map):
        self.is_number = False
        self.name = name
        phone_number_match = self.PHONE_NUMBER_REGEX.match(self.name)
        if phone_number_match:
            self.name = ' '.join(phone_number_match.groups())
            if self.name in user_number_map:
                self.name = user_number_map[self.name]
            else:
                self.is_number = True

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, user):
        return isinstance(user, User) and user.name == self.name


class Message:
    FULL_MESSAGE_REGEX = re.compile(
        r'.*?\[(?P<date>.+?)\] (?P<user>.+?): (?P<message>.+)'
    )
    LINE_CONTINUATION_REGEX = re.compile(r'^[^\[\]]+$')

    @staticmethod
    def parse_chat(chat, user_number_map) -> Dict[User, List['Message']]:
        grouped_messages = defaultdict(lambda: [])
        previous_message = None
        for i, line in enumerate(chat):
            message = Message.from_line(line, user_number_map)
            if message:
                grouped_messages[message.user].append(message)
                previous_message = message
            elif Message.is_line_continuation(line):
                previous_message._text.append(line)
        return grouped_messages

    @staticmethod
    def from_line(line, user_number_map):
        match = Message.FULL_MESSAGE_REGEX.match(line)
        if match:
            return Message(
                line,
                match.group('message'),
                match.group('date'),
                match.group('user'),
                user_number_map)

    @staticmethod
    def is_line_continuation(line):
        return Message.LINE_CONTINUATION_REGEX.match(line) is not None

    def __init__(self, line, message, date, user, user_number_map):
        self._text = [line]
        self.message = message
        self.date = date
        self.user = User(user, user_number_map)
        if self.date:
            self.date = pendulum.from_format(self.date, 'DD/MM/YYYY, HH:mm:ss')

    @property
    def text(self):
        return '\n'.join(self._text)

    @property
    def num_lines(self):
        return len(self._text)

    @property
    def num_characters(self):
        return sum(len(line) for line in self._text)
