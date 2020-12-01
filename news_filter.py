'''
Uses the newsapi to get current news for the users country
'''

import requests


def get_news(country: str, api_key_news: str,
             news_provider_preferences=("BBC News")):
    '''
    Gets the current news for your selected country
    from the set news providers and returns this as the first array
    Also returns any other covid specific news this is the second array
    '''

    # Clean input
    country = str(country)

    api_key_news = str(api_key_news)

    articles_news = []
    covid_specific = []

    # Key words for covid stories
    briefing_covid = ('covid', 'covid-19', 'coronavirus')

    base_url = "https://newsapi.org/v2/top-headlines?"
    complete_url = base_url + "country=" + country + "&apiKey=" + api_key_news

    # Load the api response
    response = requests.get(complete_url)
    output_json = response.json()

    # Make sure the information is valid if not return an error as it is hard for us to diagnose exactly
    try:
        # Cycle through the returned articles
        for article in output_json['articles']:

            # Checks for any news story from the users selected providers
            if news_provider_preferences.count(article['source']['name']) > 0:
                articles_news.append(article['title'])
                # Continue as too not add the news article twice
                continue

            test_title = article['title'].split()

            # Check each word in the title of the articles
            for title_word in test_title:
                if briefing_covid.count(title_word.lower()) > 0:
                    # If the title contains any covid key words
                    # then we add it too our breifing for covid-19
                    covid_specific.append(article['title'])

                    # Then move onto the next article
                    break

        if(len(articles_news) > 0):
            return articles_news, covid_specific
        else:
            return "Error country tag not valid or no news from selected news sources avaliable, consider changing your sources in the config file!"
    except:
        return "Error country tag not valid or api key not valid or no news from selected news sources or the open news api is offline!"
