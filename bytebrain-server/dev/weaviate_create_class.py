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

from weaviate import Tenant
from weaviate import Client
from config import load_config

config = load_config()

weaviate_client = Client(url=config.weaviate_url)
weaviate_client.schema.create_class({
    'class': 'BB',
    'multiTenancyConfig': {'enabled': True}
})

weaviate_client.schema.add_class_tenants(
    class_name='B',  # The class to which the tenants will be added
    tenants=[Tenant(name='fooo'), Tenant(name='baar')]
)
