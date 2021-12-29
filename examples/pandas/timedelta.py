#!/usr/bin/env python3
from datetime import datetime

start_time = datetime.strptime('2021-02-10T08:00:00Z','%Y-%m-%dT%H:%M:%SZ')
end_time = datetime.strptime('2021-11-18T19:00:00Z','%Y-%m-%dT%H:%M:%SZ')

print((end_time - start_time).total_seconds()/60)

# 405300