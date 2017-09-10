# AgentModel Class:     Provides an interface for the Model
#                       that is used to analyze the text.

import sys
import json
import random
from rasa_nlu.model import Metadata, Interpreter
from rasa_nlu.config import RasaNLUConfig

MODEL_DIR = "Agent/models/linda_001"
CONFIG_DIR = "Agent/config_spacy.json"


# Parameters: { eventType : assignment,classes,appointment
#               time : 2017-07-23T00:00:00:0000Z | from: --
#                                                  to: --
#               action: add, showed up
# }

def cleanParameters(parameters):
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
    # print(json.dumps(prediction, indent=4, sort_keys=True))

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

    return result


def get_parameters_list(sentence):
    ''' Get list of parameters needed
        in the response sentense'''
    default_parameters = ['$eventType', '$DATE', '$action', '$date-period', '$people', '$time',
                          '$time-from', '$time-to']

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

        response = response.replace('$' + needed_param, param_value)

    return response


def get_response(parameters, intent):
    ''' Randomly pick a response or do some magic
        if the intent was Check Event'''
    if intent['tag'] != "Check Events":
        response = random.choice(intent['response'])
        needed_parameters = get_parameters_list(response)
        response = replace_parameters_in_response(parameters, needed_parameters, response)

    return response


class AgentModel():
    modelInterpreter = None
    intents_info = {}
    last_added_event = {}
    context = {'kimonas': ''}

    def __init__(self, model_dir=MODEL_DIR, conf_file=CONFIG_DIR):
        # Takes some time,to initialize

        from data.intents import INTENTS
        self.intents_info = INTENTS

        print("Initializing the model...")

        metadata = Metadata.load(model_dir)
        interpreter = Interpreter.load(metadata, RasaNLUConfig(conf_file))

        print("Ready")
        print("")

        self.modelInterpreter = interpreter

    def getResponse(self, input_text, user_id='kimonas'):

        result = self.modelInterpreter.parse(input_text)
        result = reformResult(result)
        intent = self.intents_info[result['intents']['name']]

        if 'context_set' in intent:
            self.context[user_id] = intent['context_set']

        cleaned_result = self.get_remaining_parameters(result)

        cleaned_result['response'] = get_response(cleaned_result['parameters'], intent)
        return cleaned_result

    def printResponse(self, input_text):

        prediction = self.getResponse(input_text)

        if prediction != None:
            print(json.dumps(prediction, indent=4, sort_keys=True))
        else:
            print("Action Canceled")

    def get_remaining_parameters(self, given_parameters, user_id='kimonas'):

        needed_parameters = self.intents_info[given_parameters['intents']['name']]['parameters']

        # iterate through all the needed parameters
        for parameter in needed_parameters:

            while True:
                if parameter in given_parameters['parameters']:
                    break
                else:
                    print(self.intents_info[given_parameters['intents']['name']]
                          ['persistence_responses'][parameter])

                    # Get 'raw' new parameters
                    new_prediction = reformResult(self.modelInterpreter.parse(input()))
                    new_intent = new_prediction['intents']['name']
                    new_params = new_prediction['parameters']

                    if new_intent == 'Cancel':
                        # If the user canceled the actionj
                        return None

                    if new_intent != "Information":
                        responses_list = self.intents_info[self.context[user_id]]["out_of_context_responses"]
                        response = random.choice(responses_list)
                        print(response)
                    else:
                        # Add any missing parameter found in the last response
                        for param in new_params:
                            if (param not in given_parameters['parameters']) and (param in needed_parameters):
                                given_parameters['parameters'][param] = new_params[param]

        return given_parameters


if __name__ == "__main__":

    # import sys
    model = AgentModel()
    # model.printPrediction(sys.argv[1])


    while True:
        print('Text: ', end='')
        input_text = input()

        if input_text == 'exit':
            break

        model.printResponse(input_text)
