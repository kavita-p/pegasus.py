import feedparser
from bs4 import BeautifulSoup

page = feedparser.parse(
    "https://us12.campaign-archive.com/feed?u=c993b88231f5f84146565840e&id=ff7136981c"
)
entry = page.entries[0]

parsed_entry = BeautifulSoup(entry.description, "html.parser")
print(parsed_entry.prettify())
