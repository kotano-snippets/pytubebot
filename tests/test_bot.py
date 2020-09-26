import os
from pathlib import Path
from unittest.mock import Mock

import pytest

import bot as b

FIXTURES = Path(__file__).parent / 'fixtures'

test_token = b.config["test_token"]
test_chat = b.config["test_chat_id"]

shorty1 = 'https://youtu.be/tPEE9ZwTmy0'
shorty12 = 'https://youtu.be/PPFVK3sV8Zk'

replies = b.replies


@ pytest.fixture
def fixt_message():
    # Send message to have link to message_id.
    message = b.bot.send_message(test_chat, "Test")
    msg = Mock()
    msg.__dict__.update(message.__dict__)
    return msg


@ pytest.fixture(scope='module')
def fixt_shortvideos():
    fpath = FIXTURES / "ShortestVideoOnYoutube.mp4"
    fpath2 = FIXTURES / "ShortestVideoOnYoutubePart12.mp4"
    return (fpath.open('rb').read(), fpath2.open('rb').read(),)


def test_get_help(fixt_message):
    expected = replies["help"]
    got = b.send_help(fixt_message).text
    assert got == expected


def test_download_video(fixt_shortvideos):
    expected = fixt_shortvideos[0]
    vpath = str(Path(b.download_video(shorty1)))
    got = open(vpath, 'rb').read()
    assert got == expected
    os.remove(vpath)


def test_handle_youtuble_links(fixt_message, fixt_shortvideos):
    expected1, expected2 = fixt_shortvideos
    # We give two valid and one invalid arguments.
    fixt_message.text = "{} {} {}".format(shorty1, 'youtube', shorty12)
    got = b.handle_youtube_link(fixt_message)
    # Function must drop invalid arguments.
    assert len(got) == 2
    got1 = b.get_video_from_tg(got[0]).content
    got2 = b.get_video_from_tg(got[1]).content
    assert (expected1, expected2) == (got1, got2)
