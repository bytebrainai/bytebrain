# Copyright 2023-2024 ByteBrain AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import googleapiclient.discovery
import os
import json
from urllib.error import HTTPError


def list_of_channel_videos(channel_id: str):
    youtube = googleapiclient.discovery.build(
        'youtube',
        'v3',
        developerKey=os.environ["GOOGLE_API_KEY"]
    )

    cache_file = 'video_ids_cache.json'
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            cached_data = json.load(file)
        if channel_id in cached_data:
            return cached_data[channel_id]

    video_ids = []
    page_token = None

    try:
        while True:
            response = youtube.search().list(
                part='id',
                channelId=channel_id,
                maxResults=50,
                pageToken=page_token
            ).execute()

            for item in response['items']:
                if item['id']['kind'] == 'youtube#video':
                    video_ids.append(item['id']['videoId'])

            if 'nextPageToken' in response:
                page_token = response['nextPageToken']
            else:
                break

    except HTTPError:
        print(f'An HTTP error occurred')

    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            cached_data = json.load(file)
    else:
        cached_data = {}

    cached_data[channel_id] = video_ids

    with open(cache_file, 'w') as file:
        json.dump(cached_data, file)

    return video_ids
