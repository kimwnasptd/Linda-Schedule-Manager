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

    return result


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

    context = {'kimonas':'Idle-State'}
    working_state = {'parameters':{}, 'intents' : {'name' : 'Idle'}}

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

        analyzed_result = self.modelInterpreter.parse(input_text)
        analyzed_result = reformResult(analyzed_result)

        intent = self.intents_info[analyzed_result['intents']['name']]
        current_intent = self.intents_info[self.working_state['intents']['name']]

        # Context Processing:
        # -------------------------------
        if self.context[user_id] in intent["context_needed"]:
            # make sure given intent is not out of context

            if 'context_set' in intent:
                # Set the next context, if the intent sets one
                self.context[user_id] = intent['context_set']

                # set the current state the given analyzed parameters/prediction
                analyzed_result['current_context'] = self.context[user_id]
                self.working_state = analyzed_result
                # change the current intent
                current_intent = self.intents_info[self.working_state['intents']['name']]
        else:
            # The intent given is out of context
            analyzed_result['response'] = select_sentence(self.working_state['parameters'],
                                                          current_intent["out_of_context_responses"])
            analyzed_result['current_context'] = self.context[user_id]
            return analyzed_result

        # Needed Parameters:
        # ------------------
        needed_parameters = current_intent['parameters']

        if analyzed_result['intents']['name'] == "Information":
            # If current intent is Information, update parameters

            for parameter in analyzed_result['parameters']:
                if parameter == 'time':
                    print("time was here")

                if (parameter not in self.working_state['parameters']) and (parameter in needed_parameters):
                    # If parameter *not already given and needed, added to the current parameters
                    self.working_state['parameters'][parameter] = analyzed_result['parameters'][parameter]

        for parameter in needed_parameters:
            # loop through all the parameters to check if all the needed ones are present

            if parameter not in self.working_state['parameters']:
                # If a needed parameter in not present in the given text, ask the user
                result = self.working_state
                result['response'] = select_sentence(self.working_state['parameters'],
                                                              current_intent['persistence_responses'][parameter])
                return result

        # Action: If the Context was finished successfully
        # ------------------------------------------------
        intent = self.intents_info[self.working_state['intents']['name']]
        self.working_state['response'] = select_sentence(self.working_state['parameters'], intent['response'])
        result = self.working_state
        result['current_context'] = 'Idle-State'

        # Context ends, revert to Idle Context
        self.working_state = {'parameters':{}, 'intents' : {'name' : 'Idle'}}
        self.context[user_id] = 'Idle-State'

        return result

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
