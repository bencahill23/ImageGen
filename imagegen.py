from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import subprocess
import sys
import json
import os

import streamlit as st

st.set_page_config(layout="centered")



# TODOS
# Save Prompts / File handling + menus
# Recursion
# Batch select filenames

def initSession():
    # state variables - keep image previews buffered 
    if 'outputImage' not in st.session_state:
        st.session_state['outputImage'] = None
    if 'inputImage' not in st.session_state:
        st.session_state['inputImage'] = None
    if 'inputPrompt' not in st.session_state:
        st.session_state['inputPrompt'] = None
    if 'saveFilePath' not in st.session_state:
        st.session_state['saveFilePath'] = None
    if 'ExamplePrompts' not in st.session_state:
        st.session_state['ExamplePrompts'] = {
        "Empty" : 0
        }

@st.cache_resource(show_spinner=False)
def initGenAI():
    return genai.Client(api_key= st.secrets["GOOGLE_API_KEY"])
    

@st.cache_data(show_spinner=False)
def generateImage(input_image, prompt):
    # check if the image is imported or being recursed
    try:
        input_image.verify()
        _input_image = input_image
    except Exception:
        _input_image = Image.open(input_image)

    # Generate an image from a text prompt and source image
    try:
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
    except Exception:
        print("Exception")
        print(st.session_state['inputPrompt'])
        pass

def switchImages():
    temp = st.session_state['outputImage'].copy() 
    st.session_state['inputImage'] = temp


def loadExamplePrompts():
    prompt_paper_damage = "Degrade the quality of the image. Add dust, faded areas, creases, noise. It has been in a pocket for 10 years. Someone once spilled coffee on the image. It was left out in the sun for a month and is more faded. The edges are more creased. Maintain all of the damage in the source image and add more. If there is already damage to the image, use it to create holes, tears and extra creases. The generated image should be more damaged than the input image. "

    promt_expand_drawing = "Using the input image as a source of content and style, complete the image so any head have full figures, and are placed in situations relevant to their appearance. Render other characters in the same style and have them interact with the person in the image. Provide narural lighting that emphasises the medium."

    promtp_expand_drawing_photoreal = "Render a shallow-depth of field, moody black and white photograph of the following scene. Using the input image as a source of content only, complete the image so any head have full figures, and are paced in situations relevant to their appearance. Render other characters in the same style and have them interact with the people in the image. Establish depth-of-field using objects and people in the foreground and background."

    prompt_sharpen = "Sharpen the image. Remove noise and blur. Do not alter faces. Maintain the orignal faces and bodies of any person Increase the contrast and dynamic range of the image. "

    prompt_polaroid_fullbody ="Render a Polaroid portrait of any people in the input image. Using the input image as a source of content only, complete the image so any heads have full torsos, and are paced in situations relevant to their appearance. Render other characters in the same style and have them interact with the people in the image. Establish depth-of-field using objects and people in the foreground and background. Do not alter the faces in the image, keep them as close as possible to the input image"

    prompts_dict = {
    "Sharpen" : prompt_sharpen,
    "Paper Damage" : prompt_paper_damage,
    "Expand Portrait to Full-Body" : promt_expand_drawing,
    "Expand Portrait (Photoreal)" : promtp_expand_drawing_photoreal,
    "Polaroid Full-Body + Context" : prompt_polaroid_fullbody
    }
    st.session_state['ExamplePrompts'] = prompts_dict

def loadImage():
   st.session_state['inputImage'] = st.session_state['inputImageK']

def saveImage():
    fn = st.session_state['savefilename'] + ".png"
    fullpath = st.session_state["saveFilePath"]+ "/" +fn
    try:
        st.session_state['outputImage'].save(fullpath)
        st.success(fn+" Saved")
    except:
        st.error("Error saving file")

def updatePrompt():
    st.session_state['inputPrompt'] = st.session_state['inputPromptText'] 

def loadExamplePrompt():
    st.session_state['inputPromptText'] = st.session_state['ExamplePrompts'][st.session_state['selectedExample']]
    updatePrompt()

def selectFolder():
    result = subprocess.run([f"{sys.executable}", "folder_selector.py"], capture_output=True)#, text=True)
    if result.returncode == 0:
        folder_data = json.loads(result.stdout)
        folder_path = folder_data.get("folder_path")
        if folder_path:
            st.session_state["saveFilePath"] = folder_path 
            return folder_path

        else:
            st.error("No folder selected")
    else:
        st.error("Error selecting folder")




#############
#
# INITIALIZE
#
#############

initSession()
loadExamplePrompts()

client = initGenAI()

#############
#
# Start  GUI
#
#############


st.title("GenAI Playground")
with st.container(border=True):
    st.header("Image Gen from File + Prompt")
    source_image = st.file_uploader("Choose an image file (.jpg, .png)", type=["jpg", "jpeg", "png"], width="stretch", key='inputImageK', on_change=loadImage)

    col1, col2 = st.columns([2, 3],  vertical_alignment='center')
    
    with col1:
        if st.session_state['inputImage'] is not None:
            st.image(st.session_state['inputImage'])

    with col2:
        st.text_area("Prompt", height=200, on_change=updatePrompt, key='inputPromptText')#, value=st.session_state['inputPrompt'])
        st.selectbox("Prompt Examples", [*st.session_state['ExamplePrompts']], key='selectedExample', on_change=loadExamplePrompt)

        col1, col2 = st.columns([1, 2],  vertical_alignment='center')
        with col1:
            st.button("GENERATE", on_click=generateImage, args=[st.session_state['inputImage'], st.session_state['inputPrompt']])
        with col2:
            st.button("Send Generated Image to Input", on_click=switchImages)

if st.session_state['outputImage'] is not None:
    st.image(st.session_state['outputImage'])
else:
    st.write("No Output Generated")



with st.container(border=True):
    col1, col2, col3 = st.columns([2,3, 3],  vertical_alignment='bottom')
    with col1:
        st.button("Select Save Folder",on_click=selectFolder)
    with col2:
        st.text_input("Filename", key="savefilename")
    with col3:
        st.button("Download Image", on_click=saveImage, width="stretch")


