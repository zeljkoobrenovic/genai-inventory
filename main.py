import re
from speaking_agents.speaking_agents import run_cleaning_agent, run_podcast_episode_analyzer_agent

import asyncio
import json
import os

async def process_episode(episode_file):
    html_content = open(episode_file, 'r').read()
    markdown_content = await run_cleaning_agent(html_content)
    print(markdown_content)

    answers_json = {}

    try:
        answers = await run_podcast_episode_analyzer_agent(markdown_content)
        answers_json = answers.model_dump() if hasattr(answers, "model_dump") else answers.__dict__
        answers_json['file'] = episode_file

        return answers_json
    except Exception as e:
        print(e)

    answers_json['file'] = episode_file
    return answers_json

async def main():
    result = []

    episodes_dir = 'data/episodes'
    html_files = [f for f in os.listdir(episodes_dir) if f.endswith('.html')]

    for html_file in html_files:
        episode_path = os.path.join(episodes_dir, html_file)
        answers = await process_episode(episode_path)
        print(json.dumps(result, indent=2))
        result.append(answers)

        with open('data/answers_new.json', 'w') as f:
            json.dump(result, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())