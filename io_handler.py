# Taken from https://github.com/nicholasjconn/python-alexa-voice-service/blob/master/alexa_audio.py
import pyaudio
import wave
import subprocess
import speech_recognition
import time
from gtts import gTTS

__author__ = "NJC"
__license__ = "MIT"


class IOHandler:
    """ This object handles all audio playback and recording required by the Alexa enabled device. Audio playback
        and recording both use the PyAudio package.
    """
    def __init__(self):
        """ AlexaAudio initialization function.
        """
        # Initialize pyaudio
        self.pyaudio_instance = pyaudio.PyAudio()

    def close(self):
        """ Called when the AlexaAudio object is no longer needed. This closes the PyAudio instance.
        """
        # Terminate the pyaudio instance
        self.pyaudio_instance.terminate()

    def get_audio(self, timeout=None):
        """ Get audio from the microphone. The SpeechRecognition package is used to automatically stop listening
            when the user stops speaking. A timeout can also be specified. If the timeout is reached, the function
            returns None.
            This function can also be used for debugging purposes to read an example audio file.
        :param timeout: timeout in seconds, when to give up if the user did not speak.
        :return: the raw binary audio string (PCM)
        """
        # Create a speech recognizer
        r = speech_recognition.Recognizer()
        # Open the microphone (and release is when done using "with")
        with speech_recognition.Microphone() as source:
            if timeout is None:
                # Prompt user to say something
                print("You can start talking now...")
                # TODO add sounds to prompt the user to do something, rather than text
                # Record audio until the user stops talking
                audio = r.listen(source)
            else:
                print("Start talking now, you have %d seconds" % timeout)
                # TODO add sounds to prompt the user to do something, rather than text
                try:
                    audio = r.listen(source, timeout=timeout)
                except speech_recognition.WaitTimeoutError:
                    return None
        # Convert audio to raw_data (PCM)
        raw_audio = audio.get_raw_data()

        # Rather than recording, read a pre-recorded example (for testing)
        # with open('files/example_get_time.pcm', 'rb') as f:
        #     raw_audio = f.read()
        return raw_audio

    def play_mp3(self, file_name):
        """ Play an MP3 file. Alexa uses the MP3 format for all audio responses. PyAudio does not support this, so
            the MP3 file must first be converted to a wave file before playing.
            This function assumes ffmpeg is downloaded.
        :param raw_audio: the raw audio as a binary string
        """

        # Convert mp3 response to wave (pyaudio doesn't work with MP3 files)
        subprocess.call(['ffmpeg', '-y', '-i', file_name + '.mp3', file_name + '.wav'],
                        stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        # Play a wave file directly
        self.play_wav(file_name + '.wav')

    def play_wav(self, file, timeout=None, stop_event=None, repeat=False):
        """ Play a wave file using PyAudio. The file must be specified as a path.
        :param file: path to wave file
        """
        # Open wave wave
        with wave.open(file, 'rb') as wf:
            # Create pyaudio stream
            stream = self.pyaudio_instance.open(
                        format=self.pyaudio_instance.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

            # Set chunk size for playback
            chunk = 1024

            # Get start time
            start_time = time.mktime(time.gmtime())

            end = False
            while not end:
                # Read first chunk of data
                data = wf.readframes(chunk)
                # Continue until there is no data left
                while len(data) > 0 and not end:
                    if timeout is not None and time.mktime(time.gmtime())-start_time > timeout:
                        end = True
                    if stop_event is not None and stop_event.is_set():
                        end = True
                    stream.write(data)
                    data = wf.readframes(chunk)
                if not repeat:
                    end = True
                else:
                    wf.rewind()

        # When done, stop stream and close
        stream.stop_stream()
        stream.close()

    def tts(self, input_text):
        tts = gTTS(text=input_text, lang='en')
        tts.save('audio/sample.mp3')
        self.play_mp3('audio/sample')


if __name__ == '__main__':

    IO = IOHandler()

    input_text = input()
    while True:
        print('Input >> ', end='')
        IO.tts(input_text)
        input_text = input()

        if input == 'exit':
            break
