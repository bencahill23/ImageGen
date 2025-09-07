from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO


GOOGLE_API_KEY= "AIzaSyBC6tI_A5paMPTTAJt9OU1V25Ussf9iCeo"
client = genai.Client(api_key= GOOGLE_API_KEY)

input_image = Image.open('assets/faces.jpg')
#text_input = """Transform the provided sketch of a face into a photrealistic image with narrow depth of field style of Anton Corbijn. Preserve the original features of the face, but give piercing blue eyes, and add skin texture, wrinkles, freckles, spots or other features. The subject should be portrayes as being around 80 years of age. Add film grain, and use a higher thanb normal contrast. """
text_input = """Transform the appearance any persons into a Britpop band member. Add clothing, instruments and other accessories. Maintain the composition of the original image, apply the style of 90s UK indie. Make it look like an album cover, with a random noun as the bandname. """
# Generate an image from a text prompt
response = client.models.generate_content(
    model="gemini-2.5-flash-image-preview",
    contents=[input_image, text_input],
)

image_parts = [
    part.inline_data.data
    for part in response.candidates[0].content.parts
    if part.inline_data
]

if image_parts:
    image = Image.open(BytesIO(image_parts[0]))
    image.save('output_image.png')
    image.show()
