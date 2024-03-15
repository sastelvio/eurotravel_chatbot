# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

import requests
from typing import Any, Text, Dict, List, Optional
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk import FormAction
from rasa_sdk.events import SlotSet

class ProcessTravelDetailsAction(Action):
    def name(self) -> Text:
        return "action_process_travel_details"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract entities
        dates = tracker.get_slot("date")
        locations = tracker.get_slot("location")

        # Do something with extracted entities
        if dates:
            dispatcher.utter_message(text=f"You are traveling from {locations[0]} to {locations[1]} from {dates['from']} to {dates['to']}.")
        else:
            dispatcher.utter_message(text="Please provide both departure and return dates.")

        return []


class ValidateTravelForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_travel_form"

    async def validate_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if not slot_value:
            dispatcher.utter_message(template="utter_ask_dates")
            return {"date": None}
        return {"date": slot_value}

    async def validate_destination(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if not slot_value:
            dispatcher.utter_message(template="utter_ask_places")
            return {"destination": None}
        return {"destination": slot_value}


class TravelForm(FormAction):
    def name(self) -> Text:
        return "travel_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["date", "destination"]

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict]:
        dispatcher.utter_message("Thank you, your travel details have been confirmed.")
        return []

# Define a custom action to search for flight options
class ActionSearchFlights(Action):
    def name(self) -> Text:
        return "action_search_flights"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            # Extract relevant details from user input
            origin = tracker.get_slot("origin")
            destination = tracker.get_slot("destination")
            departure_date = tracker.get_slot("departure_date")
            return_date = tracker.get_slot("return_date")

            # Make a request to the flight booking API
            response = requests.get(
                flight_search_url,
                params={'origin': origin, 'destination': destination, 'departure_date': departure_date, 'return_date': return_date},
                headers={'Authorization': 'Bearer API_KEY'}
            )

            # Check if the request was successful
            if response.status_code == 200:
                # Process the API response
                flights = response.json().get('flights', [])
                if flights:
                    dispatcher.utter_message(text=f"Here are the available flights from {origin} to {destination} on {departure_date}:\n{flights}")
                else:
                    dispatcher.utter_message(text="Sorry, no flights found for the given criteria.")
            else:
                dispatcher.utter_message(text="Sorry, there was a problem while fetching flight information. Please try again later.")
        except Exception as e:
            # Handle any unexpected errors
            dispatcher.utter_message(text="Sorry, something went wrong. Please try again later.")

        return []

class ActionHandleFollowUp(Action):
    def name(self) -> Text:
        return "action_handle_follow_up"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Retrieve slots from the tracker
        preference = tracker.get_slot("preference")
        
        if preference == "change":
            # Handle change in preference
            dispatcher.utter_message("Sure, let's update your preference.")
            return [SlotSet("preference", None)]
        else:
            # Handle follow-up question
            dispatcher.utter_message("Here is some additional information based on your preference.")
            return []

class ActionRecommendation(Action):
    def name(self) -> Text:
        return "action_recommendation"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Retrieve user preferences from slots
        preference = tracker.get_slot("preference")

        if preference == "food":
            # Generate food recommendation based on user preference
            recommendation = "You might like the new Italian restaurant downtown!"
        elif preference == "movie":
            # Generate movie recommendation based on user preference
            recommendation = "I recommend checking out the latest thriller movie at the cinema!"
        else:
            recommendation = "I'm sorry, I couldn't find a recommendation based on your preference."

        # Send personalized recommendation to the user
        dispatcher.utter_message(text=recommendation)

        return []