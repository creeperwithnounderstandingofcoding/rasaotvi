# forms.py
from rasa_sdk.forms import ValidationAction
from typing import Any, Text, Dict, List
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker
from typing import DomainDict
from rasa_sdk.events import SlotSet  # Importing SlotSet for setting slot values
import re  # Importing regex library for pattern matching

# Defining a custom ValidationAction class for the VI information form
class ViInfoForm(ValidationAction):

    # Returning the name of the form
    def name(self) -> Text:
        return "vi_info_form"

    # Defining the slots required for the form
    def required_slots(
        self,
        slot_values: Dict[Text, Any],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict"
    ) -> List[Text]:
        return ["company", "year", "department", "position", "vi_type"]


    # Mapping entities to slots
    def slot_mappings(self) -> Dict[Text, Any]:
        return {
            "company": self.from_entity(entity="company"),
            "year": self.from_entity(entity="year"),
            "department": self.from_entity(entity="department"),
            "position": self.from_entity(entity="position"),
            "vi_type": self.from_entity(entity="vi_type"),
        }

    # Generic slot validation method
    def validate_slot(self, slot_name: Text, slot_value: Text, dispatcher: CollectingDispatcher) -> List[Dict]:
        # Checking if the slot value is not empty
        if not slot_value:
            # Providing a custom error message for each slot
            error_message = f"请输入有效的{slot_name}。" if slot_name != "year" else "请输入有效的四位数年份。"
            dispatcher.utter_message(text=error_message)
            return [SlotSet(slot_name, None)]  # Clearing the slot value if invalid
        return []

    # Validating the slots
    def validate(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict]:
        errors = []
        # Looping through each required slot
        for slot_name in self.required_slots():
            # Calling the generic validate_slot method for each slot
            errors.extend(self.validate_slot(slot_name, tracker.get_slot(slot_name), dispatcher))
            
            # Additional validation for the year slot
            if slot_name == "year":
                year_value = tracker.get_slot('year')
                year_pattern = re.compile(r"^\d{4}$")
                if not year_pattern.match(year_value):
                    dispatcher.utter_message(text="请输入有效的四位数年份。")
                    errors.append(SlotSet("year", None))  # Clearing the year slot value if invalid

        return errors
