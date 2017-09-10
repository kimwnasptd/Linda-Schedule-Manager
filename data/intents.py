# Holds the data that will be loaded
# for the agent's intents

INTENTS = {
    "Add Event" : {
        "tag" : "Add Event",
        "parameters": ["eventType","time","DATE"],
        "persistence_responses": {
            "eventType" : ["What type of event did you want me to add?"],
            "time" : ["When do you want me to add the $eventType?"],
            "DATE" : ["When do you want me to add the $eventType?"]
        },
        "response" : ["succefsully added $eventType to your schedule",
                      "Yes sir, $eventType inserted succesfully",
                      "Right away sir, just added it"],
        "context_set" : "Adding-Event",
        "out_of_context_responses" : ["I'm in the middle of adding something to your schedule",
                                      "Interupting is rude!", "Not finished with your last call",
                                      "We'll talk about that once I finish the adding a $eventType to your schedule",
                                      "We were talking about a $eventType, please concentrate"],
        "context_needed" : ["Idle-State"]
    },

    "Information" : {
        "tag" : "Information",
        "parameters" : [],
        "persistence_responses" : {},
        "response" : ["Thank you",
                      "delightfully"],
        "context_needed" : ["Adding-Event","Checking-the-Schedule"],
        "out_of_context_responses" : ["Debug quickly, I don't know how that happened"]
    },

    "Check Events" : {
        "tag" : "Check Events",
        "parameters" : ['time'],
        "persistence_responses" : {
            'time' : ["For what date should I check, sir?",
                      "What's the timeframe of the events you want me to look for?",
                      "For what day, sir?"]
        },
        "response" : ["You have $eventNum $eventType for $DATE",
                      "Not too busy, only $eventNum $eventType for $DATE",
                      "If my hearing is correct then you have $eventNum $eventType for $DATE"],
        "context_set" : "Checking-the-Schedule",
        "out_of_context_responses" : ["Need some more info in order to give you details about your schedule",
                                      "I'm looking up your schedule", "Please wait unti I finish checking"],
        "context_needed" : ["Idle-State"]
    },

    "Idle" : {
        "tag" : "Idle",
        "parameters" : [],
        "persistence_responses" : {},
        "response" : [],
        "context_needed" : [],
        "out_of_context_responses" : ["Currently I can only add or remove events to your schedule and inform you about them",
                                      "I wasn't doing anything right now sir"]
    },

    "Negative" : {
        "tag" : "Negative",
        "parameters" : [],
        "persistence_responses" : {},
        "response" : [],
        "context_needed" : [],
        "out_of_context_responses" : ["Debug quickly, this is an out of context response from the Negative Context"]
    },

    "Positive" : {
        "tag" : "Positive",
        "parameters" : [],
        "persistence_responses" : {},
        "response" : [],
        "context_needed" : [],
        "out_of_context_responses" : ["Debug quickly, this is an out of context response from the Positive Context"]
    },

    "Cancel" : {
        "tag" : "Positive",
        "parameters" : [],
        "persistence_responses" : {},
        "response" : [],
        "context_needed" : ["Adding-Event", "Checking-the-Schedule"],
        "context_set" : "Idle-State",
        "out_of_context_responses" : ["Debug quickly, this is an out of context response from the Cancel Context"]
    },
}

