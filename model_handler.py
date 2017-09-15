# AgentModel Class:     Provides an interface for the Model 
#                       that is used to analyze the text.

import sys
import json
import random
import datetime
from rasa_nlu.model import Metadata, Interpreter
from rasa_nlu.config import RasaNLUConfig

MODEL_DIR = "Agent/models/linda_001"
CONFIG_DIR = "Agent/config_spacy.json"


# Parameters: { eventType : assignment,classes,appointment
#               time : 2017-07-23T00:00:00:0000Z | from: -- 
#                                                  to: --
#               action: add, showed up
# }



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Used to Clean up and edit the parameters given by RasaNLU
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def cleanParameters(parameters):
    ''' Used from reformResult '''
    try:
        del parameters['PERSON']
    except KeyError:
        pass
    try:
        del parameters['given-name']
    except KeyError:
        pass
    try:
        del parameters['TIME']
    except KeyError:
        pass
    try:
        del parameters['date']
    except KeyError:
        pass

    return parameters


def reformResult(prediction):
    # Used to cleanup the result
    # Result = {"intents": {'':''}, "parameters": {'':''}, "text": {'':''}
    #print(json.dumps(prediction, indent=4, sort_keys=True))

    parameters = {}

    # Create the parameters dict
    entities = prediction["entities"]

    names_list = []
    for entity in entities:
        if entity.get('entity', 0) == 'PERSON':
            names_list.append(entity.get('value'))

    for entity in entities:
        key = entity.get("entity")
        val = entity.get("value")
        parameters[key] = val

    # Set 'people' list and remove the 'PERSON'
    # entity imported from ner_spacy
    parameters['people'] = names_list

    parameters = cleanParameters(parameters)

    result = {}
    result["intents"] = prediction["intent"]
    result["parameters"] = parameters
    result["text"] = prediction["text"]
    result["time_created"] = datetime.now()

    return result


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Used for substituting $parameter with values from a dict containing the values
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_parameters_list(sentence):
    ''' Get list of parameters needed
        in the response sentense'''
    default_parameters = ['$eventType','$DATE','$action','$date-period','$people','$time',
                          '$time-from','$time-to']

    found_parameters = []
    for parameter in default_parameters:

        if parameter in sentence:
            found_parameters.append(parameter[1:])

    return found_parameters


def replace_parameters_in_response(parameters_dict, needed_parameters, response):

    for needed_param in needed_parameters:

        param_value = parameters_dict[needed_param]
        if not isinstance(param_value, str):
            param_value = str(parameters_dict[needed_param])

        response = response.replace('$'+needed_param, param_value)

    return response

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def select_sentence(parameters, choices_list):
    ''' Randomly pick a sentence from a list of sentences
        and replace values of any parameters'''
    response = random.choice(choices_list)
    needed_parameters = get_parameters_list(response)
    response = replace_parameters_in_response(parameters,needed_parameters,response)
    return response


class AgentModel():

    modelInterpreter = None

    intents_info = {}
    contexts_info = {}
    fallback_responses = []

    active_contexts = {'kimonas': {} }
    incomplete_intents_stack = []

    def __init__(self, model_dir=MODEL_DIR, conf_file=CONFIG_DIR):
        # Takes some time,to initialize

        from data.intents import INTENTS
        self.intents_info = INTENTS
        from data.contexts import CONTEXTS
        self.contexts_info = CONTEXTS
        from data.fallback import RESPONSES
        self.fallback_responses = RESPONSES

        print("Initializing the model...")

        metadata = Metadata.load(model_dir)
        interpreter = Interpreter.load(metadata, RasaNLUConfig(conf_file))

        print("Ready")
        print("")

        self.modelInterpreter = interpreter

    def getResponse(self, input_text, user_id='kimonas'):
        
        analyzed_text = self.modelInterpreter.parse(input_text)
        analyzed_text = reformResult(analyzed_text)

        # Info of the given Intent
        intent = self.intents_info[analyzed_text['intents']['name']]

        # Update the Active Contexts and the Incomplete Intents Stack
        self.update_active_contexts() # To-do

        # Check if the given intent is out of context
        if self.out_of_context(intent):
            # Go to Fallback responses
            response = select_sentence({}, self.fallback_responses) # To-do
            analyzed_text['response'] = response
            return analyzed_text

        # In Context
        else:

            if all_parameters_found(intent, analyzed_text): # To-do
                # All the needed parameters were provided

                # Set the context, if the intent sets one
                if "context_set" in intent:
                    self.active_contexts[user_id][intent["context_set"]] = analyzed_text
                
                # Apply the action for the specific intent
                self.apply_intent_action(intent, analyzed_text) # To-do

                # Return the respective response for the intent
                return self.get_intent_response(intent, analyzed_text) # To-do

            else:
                # User must present missing parameters

                # Add the Incomplete Intent to the current contexts
                intent_name = intent['tag'] + " - Parameters"
                self.active_contexts[user_id][intent_name] = analyzed_text

                # Update the IIS
                self.incomplete_intents_stack.insert(0, analyzed_text)
                
                # Return a response for the missing parameter(s)
                needed_parameters = intent['parameters']
                for parameter in needed_parameters:
                    # Check for the first missing parameter
                    if parameter not in analyzed_text['parameters']:
                        analyzed_text['response'] = select_sentence(analyzed_text['parameters'], 
                                                                    intent['persistence_responses'][parameter])
                        return analyzed_text


    def printResponse(self, input_text):

        prediction = self.getResponse(input_text)
        
        if prediction != None:
            print(json.dumps(prediction, indent=4, sort_keys=True))
        else:
            print("Action Canceled")


if __name__ == "__main__":

    #import sys
    model = AgentModel()
    #model.printPrediction(sys.argv[1])

    while True:
        print('Text: ', end='')
        input_text = input()

        if input_text == 'exit':
            break

        model.printResponse(input_text)
