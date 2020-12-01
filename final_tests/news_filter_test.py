from news_filter import get_news


def test_api_key():
    assert get_news(
        "gb", "3243423423424") == "Error country tag not valid or api key not valid or no news from selected news sources or the open news api is offline!"


def test_wrong_country():
    assert get_news(
        "odosfsdo", "b21e04fe3eef409a9f4570081aa0ca0d") == "Error country tag not valid or no news from selected news sources avaliable, consider changing your sources in the config file!"


def test_wrong_source():
    assert get_news(
        "gb", "b21e04fe3eef409a9f4570081aa0ca0d", ("Pesto")) == "Error country tag not valid or no news from selected news sources avaliable, consider changing your sources in the config file!"


def test_bad_input():
    assert get_news(
        123, 12312313) == "Error country tag not valid or api key not valid or no news from selected news sources or the open news api is offline!"


def test_good_input():
    assert get_news(
        "gb", "b21e04fe3eef409a9f4570081aa0ca0d") != "Error country tag not valid or api key not valid or no news from selected news sources or the open news api is offline!"
