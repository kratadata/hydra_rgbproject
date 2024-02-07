from vosk import Model, KaldiRecognizer
import pyaudio
import socket
import threading

def msg_to_bytes(msg):
    return msg.encode('utf-8')

class LLM:
    def __init__(self):
        self.model = Model(r"C:\Users\BRAINWAVES-CLIENT-2\Documents\GitHub\hydra_rgbproject\touchDesigner\vosk\vosk-model-small-fr-0.22")
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.active = True
        self.udp_ip = "127.0.0.1"
        self.udp_port = 7000
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.udp_ip, self.udp_port))
        self.sock.settimeout(0.1)  # Set a timeout for recvfrom
        self.start_threads()

    def start_threads(self):
        # Start the threads for handling audio input and incoming messages
        audio_thread = threading.Thread(target=self.process_audio)
        msg_thread = threading.Thread(target=self.receive_messages)
        audio_thread.start()
        msg_thread.start()

    def process_audio(self):
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
        mic.terminate()

    def receive_messages(self):
        while self.active:
            try:
                received_data, addr = self.sock.recvfrom(1024)
                decoded_data = received_data.decode('utf-8')
                if decoded_data.strip() == "False":
                    self.stop_processing()
            except socket.timeout:
                pass  # Timeout occurred, no message received
            except Exception as e:
                print("Error receiving message:", e)
                break
        self.sock.close()
        
    def stop_processing(self):
        self.active = False
        print("Stopping processing.")
        
if __name__ == '__main__':
    v = LLM()