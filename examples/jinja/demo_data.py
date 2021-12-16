#!/usr/bin/env python3

import jinja2
import os
from datetime import datetime, timedelta
import random 
import json 

numdays = 30
base = datetime.today()
date_list = [(base - timedelta(days=x)).strftime('%Y-%m-%dT%H:%M:%SZ') for x in range(numdays)]
date_list.sort()
values = random.sample(range(1, 5000), len(date_list))
values2 = random.sample(range(1, 5000), len(date_list))
values.sort()
values2.sort(reverse=True)

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
            "num_non_compliant": {
                {%- for c in values2 %}
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
            "report_time": "{{ date.strftime('%Y-%m-%dT%H:%M:%SZ') }}",
            "start_time": "{{ date_list|first }}",
            "end_time": "{{ date_list|last }}",
            "rows": {{ len }}
        }
    }
}
"""

loader = jinja2.BaseLoader()
env = jinja2.Environment(loader=loader,extensions=['jinja2.ext.do'])
template = env.from_string(dataset)
dataset = json.loads(template.render(env=os.environ,date=datetime.utcnow(),date_list=date_list,values=values,values2=values2,len=len(date_list)))
print(dataset)
report_template = os.path.join(module_path,'../../templates','html','gcp_compliance_summary_report_example.html.j2')
fileloader = jinja2.FileSystemLoader(searchpath=os.path.dirname(report_template))
env = jinja2.Environment(loader=fileloader,extensions=['jinja2.ext.do'])
template = env.get_template(os.path.basename(report_template))
result = template.render(items=dataset,date=datetime.utcnow())

with open(os.path.join(module_path,'../../output','example.html'), 'w') as f:
    f.write(result)