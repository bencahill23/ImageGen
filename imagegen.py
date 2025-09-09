from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

from tempfile import NamedTemporaryFile
import streamlit as st


# TODOS
# Turn the peple into animals. Use fur, whiskers, extra eyes, teeth, antenna and other animal features.
#Degrade the quality of the image. Add dust, faded areas, creases, noise. It has been in a pocket for 10 yeasrs. Someone once spilled coffe on the image. It was left out in the sun. 
# The entire content of the input  image should be displayed in on a screen. The screen is one of the following [phone, CRT TV, laptop, cinema, projector, smartwatch]. From this screen, design a setting that works in context, e.g. a school, living room, hotel room, movie theater, someones wrist. The context should differnet than that in the input image.
# Degrade the image so it looks like a early 2000s web image. Use pixelisation, aberation, color bleed, jpeg artefacts and other digital sidstortions

@st.cache_data
def initGenAI():
    client = genai.Client(api_key= st.secrets["GOOGLE_API_KEY"])
    return client

@st.cache_resource
def generateImage(input_image, prompt):
    try:
        input_image.verify()
        print('Valid image')
        _input_image = Image.open(input_image)
    except Exception:
        print('Invalid image')
        _input_image = input_image

    

    #_input_image = input_image
    # Generate an image from a text prompt
    response = client.models.generate_content( model="gemini-2.5-flash-image-preview",contents=[_input_image, prompt])

    image_parts = [
        part.inline_data.data
        for part in response.candidates[0].content.parts
        if part.inline_data
    ]

    if image_parts:
        image = Image.open(BytesIO(image_parts[0]))
        st.session_state['outputImage'] = image
    else:
        print("no response from AI")

def switchImages():
    #buffer to new images and replace in with out
    temp = st.session_state['outputImage'].copy() 
    st.session_state['inputImage'] = temp

def loadImage():
   st.session_state['inputImage'] = st.session_state['inputImageK']

# state variables - keep image previews buffered 
if 'outputImage' not in st.session_state:
    st.session_state['outputImage'] = None
if 'inputImage' not in st.session_state:
    st.session_state['inputImage'] = None
#if 'inputImageK' not in st.session_state:
 #   st.session_state['inputImageK'] = None

client = genai.Client(api_key= st.secrets["GOOGLE_API_KEY"])

st.title("GenAI Playground")
with st.container(border=True):
    st.header("Image Generation from File and Prompt")
    source_image = st.file_uploader("Choose a file", type=["jpg", "jpeg", "png"], width="stretch", key='inputImageK', on_change=loadImage)
    #st.session_state['inputImage'] = source_image

    if st.session_state['inputImage'] is not None:
        st.image(st.session_state['inputImage'])

    user_prompt = st.text_input("Prompt for new Image")
    st.button("GENERATE", on_click=generateImage, args=[st.session_state['inputImage'], user_prompt])

if st.session_state['outputImage'] is not None:
    st.image(st.session_state['outputImage'])
else:
    st.write("No Output Generated")

st.button("Send to Input Image - RECURSE", on_click=switchImages)

# image.save('output_image.png')

