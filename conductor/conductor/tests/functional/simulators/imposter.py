from jinja2 import Template
import json
import os
import re
import sys

imposter_template = sys.argv[1]
responses_dir = sys.argv[2]
imposter_json = sys.argv[3]

with open(imposter_template, 'r') as imposter_file:
    tm = Template(imposter_file.read())

responses = {}

for filename in os.listdir(responses_dir):
    if filename.endswith('.json'):
        with open(os.path.join(responses_dir, filename), 'r') as response_file:
            responses[re.sub('\.json$', '', filename)] = response_file.read()

imposter = tm.render(responses)

with open(imposter_json, 'w') as imposter_file:
    imposter_file.write(imposter)
