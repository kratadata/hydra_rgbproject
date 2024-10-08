from vosk import Model, KaldiRecognizer
import pyaudio
import socket
import os

current_dir = os.getcwd()
model_dir = os.path.join(current_dir,"vosk-model-small-en-us-0.15" )

def msg_to_bytes(msg):
    return msg.encode('utf-8')

class LLM:
    def __init__(self):
        self.model = Model(model_dir)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.active = True
        self.udp_ip = "127.0.0.1"
        self.udp_port = 7000
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.sock.settimeout(0.1)  # Set a timeout for recvfrom
        self.start_mic()
    
    def start_mic(self):
        mic = pyaudio.PyAudio()
        stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
        stream.start_stream()
        while self.active: 
            data = stream.read(4096)
            if self.recognizer.AcceptWaveform(data):
                text = self.recognizer.Result()
                msg = f"' {text[14:-3]} '"
                print(msg)
                self.sock.sendto(msg_to_bytes(msg), (self.udp_ip, self.udp_port))

        stream.stop_stream()
        stream.close()
        self.sock.close()
  
if __name__ == "__main__":
    v = LLM()
