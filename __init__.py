
from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
import unirest
import random

__author__ = 'jarbas'

logger = getLogger(__name__)


class FbPost():
    # this class sends posts to facebook skill
    def __init__(self, emitter):
        self.emitter = emitter

    def post_text(self, text, id="me", speech= "Making a post on face book", link= None):
        self.emitter.emit(Message("fb_post_request", {"type":"text", "id":id, "link":link, "text":text, "speech":speech}))


class QuotesSkill(MycroftSkill):

    def __init__(self):
        super(QuotesSkill, self).__init__(name="QuotesSkill")
        try:
            # try jarbas core -> https://github.com/MycroftAI/mycroft-core/pull/557
            self.mashape = self.config_apis.get('MashapeAPI')
        except:
            # try to load from config
            try:
                self.mashape = self.config.get('MashapeAPI')
            except:
                # maybe try to load from skill folder .config or . txt ?
                self.mashape = "xxx" #insert here api, get api list from proxys or whatever and include here maybe?
        try:
            self.birth = self.config['birthdate']
            self.gender = self.config['gender']
        except:
            # no config use defaults
            self.birth = "1 May 1995"
            self.gender = "male"

    def initialize(self):
        self.poster = FbPost(self.emitter)

        quote_intent = IntentBuilder("quoteIntent")\
            .require("quote").build()
        self.register_intent(quote_intent,
                             self.handle_quote_intent)

        fact_intent = IntentBuilder("factIntent")\
            .require("fact").build()
        self.register_intent(fact_intent,
                             self.handle_fact_intent)

        fbquote_intent = IntentBuilder("fbquoteIntent") \
            .require("fbquote").build()
        self.register_intent(fbquote_intent,
                             self.handle_fbquote_intent)

        fbfact_intent = IntentBuilder("fbfactIntent") \
            .require("fbfact").build()
        self.register_intent(fbfact_intent,
                             self.handle_fbfact_intent)

        time_to_live_intent = IntentBuilder("timetoliveIntent")\
            .require("timetolive").build()
        self.register_intent(time_to_live_intent,
                             self.handle_time_to_live_intent)

    def handle_quote_intent(self, message):
        quote, author = self.random_quote()
        self.speak(quote + " " + author)

    def handle_fact_intent(self, message):
        fact, number = self.random_fact()
        self.speak("Fact about number " + str(number))
        self.speak(fact)

    def handle_fbquote_intent(self, message):
        quote, author = self.random_quote()
        text = quote + "\n" + author
        self.poster.post_text(text, speech="Posting a quote on Face book")

    def handle_fbfact_intent(self, message):
        fact, number = self.random_fact()
        text = "Fact about number " + str(number) + ":\n" + fact
        self.poster.post_text(text, speech="Posting a fact on Face book")

    def handle_time_to_live_intent(self, message):
        current, elapsed, time = self.time_to_live()
        self.speak("You are currently " + current + " years old")
        self.speak("You have lived " + elapsed + " of your life")
        self.speak("You  are expected to live another " + time )

    def random_quote(self):
        # These code snippets use an open-source library. http://unirest.io/python
        cat = random.choice(("famous", "movies"))
        response = unirest.post("https://andruxnet-random-famous-quotes.p.mashape.com/?cat=" + cat,
                                headers={
                                    "X-Mashape-Key": self.mashape,
                                    "Content-Type": "application/x-www-form-urlencoded",
                                    "Accept": "application/json"
                                }
                                )
        return response.body["quote"], response.body["author"]

    def random_fact(self):
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

    def stop(self):
        pass


def create_skill():
    return QuotesSkill()
