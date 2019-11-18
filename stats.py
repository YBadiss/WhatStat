from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

from emoji import UNICODE_EMOJI
from textblob import Blobber
from textblob_fr import PatternTagger, PatternAnalyzer

from utils import str_to_dict, top, group_adjacent_dates


def compute_stats(grouped_messages):
    # CPU bound, use process pool
    all_messages = [m for ms in grouped_messages.values() for m in ms]
    with ProcessPoolExecutor(max_workers=4) as executor:
        users = dict(list(
            executor.map(
                _user_stats,
                (list(grouped_messages.items()) +
                 [('__group__', all_messages)])
            )
        ))
    group = users.pop('__group__')
    return {
        'group': group,
        'users': users
    }


def _user_stats(args):
    user, messages = args
    return (user, {name: fn(messages) for name, fn in _stat_functions.items()})


def _compute_sentiment(messages):
    sentiments = [
        (_text_blobber(message.text).sentiment[0], message.text)
        for message in messages
    ]
    return {
        'mean': sum(v for v, _ in sentiments) / len(sentiments),
        'positive': len([v for v, _ in sentiments if v > 0.1]),
        'most_positive': max(sentiments),
        'negative': len([v for v, _ in sentiments if v < -0.1]),
        'most_negative': min(sentiments),
        'neutral': len([v for v, _ in sentiments if v >= -0.1 and v <= 0.1]),
    }


def _compute_emojis(messages):
    full_text = '\n'.join([m.text for m in messages])
    emojis = str_to_dict(full_text, _emoji_set)
    return {
        'count': sum(emojis.values()),
        'most_used': top((c, e) for e, c in emojis.items()) if emojis else None
    }


def _compute_sharing(messages):
    sharing_types = {
        'GIF omitted': 'GIF',
        'image omitted': 'Image',
        'video omitter': 'Video',
        'audio omitted': 'Audio',
        'Location: ': 'Location'
    }
    shares = {v: 0 for v in sharing_types.values()}
    for message in messages:
        text = message.text
        for k, v in sharing_types.items():
            if k in text:
                shares[v] += 1
                break
    return shares


def _compute_activity(messages):
    grouped_by_date = defaultdict(int)
    for m in messages:
        grouped_by_date[m.date.date()] += 1
    activity_per_day = [(v, d) for d, v in grouped_by_date.items()]
    return {
        'activity_per_day': sorted([(d, v) for v, d in activity_per_day]),
        'num_active_days': len(activity_per_day),
        'most_active_days': top(activity_per_day),
        'longest_streak': max(group_adjacent_dates([d for _, d in activity_per_day]))
    }


_text_blobber = Blobber(pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())
_emoji_set = set(UNICODE_EMOJI)
_stat_functions = {
    'start': lambda messages: min(messages, key=lambda m: m.date).date,
    'end': lambda messages: max(messages, key=lambda m: m.date).date,
    'num_lines': lambda messages: sum(m.num_lines for m in messages),
    'num_messages': lambda messages: len(messages),
    'num_characters': lambda messages: sum(m.num_characters for m in messages),
    'emojis': _compute_emojis,
    'sentiment': _compute_sentiment,
    'sharing': _compute_sharing,
    'activity': _compute_activity
}
