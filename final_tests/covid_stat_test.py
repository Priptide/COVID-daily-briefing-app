from covid_19_stat import get_covid_19_cases


def test_wrong_city():
    assert get_covid_19_cases(
        "odosfsdo") == "Error city name not valid or the UK Covid19 api is offline!"


def test_bad_input():
    assert get_covid_19_cases(
        123) == "Error city name not valid or the UK Covid19 api is offline!"


def test_good_input():
    assert get_covid_19_cases(
        "London") != "Error city name not valid or the UK Covid19 api is offline!"
