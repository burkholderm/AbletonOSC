from bs4 import BeautifulSoup

import requests

# request web page
resp = requests.get("https://docs.cycling74.com/max8/vignettes/live_object_model")

# get the response text. in this case it is HTML
html = resp.text

# parse the HTML
soup = BeautifulSoup(html, "html.parser")

def fixtext(t):
    lines = t.splitlines()
    return '\n'.join(line.strip() for line in lines if line.strip() != '')
    #import re
    #return re.sub(r'[ \n]+', ' ', t)

os = {}
for section in soup.find_all('div', {'class': 'liveapi_object_section'}):
    o = {}
    o['name'] = section.find('h3').text
    o['description'] = section.find('p', {'class': 'description'}).text
    o['description'] = fixtext(o['description'])
    details = section.find('div', {'class': 'liveapi_object_details'})

    o['canonical_paths'] = []
    o['children'] = {}
    o['properties'] = {}
    o['functions'] = {}
    for child in details.findChildren('div', recursive=False):
        if not child.has_attr('class'): continue
        if 'liveapi_child_group' in child['class']:
            s = {}
            s['name'] = child.find('h5', {'class': 'liveapi_child_name'}).text
            s['type'] = child.find('div', {'class': 'type'}).find('span', {'class': 'value'}).text
            s['access'] = child.find('div', {'class': 'access'}).find('span', {'class': 'value'}).text
            s['description'] = child.find('p', {'class': 'description'}).text
            s['description'] = fixtext(s['description'])
            o['children'][s['name']] = s
            del s['name']
        elif 'liveapi_property_group' in child['class']:
            s = {}
            s['name'] = child.find('h5', {'class': 'liveapi_property_name'}).text
            s['type'] = child.find('div', {'class': 'type'}).find('span', {'class': 'value'}).text
            s['access'] = child.find('div', {'class': 'access'}).find('span', {'class': 'value'}).text
            s['description'] = child.find('p', {'class': 'description'}).text
            s['description'] = fixtext(s['description'])
            o['properties'][s['name']] = s
            del s['name']
        elif 'liveapi_function_group' in child['class']:
            s = {}
            s['name'] = child.find('h5', {'class': 'liveapi_function_name'}).text
            s['description'] = child.find('p', {'class': 'description'}).text
            s['description'] = fixtext(s['description'])
            # TODO: split description in general, parameters, returns
            o['functions'][s['name']] = s
            del s['name']
        elif 'path' in child['class']:
            s = child.text
            o['canonical_paths'].append(s)
        elif 'none' in child['class']:
            pass
        else:
            raise Exception(f'unexpected element with class "{child["class"]}"')
    os[o['name']] = o
    del o['name']

import json
print(json.dumps(os))
