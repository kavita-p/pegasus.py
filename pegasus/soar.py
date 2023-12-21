import wings

def execute():
    entry = wings.fetch_latest_feed_entry("https://us12.campaign-archive.com/feed?u=c993b88231f5f84146565840e&id=ff7136981c")
    parsed_entry = wings.parse_from_rss_entry(entry)
    poem = wings.format_for_cohost(parsed_entry)
    wings.post_to_cohost(poem)

execute()
