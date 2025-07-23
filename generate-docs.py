import json
import datetime

data = json.load(open('data/data.json'))
dateString = datetime.date.today().strftime('%Y-%m-%d')

with open('docs/index.html', 'w') as file:
    template = open('templates/template.html').read()
    file.write(template
        .replace('${date}', dateString)
        .replace('"${data}"', json.dumps(data)))

