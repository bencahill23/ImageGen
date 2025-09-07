from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

from tempfile import NamedTemporaryFile
import streamlit as st



@st.cache_data
def generateImage(input_image, prompt):
    input_image = Image.open(input_image)
    # prompt = """Transform the appearance any persons into a Britpop band member. Add clothing, instruments and other accessories. Maintain the composition of the original image, apply the style of 90s UK indie. Make it look like an album cover, with a random noun as the bandname. """
    # Generate an image from a text prompt
    response = client.models.generate_content( model="gemini-2.5-flash-image-preview",contents=[input_image, prompt])

    image_parts = [
        part.inline_data.data
        for part in response.candidates[0].content.parts
        if part.inline_data
    ]

    if image_parts:
        image = Image.open(BytesIO(image_parts[0]))
        st.session_state['outputImage'] = image

def switchImages():
    st.session_state['inputImage'] = st.session_state['outputImage'] 
    st.session_state['outputImage'] = None


# state variables - keep image previews buffered 
if 'outputImage' not in st.session_state:
    st.session_state['outputImage'] = None
if 'inputImage' not in st.session_state:
    st.session_state['inputImage'] = None


client = genai.Client(api_key= st.secrets["GOOGLE_API_KEY"])

st.title("GenAI Playground")
with st.container(border=True):
    st.header("Image Generation from File and Prompt")
    source_image = st.file_uploader("Choose a file", type=["jpg", "jpeg", "png"], width="stretch")
    st.session_state['inputImage'] = source_image

    if st.session_state['inputImage'] is not None:
        st.image(st.session_state['inputImage'])
    user_prompt = st.text_input("Prompt for new Image")
    st.button("GENERATE", on_click=generateImage, args=[source_image, user_prompt])

if st.session_state['outputImage'] is not None:
    st.image(st.session_state['outputImage'])

st.button("Send to Input Image - RECURSE", on_click=switchImages)

# image.save('output_image.png')

