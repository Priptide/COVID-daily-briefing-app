'''
Uses the UK covid-19 api to return covid-19 cases
'''

from uk_covid19 import Cov19API


def get_covid_19_cases(area=str):
    '''
    Get the covid cases today and total cumlative case for your local area
    '''

    # Make sure the information is valid if not return an error as it is hard for us to diagnose exactly
    try:

        area = str(area)

        filters = ["areaName="+area]

        structure = {
            "areaName": "areaName",
            "date": "date",
            "newCasesByPublishDate": "newCasesByPublishDate",
            "cumCasesByPublishDate": "cumCasesByPublishDate",
        }

        data = Cov19API(
            filters=filters,
            structure=structure,
            latest_by="newCasesByPublishDate"
        )

        results = data.get_json()

        # Make sure we have results
        if(len(results['data']) > 0):
            # This will only run once but needs a for loop to get the results data
            for result in results['data']:
                total_cases = result['cumCasesByPublishDate']
                cases_today = result['newCasesByPublishDate']
                if(cases_today == 0):
                    continue
                else:
                    return total_cases, cases_today
        else:
            return "Error city name not valid or the UK Covid19 api is offline!"
    except:
        return "Error city name not valid or the UK Covid19 api is offline!"
