import json
import datetime

dateString = datetime.date.today().strftime('%Y-%m-%d')

with open('docs/index.html', 'w') as file:
    data = json.load(open('data/data.json'))
    running = json.load(open('data/running.json'))
    agents = json.load(open('data/agents.json'))
    template = open('templates/template.html').read()
    file.write(template
        .replace('${date}', dateString)
        .replace('"${data}"', json.dumps(data))
        .replace('"${running}"', json.dumps(running))
        .replace('"${agents}"', json.dumps(agents))
        )


