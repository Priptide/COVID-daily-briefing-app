import pylint.lint
pylint_opts = ['covid_19_stat.py', 'news_filter.py',
               'weather_update.py', 'webmain.py']
pylint.lint.Run(pylint_opts)
