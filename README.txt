AUTHOR: Charles Crooke
DATE CREATED: 01-12-2020

Current Github Repo: https://github.com/Priptide/COVID-daily-briefing-app


For the license please see the LICENSE file!



Welcome to my daily brieifing web app!


Note: All dates are done in UK Standard: DD-MM-YYYY

All code in here is written by me in python except for the html template which was provided by exeter university

You can run the program without editing the config.json although it will not be able to run the news and weather brieifings


In order to use this you will need to setup the config.json file properly:


All these parameters must not be left blank otherwise it is likely the app will not run or will crash!


"News_API_Key" needs to be set to an api key from https://newsapi.org/ generate your own api key and paste it there

"Weather_API_Key" needs to be an api key from https://openweathermap.org/api 
                    please be aware this can take 20+ minutes for your api key to be active so be patient

"Current_City" should be set too the city nearest too you, if you get no weather or covid stats returned try a larger city nearby,
                    this maybe helpful if you live in a smaller town with the same name as a city elsewhere

"Current_Country" should be set to the country code you live in, check this webpage https://newsapi.org/docs/endpoints/top-headlines 
                    under the country request parameter to see the options

"Covid_Briefing" is set too true by default, this means you will get a covid brieifing 
                    with your news, set this too false if you don't want this

"Name" this is just your name set it as what you would like for your welcome message

"Briefing_Times" these are preset as three times for a daily brieifing, please try set at least one minimum and any number maximum,
                    use the format HH:MM for these times, they will repeat daily

"News_Provider_Preferences" these are your prefered news sources from the newsapi.org we set BBC News as the only one for default 
                    but add any other news sources you regularly read


Please leave the "Notifications" and "Alarms" parameters empty or as they are since these are used to save your alarms and notifications


If you would like to change the icon on the web page then simply change out icon.png in the static/images folder for another image making 
                    sure to rename the new image too icon.png and removing the old image!
                

For changing the favicon you will need to go too line 268 in webmain.py and change the url for the favicon too another url of the image you would like!


Otherwise feel free to make changes and edits too the code or contact me on github via the above repo to ask any questions!