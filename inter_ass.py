import os
import sys
import eel
import speech_recognition as sr
from openai import OpenAI
import threading
import json
import base64
import time
import re
import wave

# Add more robust Eel initialization
try:
    # Verify web directory exists
    web_dir = os.path.join(os.path.dirname(__file__), 'web')
    if not os.path.exists(web_dir):
        print(f"Error: Web directory not found at {web_dir}")
        sys.exit(1)

    # Initialize Eel with more verbose options
    eel.init('web', allowed_extensions=['.html', '.js', '.css'])
    print("Eel initialized successfully with web directory")
except Exception as e:
    print(f"Error initializing Eel: {e}")
    sys.exit(1)

class AudioAssistant:
    def __init__(self):
        self.setup_audio()
        self.is_listening = False
        self.client = None
        self.api_key = None
        self.tts_enabled = True  # Set this to True by default
        self.is_speaking = False
        self.audio_playing = False
        self.load_api_key()

    def setup_audio(self):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)

    def load_api_key(self):
        if os.path.exists('config.json'):
            try:
                with open('config.json', 'r') as f:
                    config = json.load(f)
                    api_key = config.get('api_key')
                    
                    # Add logging for API key loading
                    if api_key:
                        print("API key loaded from config.json")
                        self.set_api_key(api_key)
                    else:
                        print("No API key found in config.json")
            except Exception as e:
                print(f"Error loading API key: {str(e)}")
        else:
            print("config.json file not found")

    def set_api_key(self, api_key):
        try:
            # Validate API key
            if not api_key or not isinstance(api_key, str) or len(api_key.strip()) == 0:
                print("Error: Invalid API key provided")
                return False

            # Trim any whitespace
            api_key = api_key.strip()

            # Set the API key
            self.api_key = api_key
            
            # Initialize OpenAI client with the key
            try:
                self.client = OpenAI(api_key=self.api_key)
                
                # Perform a simple test to verify the API key
                try:
                    test_response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "Hello, can you confirm the API key is working?"}]
                    )
                    print("API key test successful")
                except Exception as test_error:
                    print(f"API key test failed: {str(test_error)}")
                    return False

            except Exception as client_error:
                print(f"Error initializing OpenAI client: {str(client_error)}")
                return False

            # Save the API key to config file
            try:
                with open('config.json', 'w') as f:
                    json.dump({'api_key': self.api_key}, f)
                print("API key saved to config.json")
            except Exception as save_error:
                print(f"Error saving API key: {str(save_error)}")

            return True
        except Exception as e:
            print(f"Unexpected error setting API key: {str(e)}")
            return False

    def delete_api_key(self):
        self.api_key = None
        self.client = None
        if os.path.exists('config.json'):
            os.remove('config.json')

    def has_api_key(self):
        return self.api_key is not None

    def toggle_listening(self):
        if not self.client:
            return False
        self.is_listening = not self.is_listening
        if self.is_listening:
            threading.Thread(target=self.listen_and_process, daemon=True).start()
        return self.is_listening

    def listen_and_process(self):
        cooldown_time = 2  # Cooldown period in seconds
        last_speak_time = 0
        
        while self.is_listening:
            current_time = time.time()
            if not self.is_speaking and not self.audio_playing and (current_time - last_speak_time) > cooldown_time:
                try:
                    with self.mic as source:
                        print("Listening...")  # Debug log
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        
                        # Save the audio to a file for analysis
                        with open("captured_audio.wav", "wb") as audio_file:
                            audio_file.write(audio.get_wav_data())
                        print("Audio saved to captured_audio.wav")  # Debug log
                        
                        print("Audio captured, processing...")  # Debug log
                        text = self.recognizer.recognize_google(audio)
                        print(f"Recognized text: {text}")  # Debug log
                        if self.is_question(text):
                            capitalized_text = text[0].upper() + text[1:]
                            if not capitalized_text.endswith('?'):
                                capitalized_text += '?'
                            eel.update_ui(f"Q: {capitalized_text}", "")
                            print(f"Updating UI with question: Q: {capitalized_text}")  # Debug log
                            self.is_speaking = True
                            response = self.get_ai_response(capitalized_text)
                            eel.update_ui("", f"{response}")
                            print(f"Updating UI with response: {response}")  # Debug log
                            self.is_speaking = False
                            last_speak_time = time.time()  # Update the last speak time
                except sr.WaitTimeoutError:
                    print("Timeout: No speech detected")  # Debug log
                except sr.UnknownValueError:
                    print("Speech Recognition could not understand audio")  # Debug log
                except Exception as e:
                    eel.update_ui(f"An error occurred: {str(e)}", "")
                    print(f"Exception: {str(e)}")  # Debug log
            else:
                time.sleep(0.1)  # Short sleep to prevent busy waiting

    def is_question(self, text):
        # Convert to lowercase for easier matching
        text = text.lower().strip()
        
        # List of question words and phrases
        question_starters = [
            "what", "why", "how", "when", "where", "who", "which",
            "can", "could", "would", "should", "is", "are", "do", "does",
            "am", "was", "were", "have", "has", "had", "will", "shall"
        ]
        
        # Check if the text starts with a question word
        if any(text.startswith(starter) for starter in question_starters):
            return True
        
        # Check for question mark at the end
        if text.endswith('?'):
            return True
        
        # Check for inverted word order (e.g., "Are you...?", "Can we...?")
        if re.match(r'^(are|can|could|do|does|have|has|will|shall|should|would|am|is)\s', text):
            return True
        
        # Check for specific phrases that indicate a question
        question_phrases = [
            "tell me about", "i'd like to know", "can you explain",
            "i was wondering", "do you know", "what about", "how about"
        ]
        if any(phrase in text for phrase in question_phrases):
            return True
        
        # If none of the above conditions are met, it's probably not a question
        return False

    def get_ai_response(self, question):
        try:
            # Verify API key is set
            if not self.client:
                print("Error: OpenAI client not initialized. API key may be missing.")
                return json.dumps({"text": "Error: OpenAI API key not set", "audio": None})

            print(f"Sending request to OpenAI with question: {question}")
            
            # Detailed logging of request parameters
            request_params = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question}
                ]
            }
            print("Request Parameters:", json.dumps(request_params, indent=2))

            # Make API call with more detailed error handling
            try:
                response = self.client.chat.completions.create(**request_params)
            except Exception as api_error:
                print(f"OpenAI API Call Error: {str(api_error)}")
                return json.dumps({"text": f"API Call Error: {str(api_error)}", "audio": None})

            # Verify response structure
            if not hasattr(response, 'choices') or len(response.choices) == 0:
                print("Error: Invalid API response structure")
                return json.dumps({"text": "Error: Invalid API response", "audio": None})

            # Extract and log response details
            text_response = response.choices[0].message.content.strip()
            print(f"OpenAI Response Text: {text_response}")
            print(f"Response Metadata: {response}")

            # Prepare response data
            response_data = {"text": text_response, "audio": None}
            
            # Text-to-Speech generation
            if self.tts_enabled:
                try:
                    speech_response = self.client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=text_response
                    )
                    
                    audio_base64 = base64.b64encode(speech_response.content).decode('utf-8')
                    response_data["audio"] = audio_base64
                    print("TTS Audio generated successfully")
                except Exception as tts_error:
                    print(f"TTS Generation Error: {str(tts_error)}")
            
            # Convert to JSON and log
            json_response = json.dumps(response_data)
            print(f"Final JSON Response: {json_response}")
            
            return json_response

        except Exception as e:
            print(f"Unexpected error in get_ai_response: {str(e)}")
            error_response = json.dumps({"text": f"Unexpected Error: {str(e)}", "audio": None})
            print(f"Error Response: {error_response}")
            return error_response

assistant = AudioAssistant()

@eel.expose
def toggle_listening():
    return assistant.toggle_listening()

@eel.expose
def save_api_key(api_key):
    try:
        assistant.set_api_key(api_key)
        return True
    except Exception as e:
        print(f"Error saving API key: {str(e)}")
        return False

@eel.expose
def delete_api_key():
    try:
        assistant.delete_api_key()
        return True
    except Exception as e:
        print(f"Error deleting API key: {str(e)}")
        return False

@eel.expose
def has_api_key():
    return assistant.has_api_key()

@eel.expose
def toggle_tts():
    assistant.tts_enabled = not assistant.tts_enabled
    return assistant.tts_enabled

@eel.expose
def speaking_ended():
    assistant.is_speaking = False

@eel.expose
def audio_playback_started():
    assistant.audio_playing = True

@eel.expose
def audio_playback_ended():
    assistant.audio_playing = False
    assistant.is_speaking = False

@eel.expose
def test_javascript_connection(message):
    print(f"Received message from JavaScript: {message}")
    # Send a message back to JavaScript
    eel.receiveTestMessage("Hello from Python!")

try:
    eel.start('index.html', size=(960, 840), mode='chrome-app', port=8000, 
               cmdline_args=['--disable-web-security', '--allow-file-access-from-files'])
except Exception as e:
    print(f"Error starting Eel application: {e}")
    sys.exit(1)