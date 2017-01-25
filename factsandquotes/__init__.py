
from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
import unirest
import random

__author__ = 'jabas'

logger = getLogger(__name__)


class QuotesSkill(MycroftSkill):

    def __init__(self):
        super(QuotesSkill, self).__init__(name="QuotesSkill")
        self.mashape = "RMVFoC2g1MmshMM8RGP4tJe9TtqCp1tTks6jsnG6IEvglDjqqp"
        self.birth = "13 May 1992"
        self.gender = "male"

    def initialize(self):
        self.load_data_files(dirname(__file__))

        quote_intent = IntentBuilder("quoteIntent")\
            .require("quote").build()
        self.register_intent(quote_intent,
                             self.handle_quote_intent)

        fact_intent = IntentBuilder("factIntent")\
            .require("fact").build()
        self.register_intent(fact_intent,
                             self.handle_fact_intent)

        time_to_live_intent = IntentBuilder("timetoliveIntent")\
            .require("timetolive").build()
        self.register_intent(time_to_live_intent,
                             self.handle_time_to_live_intent)

    def handle_quote_intent(self, message):
        self.speak(self.randomquote())

    def handle_fact_intent(self, message):
        fact , number = self.randomfact()
        self.speak("Fact about number " + str(number))
        self.speak(fact)

    def handle_time_to_live_intent(self, message):
        current , elapsed, time = self.time_to_live()
        self.speak("You are currently " + current + " years old")
        self.speak("You have lived " + elapsed + " of your life")
        self.speak("You  are expected to live another " + time )

    def randomquote(self):
        # These code snippets use an open-source library. http://unirest.io/python
        cat = random.choice(("famous", "movies"))
        response = unirest.post("https://andruxnet-random-famous-quotes.p.mashape.com/?cat=" + cat,
                                headers={
                                    "X-Mashape-Key": self.mashape,
                                    "Content-Type": "application/x-www-form-urlencoded",
                                    "Accept": "application/json"
                                }
                                )
        return response.body["quote"] , response.body["author"]

    def randomfact(self):
        # These code snippets use an open-source library. http://unirest.io/python
        response = unirest.get(
            "https://numbersapi.p.mashape.com/random/trivia?fragment=true&json=false&max=10000&min=0",
            headers={
                "X-Mashape-Key": self.mashape,
                "Accept": "text/plain"
            }
            )

        return response.body["text"] , response.body["number"]

    def time_to_live(self):
        response = unirest.post("https://life-left.p.mashape.com/time-left",
                                headers={
                                    "X-Mashape-Key": self.mashape,
                                    "Content-Type": "application/x-www-form-urlencoded",
                                    "Accept": "application/json"
                                },
                                params={
                                    "birth": self.birth,
                                    "gender": self.gender
                                }
                                )
        response = response.body["data"]
        current = str(response["currentAge"])[:3]
        time = str(response["dateString"])
        elapsed = str(response["lifeComplete"])[:4]
        # print response.body["author"]
        return current , elapsed, time

    def convertyoda(self, text="speak like yoda"):
        text = text.replace(" ", "+")
        response = unirest.get("https://yoda.p.mashape.com/yoda?sentence=" + text,
                               headers={
                                   "X-Mashape-Key":self.mashape,
                                   "Accept": "text/plain"
                               }
                               )
        print response.body

    def convertklingon(self, text="death to all but zorbazour"):
        text = text.replace(" ", "+")
        # These code snippets use an open-source library. http://unirest.io/python
        response = unirest.get("https://klingon.p.mashape.com/klingon?text=" + text,
                               headers={
                                   "X-Mashape-Key": self.mashape,
                                   "X-FunTranslations-Api-Secret": "http://api.funtranslations.com/translate/"
                               }
                               )
        response = response.body["contents"]
        return response["translated"]

    def stop(self):
        pass


def create_skill():
    return QuotesSkill()
