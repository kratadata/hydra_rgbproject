import azure.cognitiveservices.speech as speechsdk

word = "" # current text
prevWord = "" # store previous text

class AzureSTT:
    def __init__(self, subscription_key, region, maximumWords):
        self.session_started = False
        self.speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
        self.speech_config.set_profanity(speechsdk.ProfanityOption.Raw)
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config)

        self.speech_recognizer.session_started.connect(self.on_session_started)
        self.speech_recognizer.recognizing.connect(self.on_message)
        self.speech_recognizer.session_stopped.connect(self.on_session_stopped)
        self.speech_recognizer.canceled.connect(self.on_canceled)

        self.speech_recognizer.start_continuous_recognition()

        self.filterWords = [ "yeah", "oh", "no", "yes"]
        self.maxWords = maximumWords


    def on_message(self, msg):
        global word
        global prevWord

	    # filter words
        result = msg.result.text.lower()
       
        for f in self.filterWords:
            result = result.replace(f, "")

        # clamp maximum words
        separateWords = result.split(" ")
        clampedWords = separateWords[-self.maxWords:]

        # finalize
        finalResult = " ".join(clampedWords)
        print(finalResult)
        if finalResult != "":
            word = finalResult
            if prevWord != word:
                prevWord = word

        print("Recognized:", word)

    def on_session_started(self, evt):
        print('Connected to Azure:', evt)
        self.session_started = True

    def on_session_stopped(self, evt):
        print('Session stopped:', evt)

    def on_canceled(self, evt):
        print('Canceled:', evt.reason)


        
      