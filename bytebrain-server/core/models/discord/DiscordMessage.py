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

import json
from datetime import datetime


class DiscordMessage:
    def __init__(self, id: int, user: str, created_at: datetime, content):
        self.id = id
        self.user = user
        self.created_at = created_at
        self.content = content

    def __str__(self):
        return f"Message(is: {self.id}, user: {self.user}, created_at: {self.created_at}, content: '{self.content}')"

    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user,
            "created_at": self.created_at.isoformat(),
            "content": self.content
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        created_at = datetime.fromisoformat(data["created_at"])
        return cls(data["id"], data["user"], created_at, data["content"])
