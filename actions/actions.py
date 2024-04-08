
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import openai

class ActionFallback(Action):

    def name(self) -> Text:
        return "action_echo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        openai.api_key = "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"

        prompt = """ 
            Suppose there are a list of food items provided to you in a CSV format, ask some questions to help the user find the food and make an amazing diet depending on the csv products list
            ----
            Following is the CSV with product details -
            age, gender, weight, height, disease, region, allergies, foodtype
            60, male, 75, 6, aneamia, India, Latex Allergies, Fruits
            79, female, 67, 5.3, cancer, Pakistan, Milk Allergy, Salad
            55, male, 88, 5.8, diabetes, India, Egg Allergy, vegan
            39, male, 66, 5.11, high blood pressure, India, Wheat Allergy, vegetables
            46, female, 55, 5.2, low blood pressure, USA, Fish Allergy, Non-veg

            ---
            If the user doesn't know about any word please give them the words meaning and then return back to where you stopped the conversation 
            ---
            Reply only to the last message of the user
            --- 
            dont say 'Hey there' or 'hi there'
            ---
            send only the bot's response, dont say 'bot:' and then response
            ---
            following is the chat history 
            """

        question = "\n\n user: " + tracker.latest_message["text"][0:]
        hist_slot = " "
        hist_slot = str(tracker.slots.get('hist_slot')) + question
        # hist_slot stores the history fo the conversation

        # pmt is the ffinal prompt to send to open ai
        pmt = prompt + hist_slot + " \n ---\n reply to only this text :" + question

        try:
            response = openai.Completion.create(
                engine="gpt-3.5-turbo-instruct",  # Use a valid and non-deprecated model version
                prompt=pmt,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.5
            ).choices[0].text

            dispatcher.utter_message(response.replace('Bot:', ''))
            hist_slot = hist_slot + "\nBot: " + response
            return [SlotSet("hist_slot", hist_slot)]

        except Exception as e:
            # Log the exception or handle it appropriately
            print(f"An error occurred: {e}")
            dispatcher.utter_message("An error occurred while processing your request.")
            return []

