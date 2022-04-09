import logging
import json
from platform import platform
from jinja2 import Template
import sys

platform_config = json.loads(open('platform_config.json').read())

logging.basicConfig(level=logging.INFO)

server_list  = sys.argv[1]
logging.info('Reading ' + server_list)
servers = json.loads(open(server_list).read())

def render_template(template_file, output_file, workers):
    with open(template_file) as f:
        template = Template(f.read())
    with open(output_file, 'w') as f:
        f.write(template.render(servers=workers))

def generate_config():
    workers = []
    for worker in servers['workers']:
        temp = {}
        temp['name'] = worker['user']
        temp['ip'] = worker['ip']
        workers.append(temp)
    if server_list == 'dynamic_servers.json':
        for worker in platform_config['workers']:
            temp = {}
            temp['name'] = worker['user']
            temp['ip'] = worker['ip']
            workers.append(temp)
    render_template('haproxy.j2', 'haproxy.cfg', workers=workers)

generate_config()