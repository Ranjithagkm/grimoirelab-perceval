# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2017 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1335, USA.

## Its WIP file, there is a lot more that needs to be done to make it work

import json
import logging
import time
import os

import requests

from grimoirelab.toolkit.datetime import datetime_to_utc, str_to_datetime
from grimoirelab.toolkit.uris import urijoin

from ...backend import (Backend,
                        BackendCommand,
                        BackendCommandArgumentParser)
from ...client import HttpClient, RateLimitHandler

from ...utils import DEFAULT_DATETIME

TWITTER_URL = "https://api.twitter.com/1.1/search/tweets.json?q="
DEFAULT_HASHTAG = "#perceval"

CATEGORY_TWEET = "tweet"

logger = logging.getLogger(__name__)

class twitter(Backend):
    """Twitter backend for perceval.

    This class allows the fetch of tweets with a hashtag

    :param hashtag: hashtag to be searched

    """
    version = '0.15.2'

    CATEGORIES = [CATEGORY_TWEET]

    def __init__(self,tag=None, archive=None, hash_tag=DEFAULT_HASHTAG, file_path=None):

        hashtag = DEFAULT_HASHTAG
        origin = TWITTER_URL
        super().__init__(origin, tag=tag, archive=archive)

        self.hash_tag = hash_tag
        self.file_path = file_path

        self.client = None

    def fetch(self, category=CATEGORY_TWEET):
        """Fetch the tweets.

        The method retrieves the search results of a hashtag.

        :returns: a generator of tweets
        """

        kwargs =  {}
        items = super().fetch(category, **kwargs)

        return items

    def fetch_items(self, category, **kwargs):
        """Fetch the tweet text

        :param category: the category of items to fetch
        :param kwargs: backend arguments

        :returns: a generator of items
        """
        if os.path.isfile(self.file_path):
            raw_json = open(self.file_path).read()
        else:
            raw_json = self.client.getTweets(self.hash_tag)
        jsonfmt = json.loads(raw_json)
        statuses = jsonfmt["statuses"]
        for tweet in statuses:
            yield tweet["text"]

    @classmethod
    def has_archiving(cls):
        """Returns whether it supports archiving items on the fetch process.

        :returns: this backend supports items archive
        """
        return False

    @classmethod
    def has_resuming(cls):
        """Returns whether it supports to resume the fetch process.

        :returns: this backend supports items resuming
        """
        return True

    @staticmethod
    def metadata_id(item):
        """Extracts the identifier from an item."""

        return str(item['id'])

    @staticmethod
    def metadata_updated_on(item):
        """Extracts the update time from an item.

        The timestamp used is extracted from 'updated_at' field.
        This date is converted to UNIX timestamp format.

        :param item: item generated by the backend

        :returns: a UNIX timestamp
        """
        ts = item['created_at']
        ts = str_to_datetime(ts)

        return ts.timestamp()

    @staticmethod
    def metadata_category(item):
        """Extracts the category from an item.

        This backend only generates one type of item which is
        'issue'.
        """
        return CATEGORY_TWEET

    def _init_client(self, from_archive=False):
        """Init client"""

        return twitterClient(self.archive, from_archive)


class twitterClient(HttpClient):
    """Client for retieving information from Twitter API"""

    def __init__(self, hash_tag=DEFAULT_HASHTAG, archive=None, from_archive=False):
        super().__init__(TWITTER_URL, archive=archive, from_archive=from_archive)
        self.hash_tag = hash_tag

    def getTweets(self, hash_tag=DEFAULT_HASHTAG):
        print (hash_tag)
        url = TWITTER_URL + str(hash_tag)

        r = self.fetch(url)

        return r.text

class twitterCommand(BackendCommand):
    """Class to run twitter backend from the command line."""

    BACKEND = twitter

    @staticmethod
    def setup_cmd_parser():
        """Returns the twitter argument parser."""

        parser = BackendCommandArgumentParser(token_auth=True,
                                              archive=True)

        # twitter options
        group = parser.parser.add_argument_group('twitter arguments')
        group.add_argument('--hash-tag', dest='hash_tag',
                           default=DEFAULT_HASHTAG,
                           help="Hash tag to be searched")
        group.add_argument('--file-path', dest='file_path',
                           help="File to be searched")
        return parser
