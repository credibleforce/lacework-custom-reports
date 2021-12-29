#!/usr/bin/env python3

import json
import glob
from genson import SchemaBuilder

builder = SchemaBuilder()
root_dir = "./"
for filename in glob.iglob(root_dir + 'reports/**/*.json', recursive=True):
    with open(filename, 'r') as f:
        datastore = json.load(f)
        builder.add_object(datastore )

print(builder.to_schema())