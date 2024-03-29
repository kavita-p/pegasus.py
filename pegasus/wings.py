from types import SimpleNamespace
import re
import feedparser
import os
from bs4 import BeautifulSoup
from cohost.models.user import User
from cohost.models.block import MarkdownBlock


def fetch_latest_feed_entry(feed_url):
    return feedparser.parse(feed_url).entries[0]


def parse_from_rss_entry(rss_entry):
    parsed_entry = BeautifulSoup(rss_entry.description, "html.parser")

    # attribution/author
    attribution = parsed_entry.find("div", class_="text-attribution")
    if attribution is not None:
        attribution = attribution.get_text().strip()
        author = attribution[3:]
    else:
        attribution = "Attribution missing!"
        author = ""

    # supporting text
    supporting_text = parsed_entry.find("div", class_="text-supporting")
    if supporting_text is not None:
        supporting_text = " ".join(supporting_text.get_text().split())

    # editor's note
    editor_note = parsed_entry.select(".note p")[0:1] or None
    if editor_note is not None:
        editor_note = editor_note[0].decode_contents().strip()

    # source
    source_tag = parsed_entry.find(string=re.compile("Source"))
    if source_tag is not None and source_tag.parent is not None:
        source = " ".join(source_tag.parent.get_text().split())
        source = (source
            .replace(" ( ", " (")\
            .replace(" )", ")")
            .replace(" (", "* (")
            .replace(": ", ": *")
        )
    else:
        source = None

    return {
        "url": parsed_entry.select(".poemTitle a")[0].get("href"),
        "title": rss_entry.title[17:],
        "text": parsed_entry.find("div", class_="poem"),
        "attribution": attribution,
        "author": author,
        "supporting_text": supporting_text,
        "editor_note": editor_note,
        "source": source,
    }


def format_for_cohost(poem):
    poem = SimpleNamespace(**poem)
    markdown = f"*{poem.attribution}"

    if poem.supporting_text != "":
        markdown += f"""
{poem.supporting_text}"""

    markdown += f"""
via [the Poetry Foundation]({poem.url})*
{poem.text}
"""

    if poem.editor_note is not None:
        markdown += f"""
**A Note from the Editor** 
{poem.editor_note}
"""

    if poem.source is not None:
        markdown += f"""
<sup>{poem.source}</sup>
"""
    markdown += """  
<hr />

<sub>I'm Pegasus! I fetch the Poetry Foundation's Poem of the Day and crosspost it to cohost. Find more details about me [here](https://cohost.org/pegasus-poetry/post/1372999-i-m-pegasus).</sub>
"""

    return {"title": poem.title, "author": poem.author, "markdown": markdown}


def post_to_cohost(poem):
    cookie = os.getenv("COOKIE") 
    project_name = os.getenv("PROJECT_NAME") 

    if project_name is None:
        raise Exception("Missing project name!")

    user = User.loginWithCookie(cookie)
    project = user.getProject(project_name)

    blocks = [MarkdownBlock(poem["markdown"])]

    if project is not None:
        newPost = project.post(
            poem["title"], blocks, tags=[poem["author"], "poetry", "poetry foundation"]
        )
        if newPost is not None:
            print(f"Check out your post at {newPost.url}")
