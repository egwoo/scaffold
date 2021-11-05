import re

def camel_to_kebab(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1-\2', name).lower()
    name = re.sub('\.', '-', name)
    return name

def camel_to_spaces(name):
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', name)
