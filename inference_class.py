from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from PIL import Image
import numpy as np
import pathlib
import glob
import time
import os
import cv2

tf.get_logger().setLevel('ERROR')           # Suppress TensorFlow logging (2)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Setting the memory growth to True. If this setting is not set to True then when using a GPU for training, 
# there will be a memory problem.
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
    tf_gpu = tf.config.list_physical_devices('GPU')
    print("Tensorflow ===> ", tf_gpu[0][1])
print("Tensorflow version ===> ", tf.__version__)


class DefectInspection:
    def __init__(self, models_dir):#def __init__(self, models_dir, img_path):

        self.od_model_path = os.path.join(models_dir, "mobilenet/saved_model")
        print("od_model_path=", self.od_model_path)
        self.od_threshold = 0.65
        self.od_img_size = [320, 320]
        self.max_output_size = 5
        self.feat_model_path = os.path.join(models_dir, "efficientnet-b0")
        self.cls_model_path = os.path.join(models_dir, "mlp_224_best_98.h5")
        self.img_org = None
        self.CROP_SIZE = (224, 224)
        self.CHANNEL = 3
        self.gamma = 0.55
        self.od_model = None
        self.feat_ext = None
        self.cls_model = None
        #self.img_path = img_path
        self.IMG_LIST = None
        self.label_map = {0: "Failure", 1: "Success"}
        
    def load_models(self):
        start = time.time()
        # Loading object detection model         
        self.od_model = tf.saved_model.load(self.od_model_path)
        
        # Loading feature extraction and classification models
        self.feat_ext = keras.models.load_model(self.feat_model_path)
        self.cls_model = keras.models.load_model(self.cls_model_path)
        
        end = time.time()
               
        
        print("All models loaded successfully")
        print(f"Loading time is {end-start} s")
        

    def load_image(self, path): 
        img = Image.open(path).convert('L')
        img_numpy = np.array(img, 'uint8')
        cv2.imwrite(path, img_numpy)
        
        data = tf.keras.preprocessing.image.load_img(path) #A PIL Image instance.
        img_tr = tf.convert_to_tensor(tf.keras.preprocessing.image.img_to_array(data), dtype=tf.uint8)
        return img_tr
    
    @tf.function
    def get_detections(self, image):
        """Detect objects in image."""    
        img = tf.dtypes.cast(tf.image.resize(image, self.od_img_size), dtype=tf.uint8) 
        detections = self.od_model(img)######################

        return detections
    def post_processing(self, boxes, scores):
        # apply non-max suppression
        selected_indices, selected_scores = tf.image.non_max_suppression_with_scores(
                                                            boxes,
                                                            scores,
                                                            self.max_output_size,
                                                            iou_threshold=1.0,
                                                            score_threshold=0.5,
                                                            soft_nms_sigma=0.5 )
        selected_boxes = tf.gather(boxes, selected_indices)
        return selected_boxes, selected_scores        
        
    def preprocess_cls(self, img):
        # Apply gamma correction.
        img = tf.image.adjust_gamma(img, gamma=self.gamma)
        img = tf.dtypes.cast(img, dtype=tf.float32)/255.0
        return img
		
    def inspection_cls(self, img_cls):
        # get feature vector
        feature_vector = self.feat_ext(img_cls)

        # # make prediction on the test data.
        pred = self.cls_model.predict(feature_vector)
        pred_cls = self.label_map[int(pred.argmax(axis=1))]

        return pred_cls

    def start_processing(self, img_path):#def start_processing(self, input_tensor):
        ximg_path = os.path.join("project_dir", img_path)

        img_tr = self.load_image(ximg_path)
        
        print("start_processing load_image completion")  
        
        input_tensor = tf.expand_dims(img_tr, axis=0)
        
        detections = self.get_detections(input_tensor)        
        
        det_boxes = detections.get("detection_boxes")[0]
        det_scores = detections.get("detection_scores")[0]
        selected_boxes, selected_scores = self.post_processing(det_boxes, det_scores)
        
        num_det_ob = len(selected_scores)          
        
        results = {}
        results.setdefault('num_det_ob', 0)
        
        if num_det_ob>0 :
            
            rectsample = np.zeros((num_det_ob, 4), float)
            rectraw = np.zeros((num_det_ob, 4), float) 
            predcls = np.empty((num_det_ob, 1), dtype=int) 

            results['num_det_ob'] = num_det_ob
            results.setdefault('rect_samples',selected_boxes.numpy())
            results.setdefault('scores',selected_scores.numpy())         
            
            box_indices = tf.random.uniform(shape=(num_det_ob,), minval=0, maxval=1, dtype=tf.int32)
            det_objects = tf.dtypes.cast(tf.image.crop_and_resize(input_tensor, selected_boxes, box_indices, self.CROP_SIZE), dtype=tf.uint8)
            # Preprocessing for classification
            images_cls = self.preprocess_cls(det_objects)
            feat_vec = self.feat_ext(images_cls)
            preds = self.cls_model.predict(feat_vec)
            predictions = list(preds.argmax(axis=1))
            
            #for  pred in predictions:
            for index, pred in enumerate(predictions):
                 pred_cls = self.label_map[pred]                 
                 predcls[index] = pred              
            results.setdefault("predcls", predcls)            
            
        return results
        #print("- start_processing()\n")