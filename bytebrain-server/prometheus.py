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
