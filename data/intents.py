# Holds the data that will be loaded
# for the agent's intents

# Lifespan : [Minutes, Requests]

INTENTS = {

    # Core Intents
    "Cancel" : {
        "tag" : "Cancel",
        "parameters" : [],
        "persistence_responses" : {},
        "response" : ["Stopped!",
                      "Ok, stopped it",
                      "Yes sir, just deopped it",
                      "Stopped as you wished"],
        "context_needed" : ["Adding-Event", "Checking-the-Schedule"],
        "lifespan" : [1,3]
    },

    "Information" : {
        "tag" : "Information",
        "parameters" : [],
        "persistence_responses" : {},
        "response" : ["Thank you",
                      "delightfully"],
        "context_needed" : ["Adding-Event","Checking-the-Schedule"],
        "lifespan" : [0,0]
    },
    # ~~~~~~~~~~~~

    # ~~~~~~~~~~~~~~~~~~~~
    # Adding Event Intents
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
        "context_needed" : [],
        "lifespan" : [3, 5]
    },

    "Change Last Added Event" : {
        "tag" : "Change Last Added Event",
        "parameters": [],
        "persistence_responses": {},
        "response" : ["Just modified it.",
                      "Yes sir, fixed your $context-eventType.",
                      "Right away, just edited your $context-eventType",
                      "Changed you $context-eventType, if you need anything else tell me"],
        "context_needed" : ["Adding-Event"],
        "lifespan" : [1, 3]
    },

    "Remove Last Added Event" : {
        "tag" : "Remove Last Added Event",
        "parameters" : [],
        "persistence_responses" : {},
        "response" : ["Right away, just removed them",
                      "Just removed it",
                      "Cleaned it up"],
        "context_needed" : ["Adding-Event"],
        "lifespan" : [1,3]
    },
    # ~~~~~~~~~~~~~~~~~~~~~

    # Checking the Schedule Intents
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
        "context_needed" : [],
        "lifespan" : [3, 5]
    },

    "Check Specific Events" : {
        "tag" : "Check Specific Events",
        "parameters" : [],
        "persistence_responses" : {},
        "response" : ["You have $eventNum $eventType for $DATE",
                      "Not too busy, only $eventNum $eventType for $DATE",
                      "If my hearing is correct then you have $eventNum $eventType for $DATE"],
        "context_needed" : ["Checking-the-Schedule"],
        "lifespan" : [3, 5]
    },

    "Remove Event from Selection" : {
        "tag" : "Remove Event from Selection",
        "parameters" : [],
        "persistence_responses" : {},
        "response" : ["Right away, just removed them",
                      "Just removed it",
                      "Cleaned it up"],
        "context_needed" : ["Checking-the-Schedule"],
        "lifespan" : [1,3]
    },
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    "Check Current State" : {
        "tag" : "Check Current State",
        "parameters": [],
        "persistence_responses": {},
        "response" : ["Last give intent was $last-intent"],
        "context_set" : "Checking-Current-State",
        "context_needed" : [],
        "lifespan" : [3, 5]
    },

    "Negative" : {
        "tag" : "Negative",
        "parameters" : [],
        "persistence_responses" : {},
        "response" : [],
        "context_needed" : [],
        "lifespan" : [1,3]
    },

    "Positive" : {
        "tag" : "Positive",
        "parameters" : [],
        "persistence_responses" : {},
        "response" : [],
        "context_needed" : [],
        "lifespan" : [1,3]
    },

    "Remove Event" : {
        "tag" : "Remove Event",
        "parameters" : [],
        "persistence_responses" : {},
        "response" : ["Right away, just removed them",
                      "Just removed it",
                      "Cleaned it up"],
        "context_needed" : [],
        "lifespan" : [1,3]
    },

}
