# from ultralytics import YOLO
# import cv2
# import pafy
# import pickle
# import settings
# import tensorflow as tf
# import numpy as np
# from tensorflow.keras.preprocessing.image import img_to_array, load_img

#original model(perfect)
# with open('weights/model1/yolov8.pkl', 'rb') as file:
    # model1= pickle.load(file)

# def load_model1(model_path):
    # model1 = YOLO('weights/model1/yoloooo.pt')
    # return model1

#Jay soni
# model = None
# output_class = ["Batteries", "Clothes", "E-waste", "Glass", "Light Blubs", "Metal", "Organic", "Paper", "Plastic"]

# def load_model2(model_path):
#     # global model
#     model2 = tf.keras.models.load_model(model_path)
#     return model2

#using CNN
# model3 = load_model('waste-classification-model.h5')
# class_labels = ['Cardboard', 'Glass', 'Metal', 'Paper', 'Plastic', 'Trash']

# def preprocess_image(image_path):
#     print('image path:', image_path)
#     image = load_img(image_path, target_size=(32, 32))
#     image = img_to_array(image, dtype=np.uint8)
#     image = np.array(image) / 255.0
#     return image[np.newaxis, ...]

# def classify_waste3(uploaded_file):
#     # Preprocess the image
#     image = preprocess_image(uploaded_file)

#     # Make prediction
#     prediction = model3.predict(image)
#     # predicted_class = class_labels[np.argmax(prediction[0], axis=-1)]
#     print("Probability:",np.max(prediction[0], axis=-1))
#     predicted_class = class_labels[np.argmax(prediction[0], axis=-1)]
#     print("Classified:",predicted_class,'\n' , class_labels[np.argmax(uploaded_file[0])])

#     # Display the image and prediction
#     # st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
#     # st.write(f"Predicted Category: {predicted_class}")
#     return predicted_class