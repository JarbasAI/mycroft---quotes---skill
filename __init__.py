
from adapt.intent import IntentBuilder
from mycroft.util.parse import extract_datetime
from mycroft.skills.core import FallbackSkill, intent_handler, \
    intent_file_handler
from langcodes import standardize_tag, LanguageData, find_name
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
        self.countries_data = {}
        self.country_codes = {}
        self.regions = [u'Asia', u'Europe', u'Africa', u'Oceania',
                        u'Americas', u'Polar']
        self.subregions = [u'Southern Asia', u'Northern Europe',
                           u'Southern Europe', u'Northern Africa',
                           u'Polynesia', u'Middle Africa', u'Caribbean',
                           u'South America', u'Western Asia',
                           u'Australia and New Zealand', u'Western Europe',
                           u'Eastern Europe', u'Central America',
                           u'Western Africa', u'Northern America',
                           u'Southern Africa', u'Eastern Africa',
                           u'South-Eastern Asia', u'Eastern Asia',
                           u'Melanesia', u'Micronesia', u'Central Asia']

    def initialize(self):
        self.register_fallback(self.handle_brainshop, 99)
        self.get_country_data()

        for c in self.countries_data:
            self.register_vocabulary("country", c)

    # mashape poetry api
    # TODO intents for these
    def poetry_authors(self):
        url = "https://thundercomb-poetry-db-v1.p.mashape.com/author",
        response = self.get_mashape(url)
        return response["authors"]

    def search_poem(self, poem="Sonnet 18", author=None):
        poem = poem.replace(" ", "%20")
        if author is not None:
            author = author.replace(" ", "%20")
            url = "https://thundercomb-poetry-db-v1.p.mashape.com/author,title/" \
                  + author + ";" + poem
        else:
            url = "https://thundercomb-poetry-db-v1.p.mashape.com/title/" + poem
        response = self.get_mashape(url)
        return response

    def search_author(self, author="William Shakespeare"):
        author = author.replace(" ", "%20")
        url = "https://thundercomb-poetry-db-v1.p.mashape.com/author/" + \
             author
        response = self.get_mashape(url)
        return response

    # intent handlers
    @intent_handler(IntentBuilder("CountryRegion")
                    .require("where").require("country"))
    @intent_file_handler("country_region.intent")
    def handle_country_where(self, message):
        country = message.data["country"]
        countries = self.search_country(country)
        if len(countries):
            # TODO did you mean this or that
            self.log.debug("multiple matches found: " +
                          str([c["name"] for c in countries]))
            c = countries[0]
            name = c["name"]
            region = c["region"]
            sub = c["subregion"]
            if region in sub:
                r = sub
            else:
                r = sub + ", " + region
            self.speak_dialog("country_location",
                              {"country": name, "region": r})
        else:
            self.speak_dialog("bad_country")

    @intent_handler(IntentBuilder("CountryCurrency")
                    .require("currency").require("country")
                    .require("question"))
    @intent_file_handler("country_currency.intent")
    def handle_country_currency(self, message):
        if not len(self.countries_data):
            self.get_country_data()
        country = message.data["country"]
        if country in self.countries_data.keys():
            coins = self.countries_data[country]["currencies"]
            for c in coins:
                # TODO currency code to spoken currency name
                self.speak(c)
        else:
            self.speak_dialog("bad_country")

    @intent_file_handler("country_in_region.intent")
    def handle_country_in_region(self, message):
        region = message.data["region"]
        if region in self.regions:
            countries = self.search_country_by_region(region)
        elif region in self.subregions:
            countries = self.search_country_by_subregion(region)
        else:
            self.speak_dialog("bad_region")
            return
        if len(countries):
            for c in countries:
                self.speak(c["name"])
        else:
            self.speak_dialog("bad_country")

    @intent_file_handler("where_language_spoken.intent")
    def handle_language_where(self, message):
        language = message.data["language"]
        lang_code = find_name('language', language, standardize_tag(self.lang))
        countries = self.search_country_by_language(lang_code)
        if len(countries):
            for c in countries:
                self.speak(c["name"])
        else:
            self.speak_dialog("bad_country")

    @intent_handler(IntentBuilder("CountryLanguage")
                    .require("languages").require("country")
                    .require("question"))
    @intent_file_handler("country_languages.intent")
    def handle_country_languages(self, message):
        if not len(self.countries_data):
            self.get_country_data()
        country = message.data["country"]
        if country in self.countries_data.keys():
            langs = self.countries_data[country]["languages"]
            for lang in langs:
                self.speak(lang)
        else:
            self.speak_dialog("bad_country")

    @intent_handler(IntentBuilder("CountryTimezone")
                    .require("timezone").require("country"))
    @intent_file_handler("country_timezones.intent")
    def handle_country_timezones(self, message):
        if not len(self.countries_data):
            self.get_country_data()
        country = message.data["country"]
        if country in self.countries_data.keys():
            self.set_context("country", country)
            timezones = self.countries_data[country]["timezones"]
            for t in timezones:
                self.speak(t)
        else:
            self.speak_dialog("bad_country")

    @intent_file_handler("country_area.intent")
    def handle_country_area(self, message):
        if not len(self.countries_data):
            self.get_country_data()
        country = message.data["country"]
        if country in self.countries_data.keys():
            self.set_context("country", country)
            area = self.countries_data[country]["area"]
            # TODO units
            self.speak(area)
        else:
            self.speak_dialog("bad_country")

    @intent_handler(IntentBuilder("CountryPopulation")
                    .require("population").require("country")
                    .require("question"))
    @intent_file_handler("country_population.intent")
    def handle_country_population(self, message):
        if not len(self.countries_data):
            self.get_country_data()
        country = message.data["country"]
        if country in self.countries_data.keys():
            self.set_context("country", country)
            population = self.countries_data[country]["population"]
            self.speak(population)
        else:
            self.speak_dialog("bad_country")

    @intent_handler(IntentBuilder("CountryBorders")
                    .require("borders").require("country")
                    .require("question"))
    @intent_file_handler("country_borders.intent")
    def handle_country_borders(self, message):
        if not len(self.countries_data):
            self.get_country_data()
        country = message.data["country"]
        if country in self.countries_data.keys():
            self.set_context("country", country)
            borders = self.countries_data[country]["borders"]
            for b in borders:
                self.speak(self.country_codes[b])
        else:
            self.speak_dialog("bad_country")

    @intent_handler(IntentBuilder("CountryCapital")
                    .require("capital").require("country")
                    .require("question"))
    @intent_file_handler("country_capital.intent")
    def handle_country_capital(self, message):
        if not len(self.countries_data):
            self.get_country_data()
        country = message.data["country"]
        if country in self.countries_data.keys():
            self.set_context("country", country)
            capital = self.countries_data[country]["capital"]
            self.speak(capital)
        else:
            self.speak_dialog("bad_country")

    @intent_file_handler("denonym.intent")
    def handle_country_denonym(self, message):
        if not len(self.countries_data):
            self.get_country_data()
        country = message.data["country"]
        if country in self.countries_data.keys():
            denonym = self.countries_data[country]["denonym"]
            self.speak(denonym)
            self.set_context("country", country)
        else:
            self.speak_dialog("bad_country")

    @intent_file_handler("country_num.intent")
    def handle_country_number(self, message):
        if not len(self.countries_data):
            self.get_country_data()
        self.speak_dialog("country_number",
                          {"number": len(self.countries_data)})

    @intent_file_handler("similar_word.intent")
    def handle_similar_word_intent(self, message):
        sentence = message.data["sentence"]
        words = self.similar_word(sentence)
        self.speak(random.choice(words))

    @intent_file_handler("ingredients.intent")
    def handle_ingredients_intent(self, message):
        sentence = message.data["sentence"]
        data = self.ingredient_analysis(sentence)
        status = data["status"]
        food = data['food']
        nutrients = data['nutrients']
        quantity = str(data["quantity"])
        if not status == "MISSING_QUANTITY":
            measure = data["measure"]
            text = quantity + " " + measure + " " + food + " has:"
        else:
            text = food + " has:"

        for nutrient in nutrients:
            nutrient = nutrients[nutrient]
            name = nutrient["label"].split(",")[0]
            if not status == "MISSING_QUANTITY":
                quantity = str(nutrient["quantity"])
                unit = nutrient["unit"]
                text += "\n" + quantity + " " + unit + " of " + name
            else:
                text += "\n" + name
        self.speak(text)

    @intent_file_handler("brainshop.intent")
    def handle_brainshop(self, message):
        # intent and fallback
        sentence = message.data.get("sentece", message["utterance"])
        self.speak(self.ask_brainshop(sentence))
        return True

    @intent_file_handler("klingon.intent")
    def handle_klingon_intent(self, message):
        sentence = message.data["sentence"]
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

    def ingredient_analysis(self, sentence="1 large apple"):
        sentence = sentence.replace(" ", "+")
        url = "https://edamam-edamam-nutrition-analysis.p.mashape.com/api/" \
              "nutrition-data?ingr=" + sentence
        response = self.get_mashape(url)
        return response["ingredients"][0]["parsed"][0]

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

    # mashape country api
    def get_all_countries(self):
        url = "https://restcountries-v1.p.mashape.com/all"
        response = self.get_mashape(url)
        return response

    def get_country_data(self):
        countries = self.get_all_countries()
        for c in countries:
            name = c["name"]
            self.countries_data[name] = {}
            self.countries_data[name]["timezones"] = c["timezones"]
            self.countries_data[name]["demonym"] = c["demonym"]
            self.countries_data[name]["currencies"] = c["currencies"]
            self.countries_data[name]["alpha2Code"] = c["alpha2Code"]
            self.country_codes[c["alpha2Code"]] = name
            self.countries_data[name]["alpha3Code"] = c["alpha3Code"]
            self.country_codes[c["alpha3Code"]] = name
            self.countries_data[name]["area"] = c["area"]
            self.countries_data[name]["languages"] = [LanguageData(language=l)
                                                          .language_name()
                                                      for l in c["languages"]]
            self.countries_data[name]["lang_codes"] = [standardize_tag(l)
                                                       for l in
                                                       c["languages"]]
            self.countries_data[name]["capital"] = c["capital"]
            self.countries_data[name]["borders"] = c["borders"]
            self.countries_data[name]["nativeName"] = c["nativeName"]
            self.countries_data[name]["population"] = c["population"]
            self.countries_data[name]["region"] = c["region"]
            self.countries_data[name]["subregion"] = c["subregion"]
            if len(c["latlng"]):
                self.countries_data[name]["lat"], self.countries_data[name][
                    "long"] = c["latlng"]

    def search_country(self, name="portugal"):
        url = "https://restcountries-v1.p.mashape.com/name/" + name
        response = self.get_mashape(url)
        return response

    def search_country_by_code(self, code="ru"):
        url = "https://restcountries-v1.p.mashape.com/alpha/" + code
        response = self.get_mashape(url)
        return response

    def search_country_by_language(self, lang_code="pt"):
        url = "https://restcountries-v1.p.mashape.com/lang/" + lang_code
        response = self.get_mashape(url)
        return response

    def search_country_by_region(self, region="africa"):
        url = "https://restcountries-v1.p.mashape.com/region/" + region
        response = self.get_mashape(url)
        return response

    def search_country_by_subregion(self, sub_region="western asia"):
        url = "https://restcountries-v1.p.mashape.com/subregion/" + \
              sub_region
        response = self.get_mashape(url)
        return response

def create_skill():
    return MashapeSkill()
