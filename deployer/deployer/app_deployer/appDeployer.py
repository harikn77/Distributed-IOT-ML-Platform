from cmath import log
import json
from deployer import module_config
import logging
logging.basicConfig(level=logging.INFO)


def run(package, sensor_id):
    import zipfile
    with zipfile.ZipFile(package, 'r') as zip_ref:
        zip_ref.extractall('/tmp/app_deployer')
    logging.info('Extracted package: ' + package)
    contract = json.load(open('/tmp/app_deployer/app/app_contract.json'))

    container_name = contract['name']
    # generate getdata.py inside app/src
    sensorStub = ''
    sensorStub += "import requests\n"
    sensorStub += "import json\n"
    sensorStub += 'def get_data():\n'
    sensorStub += '    url = "{}/{}"\n'.format(module_config['sensor_api'], sensor_id)
    sensorStub += "    r = requests.get(url)\n"
    sensorStub += "    return json.loads(r.text)\n"
    logging.info('Generated getdata.py')
    with open('/tmp/app_deployer/app/src/getdata.py', 'w') as f:
        f.write(sensorStub)
    logging.info('Wrote getdata.py')

    dockerfile = """FROM python:3
ADD app app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python3", "src/app.py","model_contract.json"]"""

    with open('/tmp/app_deployer/Dockerfile', 'w') as f:
        f.write(dockerfile)
    logging.info('Wrote Dockerfile')
    logging.info('Ready to build the app image')
    return container_name
