#!/usr/bin/env python3

import jinja2
import os
from datetime import datetime, timedelta
import random 
import json 

numdays = 30
base = datetime.today()
date_list = [base - timedelta(days=x) for x in range(numdays)]
values = random.sample(range(10, 1000), len(date_list))
values.sort()

module_path = os.path.abspath(os.path.dirname(__file__))

dataset = """
{
    "dataset1": {
        "data": {
            "count": {
                {%- for c in values %}
                    "{{ loop.index }}": {{ c }}
                    {%- if not loop.last -%}
                    ,
                    {%- endif %}
                {%- endfor %}
            },
            "num_compliant": {
                {%- for c in values %}
                    "{{ loop.index }}": {{ c }}
                    {%- if not loop.last -%}
                    ,
                    {%- endif %}
                {%- endfor %}
            },
            "reportTime": {
                {%- for d in date_list %}
                    "{{ loop.index }}": "{{ d }}"
                    {%- if not loop.last -%}
                    ,
                    {%- endif %}
                {%- endfor %}
            }
        },
        "name": "dataset1",
        "summary": {
            "rows": {{ len }}
        }
    }
}
"""

loader = jinja2.BaseLoader()
env = jinja2.Environment(loader=loader,extensions=['jinja2.ext.do'])
template = env.from_string(dataset)
dataset = json.loads(template.render(env=os.environ,date=datetime.utcnow(),date_list=date_list,values=values,len=len(date_list)))

fileloader = jinja2.FileSystemLoader(searchpath=os.path.dirname(module_path))
env = jinja2.Environment(loader=fileloader,extensions=['jinja2.ext.do'])
template = env.get_template(os.path.basename(os.path.join(module_path,'templates','gcp_compliance_summary_report.html.j2')))
result = template.render(items=dataset,date=datetime.utcnow())

with open(os.path.join(module_path,'output','example.html'), 'w') as f:
    f.write(result)