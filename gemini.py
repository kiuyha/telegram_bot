from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv('.env')
API_KEY= os.getenv('API_KEY_GEMINI')
def gemini(user_input):
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    respond = model.generate_content(user_input)
    return respond.text

if __name__ == '__main__':
    while True:
        user_input = str(input("your input: "))
        respond = gemini(user_input)
        if user_input == 'exit':
            break
        print (f'gemini respond:{respond}')