import sys
from rasa_nlu.model import Metadata, Interpreter
from rasa_nlu.config import RasaNLUConfig
import json

# argv[1]: Model Dir
# argv[2]: config file path
# argv[3]: Phrase to decrypt

try:
    print("Initializing the model...")
    metadata = Metadata.load(sys.argv[1])
    interpreter = Interpreter.load(metadata, RasaNLUConfig(sys.argv[2]))

    result = interpreter.parse(sys.argv[3])
    print(json.dumps(result, indent=4, sort_keys=True))
    # print(result["entities"][-1]["value"])
except IndexError:
    print("Not given")
