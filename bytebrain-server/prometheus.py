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

import os
import yaml


def configure():
    with open('prometheus.template.yml', 'r') as file:
        config = yaml.safe_load(file)

    password = os.environ.get('PROMETHEUS_REMOTE_WRITE_PASSWORD')
    username = os.environ.get('PROMETHEUS_REMOTE_WRITE_USERNAME')
    url = os.environ.get('PROMETHEUS_REMOTE_WRITE_URL')

    if not password or not username or not url:
        raise Exception('One or more environment variables are not set (PROMETHEUS_REMOTE_WRITE_*)')

    config['remote_write'][0]['basic_auth']['password'] = password
    config['remote_write'][0]['basic_auth']['username'] = username
    config['remote_write'][0]['url'] = url

    with open('prometheus.yml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
