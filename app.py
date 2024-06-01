from urllib.request import urlretrieve
from PIL import Image
from flask import Flask, jsonify, request,send_file, render_template
from flask_cors import CORS, cross_origin
import cv2
import numpy as np
import torch
from torchvision import transforms
import base64

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'



def load_model():
  model = torch.hub.load('pytorch/vision:v0.10.0', 'deeplabv3_resnet50', pretrained=True)
  model.eval()
  return model

def make_transparent_foreground(pic, mask):
  # split the image into channels
  b, g, r = cv2.split(np.array(pic).astype('uint8'))
  # add an alpha channel with and fill all with transparent pixels (max 255)
  a = np.ones(mask.shape, dtype='uint8') * 255
  # merge the alpha channel back
  alpha_im = cv2.merge([b, g, r, a], 4)
  # create a transparent background
  bg = np.zeros(alpha_im.shape)
  # setup the new mask
  new_mask = np.stack([mask, mask, mask, mask], axis=2)
  # copy only the foreground color pixels from the original image where mask is set
  foreground = np.where(new_mask, alpha_im, bg).astype(np.uint8)

  return foreground

def remove_background(model, input_file):
  input_image = Image.open(input_file)
  preprocess = transforms.Compose([
      transforms.ToTensor(),
      transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
  ])

  input_tensor = preprocess(input_image)
  input_batch = input_tensor.unsqueeze(0) # create a mini-batch as expected by the model

  # move the input and model to GPU for speed if available
  if torch.cuda.is_available():
      input_batch = input_batch.to('cuda')
      model.to('cuda')

  with torch.no_grad():
      output = model(input_batch)['out'][0]
  output_predictions = output.argmax(0)

  # create a binary (black and white) mask of the profile foreground
  mask = output_predictions.byte().cpu().numpy()
  background = np.zeros(mask.shape)
  bin_mask = np.where(mask, 255, background).astype(np.uint8)

  foreground = make_transparent_foreground(input_image ,bin_mask)

  return foreground, bin_mask

deeplab_model = load_model()

@app.route("/remove",methods=["POST"])
def remover():
    file = request.files['file']
    file.save(file.filename)
    print(file.filename)
    input_file=file.filename
    # input_file = np.array(input_image)
    foreground, bin_mask = remove_background(deeplab_model, input_file)
    Image.fromarray(foreground).save("foreground.png")
    with open('foreground.png', 'rb') as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode('utf-8')

    return jsonify({'foregroundimage': encoded_image})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True) 