from pegasus import soar


def test_fetch():
    page = soar.fetch(
        "https://us12.campaign-archive.com/feed?u=c993b88231f5f84146565840e&id=ff7136981c"
    )
    print(page.text)
    assert False
