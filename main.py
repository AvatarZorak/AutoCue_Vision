from time import sleep
import sys
import os
import azure.cognitiveservices.speech as speechsdk
import re 
from dotenv import load_dotenv

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')

if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_OLED import OLED_1in51
from PIL import Image,ImageDraw,ImageFont



LINE_LIMIT = 28 #26
LINES = 4
CHARACTER_LIMIT = LINE_LIMIT * LINES #130
FONT_SIZE = 9
X_OFFSET = 5
Y_OFFSET = 0
SLEEP_TIME = 4

done = False
words_to_be_printed = ''
result_future = None


def main():
    global result_future
    
    load_dotenv()
    
    disp = OLED_1in51.OLED_1in51()

    disp.Init()
    disp.clear()
    
    with open('text.txt') as f:
        text = f.read()

    #sentences = text.split('. ') #'. \n'
    sentences = re.split(r'\. |\.\n', text)
    
    print(sentences)
    
    speech_config = speechsdk.SpeechConfig(subscription=f'{os.environ.get("API_KEY")}', region='eastus')
    speech_config.speech_recognition_language = "en-US"
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    
    result_future = speech_recognizer.start_continuous_recognition_async()

    def recognizing_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        heard_text = evt.result.text
        
        global words_to_be_printed
        
        words_from_display = split_words(words_to_be_printed)
        heard_words = split_words(heard_text)
        
        print("Words: ", words_from_display)
        print("Heard: ", heard_words)
        
      #  words_from_display = re.split(', | |\n', words_to_be_printed)
     #   
    #    words_from_display = words_from_display[-3:]
   #     
  #      for i in range(len(words_from_display)):
 #           words_from_display[i] = words_from_display[i].strip('.')
#            words_from_display[i] = words_from_display[i].lower()
        
        if words_from_display == heard_words:
            global done
            done = True
            return
        
        print('RECOGNIZIG: {}'.format(heard_text))


    def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        print('RECOGNIZED: {}'.format(evt.result.text))
        
        global words_to_be_printed
        
        words_from_display = split_words(words_to_be_printed)
        heard_words = split_words(evt.result.text)
        
        print("Words: ", words_from_display)
        print("Heard: ", heard_words)
        
        if words_from_display == heard_words:
            print('something')
            global done
            done = True
            return

    def stop_cb(evt: speechsdk.SessionEventArgs):
        """callback that signals to stop continuous recognition"""
        print('CLOSING on {}'.format(evt.result.text))
        global done
        done = True

    speech_recognizer.recognizing.connect(recognizing_cb)
    speech_recognizer.recognized.connect(recognized_cb)
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    try:
        
        for sentence in sentences:
            #words = sentence.split(' ')
            words = re.split(' |\n|, |\. ', sentence)
            print_words(disp, words, speech_recognizer)

    except KeyboardInterrupt:
        disp.clear()
        disp.module_exit()
        exit()


def print_words(disp, words, speech_recognizer):
    global words_to_be_printed
    
    words_to_be_printed = ''
    current_characters_length = 0
    current_line_length = 0

    for word in words:
        if current_characters_length + len(word) + 1 <= CHARACTER_LIMIT:
            current_characters_length += (len(word) + 1)
            
            if current_line_length + len(word) > LINE_LIMIT:
                words_to_be_printed += '\n'
                current_line_length = (len(word) + 1)
            else:
                current_line_length += (len(word) + 1)
            
            words_to_be_printed += word
            words_to_be_printed += ' '
        else:
            image = Image.new('1', (disp.width, disp.height), "WHITE")
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), FONT_SIZE)
            draw.text((X_OFFSET, Y_OFFSET), words_to_be_printed, font = font, fill = 0)
            disp.ShowImage(disp.getbuffer(image))
            print(words_to_be_printed)
            listen(words_to_be_printed, speech_recognizer)
            print('ended')
            disp.clear()
            
            words_to_be_printed = ''
            words_to_be_printed += word
            words_to_be_printed += ' '
            current_characters_length = len(word) + 1
            current_line_length = (len(word) + 1)

    image = Image.new('1', (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), FONT_SIZE)
    draw.text((X_OFFSET, Y_OFFSET), words_to_be_printed, font = font, fill = 0)
    disp.ShowImage(disp.getbuffer(image))
    print(words_to_be_printed)
    listen(words_to_be_printed, speech_recognizer)
    print('ended')
    disp.clear()


def split_words(words_to_be_printed):
    words = re.split(', | |\n| \n', words_to_be_printed)

    for word in words:
        if not word or word == '\n' or word == '.' or word == ' ':
            words.remove(word)

    words = words[-3:]
    
    for i in range(len(words)):
        words[i] = words[i].strip() 
        words[i] = words[i].strip('.')
        words[i] = words[i].lower()
        
    return words
    

def listen(words_to_be_printed, speech_recognizer):
    global done 
    global result_future
    done = False

    

    result_future.get()
    print('Continuous Recognition is now running, say something.')

    while not done:
        pass
        
    #print("recognition stopped, main thread can exit now.")

if __name__ == '__main__':
    main()
