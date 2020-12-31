    

!pip install flask-ngrok

from google.colab import drive
drive.mount('/content/drive')

from flask_ngrok import run_with_ngrok
from flask import Flask
from flask import Flask, render_template, request
import cv2
from keras.models import load_model
import numpy as np
from keras.applications import ResNet50,VGG16
from keras.optimizers import Adam
from keras.layers import Dense, Flatten, Input, Convolution2D, Dropout, LSTM, TimeDistributed, Embedding, Bidirectional, \
    Activation, RepeatVector, Concatenate
from keras.models import Sequential, Model
from keras.utils import np_utils
from keras.preprocessing import image, sequence
import cv2
from keras.preprocessing.sequence import pad_sequences
from tqdm import tqdm

vocab = np.load('/content/drive/MyDrive/Colab Notebooks/image caption/vocab.npy', allow_pickle=True)

vocab = vocab.item()

inv_vocab = {v: k for k, v in vocab.items()}

print("+" * 50)
print("vocabulary loaded")

embedding_size = 128
vocab_size = len(vocab)
max_len = 40

model = load_model('/content/drive/MyDrive/Colab Notebooks/image caption/ic_model.h5')
print("=" * 150)
print("MODEL LOADED")

#vgg16 = VGG16(include_top=False,weights='imagenet',input_shape=(224,224,3),pooling='avg')


vgg16 = load_model('/content/drive/MyDrive/Colab Notebooks/image caption/vgg16.h5')

print("=" * 150)
print("vgg16 MODEL LOADED")

app = Flask(__name__)
run_with_ngrok(app)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/after', methods=['GET', 'POST'])
def after():
    global model, vgg16, vocab, inv_vocab

    img = request.files['file1']

    img.save('static/file.jpg')

    print("=" * 50)
    print("IMAGE SAVED")

    image = cv2.imread('static/file.jpg')
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image = cv2.resize(image, (224, 224))

    image = np.reshape(image, (1, 224, 224, 3))

    incept = vgg16.predict(image).reshape(1, 4096)

    print("=" * 50)
    print("Predict Features")

    text_in = ['startofseq']

    final = ''

    print("=" * 50)
    print("GETING Captions")

    count = 0
    while tqdm(count < 20):

        count += 1

        encoded = []
        for i in text_in:
            encoded.append(vocab[i])

        padded = pad_sequences([encoded], maxlen=max_len, padding='post', truncating='post').reshape(1, max_len)

        sampled_index = np.argmax(model.predict([incept, padded]))

        sampled_word = inv_vocab[sampled_index]

        if sampled_word != 'endofseq':
            final = final + ' ' + sampled_word

        text_in.append(sampled_word)

    return render_template('after.html', data=final)


if __name__ == "__main__":
    app.run()