# mycroft---quotes---skill

- say a random quote from a famous person or movie
- say a random fact about a number
- say how much time you are have left to live based on gender and birthdate (life expectancy)

# output example

        Input: quote
        2017-04-27 17:56:11,222 - CLIClient - INFO - Speak: Never interrupt your enemy when he is making a mistake. Napoleon Bonaparte

        Input: when will i die
        2017-04-27 17:56:26,797 - CLIClient - INFO - Speak: You are currently 17. years old
        2017-04-27 17:56:26,816 - CLIClient - INFO - Speak: You have lived 0.23 of your life
        2017-04-27 17:56:26,841 - CLIClient - INFO - Speak: You  are expected to live another 59 years 1 months 26 days 3 hours 54 minutes 49 seconds

        Input: fact about a number
        2017-04-27 17:56:32,909 - CLIClient - INFO - Speak: Fact about number 4000
        2017-04-27 17:56:32,921 - CLIClient - INFO - Speak: the weight in pounds that the Great White Shark can grow to

# configuration

you need a mashape APi key, add this to your config file

https://market.mashape.com/explore?sort=developers

# msm install

this skill is msm compatible, you must only add the mashape key to the config and are ready to go

# manual install

        pip install unirest
        git clone into skills folder


