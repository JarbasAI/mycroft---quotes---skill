from adapt.intent import IntentBuilder
from mycroft.util.parse import extract_datetime
from mycroft.skills.core import FallbackSkill, intent_handler, \
    intent_file_handler
import unirest
import random
import json

__author__ = 'jarbas'


class MashapeSkill(FallbackSkill):

    def __init__(self):
        super(MashapeSkill, self).__init__(name="MashapeSkill")
        if "key" not in self.settings:
            # you are welcome, else get yours here
            # https://market.mashape.com/explore?sort=developers
            self.settings["key"] = \
                "mX8W7sqzonmshpIlUSgcf4VS2nzNp1dObQYjsniJyZlq3F2RBD"

    def initialize(self):
        self.register_fallback(self.handle_brainshop, 99)

    @intent_file_handler("similar_word.intent")
    def handle_similar_word_intent(self, message):
        sentence = message.data["sentence"]
        words = self.similar_word(sentence)
        self.speak(random.choice(words))

    @intent_file_handler("brainshop.intent")
    def handle_brainshop(self, message):
        # intent and fallback
        sentence = message.data.get("sentence", message.data["utterance"])
        self.speak(self.ask_brainshop(sentence))
        return True

    #@intent_handler(IntentBuilder("klingonSay")
    #    .require("klingon").require("say"))
    def handle_klingon_intent(self, message):
        sentence = message.utterance_remainder()
        # TODO google translate for non english input
        self.speak(self.en_to_klingon(sentence))

    @intent_handler(IntentBuilder("quoteIntent")
                    .require("quote")
                    .optionally("famous")
                    .optionally("movies"))
    def handle_quote_intent(self, message):
        if "movies" in message.data:
            cat = "movies"
        elif "famous" in message.data:
            cat = "famous"
        else:
            cat = random.choice(["movies", "famous"])
        quote, author = self.get_quote(cat)
        self.speak(quote + " " + author)

    @intent_handler(IntentBuilder("NumberfactIntent")
                    .require("fact")
                    .require("random_number"))
    def handle_fact_intent(self, message):
        fact, number = self.number_fact()
        self.speak("Fact about number " + str(number))
        self.speak(fact)

    @intent_file_handler("timetolive.intent")
    def handle_time_to_live_intent(self, message):
        gender = self.get_response("gender")
        if gender is None or gender not in ["male", "female"]:
            self.speak("invalid gender")
            return
        birth = self.get_response("birthday")
        if birth is None:
            self.speak("invalid answer")
            return
        date = extract_datetime(birth, lang=self.lang)
        birth = str(date.day) + " " + date.month + " " + str(date.year)
        current, elapsed, time = self.time_to_live(birth, gender)
        self.speak("You are currently " + current + " years old")
        self.speak("You have lived " + elapsed + " of your life")
        self.speak("You  are expected to live another " + time )

    # mashape methods
    def get_mashape(self, url, headers=None):
        """
        generic mashape request method, provides api key in headers
        amd parses result accounting for possible encoding errors
        """
        headers = headers or {
            "X-Mashape-Key": self.settings["key"],
            "Accept": "application/json"
        }
        response = unirest.get(url,
                               headers=headers
                               )
        result = response.body
        if not isinstance(result, dict):
            result = json.loads(result.decode("utf-8", "ignore"))
        return result

    def similar_word(self, word):
        url = "https://similarwords.p.mashape.com/moar?query=" + word
        response = self.get_mashape(url)
        return response["result"]

    def ask_brainshop(self, sentence):
        sentence = sentence.replace(" ", "+")
        response = unirest.get(
            "https://acobot-brainshop-ai-v1.p.mashape.com/get?bid=178&key"
            "=sX5A2PcYZbsN5EY6&uid=mashape&msg=" + sentence,
            headers={
                "X-Mashape-Key": self.settings["key"],
                "Accept": "application/json"
            }
        )
        return response.body["cnt"]

    def time_to_live(self, birth, gender="male"):
        response = unirest.post("https://life-left.p.mashape.com/time-left",
                                headers={
                                    "X-Mashape-Key": self.settings["key"],
                                    "Content-Type": "application/x-www-form-urlencoded",
                                    "Accept": "application/json"
                                },
                                params={
                                    "birth": birth,
                                    "gender": gender
                                }
                                )
        response = response.body["data"]
        current = str(response["currentAge"])[:3]
        time = str(response["dateString"])
        elapsed = str(response["lifeComplete"])[:4]
        return current, elapsed, time

    def get_quote(self, categorie="movies"):
        if categorie not in ["famous", "movies"]:
            raise AttributeError("invalid categorie")
        response = unirest.post(
            "https://andruxnet-random-famous-quotes.p.mashape.com/?cat=" +
            categorie,
            headers={
                "X-Mashape-Key": self.settings["key"],
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
        )
        return response.body["quote"], response.body["author"]

    def number_fact(self, min=0, max=10000):
        min = str(min)
        max = str(max)
        response = unirest.get(
            "https://numbersapi.p.mashape.com/random/trivia?fragment=true"
            "&json=false&max="+max+"&min="+min,
            headers={
                "X-Mashape-Key": self.settings["key"],
                "Accept": "text/plain"
            }
        )

        return response.body["text"], response.body["number"]

    def en_to_klingon(self, sentence):
        sentence = sentence.replace(" ", "+")
        response = unirest.get(
            "https://klingon.p.mashape.com/klingon?text=" + sentence,
            headers={
                "X-Mashape-Key": self.settings["key"],
                "X-FunTranslations-Api-Secret": "<required>"
            }
        )
        return response.body["contents"]["translated"]


def create_skill():
    return MashapeSkill()
