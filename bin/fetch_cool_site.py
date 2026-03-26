import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
import yaml
import datetime


prompt = (
    "Suggest a really cool, creative, or fun website to feature today on a site called 'Cool Stuff'. "
    "Just return the name, URL, and a one-paragraph description of why it's cool. Only return one site."
    "The URL should just be the URL itself (a full URL, not just a domain). Do not wrap it in Markdown."
)

response = client.chat.completions.create(model="gpt-4o",
messages=[
    {"role": "system", "content": "You are a helpful curator of awesome websites."},
    {"role": "user", "content": prompt}
],
temperature=1.0)

text = response.choices[0].message.content

lines = text.strip().split("\n")

# Very naive parse
name = lines[0].strip(" *")
url = lines[1].strip()
description = " ".join(lines[2:]).strip()

new_entry = {
    "date": datetime.date.today().isoformat(),
    "name": name,
    "url": url,
    "description": description,
}

with open("docs/_data/coolstuff.yml") as f:
    existing = yaml.safe_load(f)

# Only add if not a duplicate
if not any(entry["url"] == new_entry["url"] for entry in existing):
    existing.append(new_entry)
    with open("docs/_data/coolstuff.yml", "w") as f:
        yaml.dump(existing, f, sort_keys=False)

