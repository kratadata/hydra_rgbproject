from vosk import Model, KaldiRecognizer
import pyaudio


def msg_to_bytes(msg):
    return msg.encode('utf-8')

class LLM:
    def __init__(self):
        self.model = Model(r"C:\Users\BRAINWAVES-CLIENT-2\Documents\GitHub\hydra_rgbproject\touchDesigner\vosk\vosk-model-small-en-us-0.15")
        self.recognizer = KaldiRecognizer(self.model, 16000)
    
    def start_mic(self):
        mic = pyaudio.PyAudio()
        self.stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
        self.stream.start_stream()
        self.stt()
    
    def stt(self):
        data = self.stream.read(4096)
        if self.recognizer.AcceptWaveform(data):
            text = self.recognizer.Result()
            #me.parent().store("vosk", {text[14:-3]})
            line = f"' {text[14:-3]} '"
            sock.sendto(msg_to_bytes(line), (upd_ip, udp_port))


    def stop_mic(self):
        self.stream.stop_stream()
    

if __name__ == "__main__":
    v = LLM()
    v.startMic()