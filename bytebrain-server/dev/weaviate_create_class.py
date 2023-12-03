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
