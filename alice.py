#!/usr/bin/env python -W ignore::DeprecationWarning
import shutup; shutup.please() # This is just to suppress the annoying warning messages from the SIP library
from pyVoIP.VoIP import VoIPPhone, InvalidStateError, CallState
import speech_recognition
import pyaudio

#Voip settings
USER = "PythonTest" # Voip username
PASS = "Python1234" # Voip password
PHONEHOST = "192.168.178.1" # ip of router (or whatever the phone is connected to)
HOST = "192.168.178.59" #ip of this machine

#PyAudio settings
CHUNK = 160
FORMAT = pyaudio.paInt8
CHANNELS = 1
RATE = 8000

#LLM settings


#stuff
init_banner = """Alice - The AI Phone"""


#inits
r = speech_recognition.Recognizer()
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK)

def answer(call): # This will be your callback function for when you receive a phone call.
    try:
        call.answer()
        print("Call by " + call.request.headers["From"]["number"] + " answered")
        frames = []
        while call.state == CallState.ANSWERED:
            stream.write(call.read_audio())
            mic = speech_recognition.Microphone()
            speech_recognition.Microphone.list_microphone_names()
            with mic as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source)
                text = r.recognize_whisper(audio) # got decent results with this
                print(text)

            #generate response
            #LLama.generate_response(text) or smth
            #send response
            call.write_audio(stream.read(CHUNK))
        print("Call by " + call.request.headers["From"]["number"] + " ended")
        call.hangup()
    except InvalidStateError:
        pass
    except Exception as e:
        call.hangup()
        print(e)

  
if __name__ == "__main__":
    #load mdoel
    print(init_banner)
    print("Loading model...")
    source = speech_recognition.AudioData(b'\x80'*8000, 8000, 1)
    r.recognize_whisper(source)
    #start phone
    print("Starting phone...")
    phone=VoIPPhone(PHONEHOST, 5060, USER, PASS, callCallback=answer, myIP=HOST, sipPort=5060, rtpPortLow=16384 , rtpPortHigh=32767 )
    phone.start()
    input('Press enter to disable the phone:\n')
    phone.stop()