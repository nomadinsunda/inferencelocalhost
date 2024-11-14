from PIL import Image
import numpy as np
import pathlib
import glob
import time
import os

class DefectInspection:
    def __init__(self):
        
        self.label_map = {0: "NG", 1: "OK"}


    def start_processing1(self):   
        print("+ start_processing()")
        num_det_ob = 1  

        selected_scores = np.array([0.66370654])  #[0.66370654]
        selected_boxes= np.array([[0.24692935, 0.43480504, 0.789215, 0.853683]]) #[[0.24692935, 0.43480504, 0.789215, 0.853683  ]]
                
        results = {}
        results.setdefault('num_det_ob', num_det_ob)
        
        if num_det_ob>0 :
            rectsample = np.zeros((num_det_ob, 4), float)
            rectraw = np.zeros((num_det_ob, 4), float) 
            predcls = np.empty((num_det_ob, 1), dtype=int)
            
            results['num_det_ob'] = num_det_ob
            results.setdefault('rect_samples',selected_boxes)
            results.setdefault('scores',selected_scores)            
            
            predictions = np.array([1])
            
            #for  pred in predictions:
            for index, pred in enumerate(predictions):
                 pred_cls = self.label_map[pred]                 
                 predcls[index] = pred              
            results.setdefault("predcls", predcls)      
        
        print("- start_processing()")
               
        return results
    
    
    def start_processing2(self):   
        print("+ start_processing()")
        num_det_ob = 2

        selected_scores = np.array([0.90452623, 0.67441374])  #[0.66370654]
        selected_boxes= np.array([[0.27618462, 0.25817466, 0.48863763, 0.43468946],
                                  [0.76034105, 0.24680996, 0.96926427, 0.42926288]])
        
        
        results = {}
        results.setdefault('num_det_ob', num_det_ob)
        
        if num_det_ob>0 :
            rectsample = np.zeros((num_det_ob, 4), float)
            rectraw = np.zeros((num_det_ob, 4), float) 
            predcls = np.empty((num_det_ob, 1), dtype=int)
            
            results['num_det_ob'] = num_det_ob
            results.setdefault('rect_samples',selected_boxes)
            results.setdefault('scores',selected_scores)            
            
            predictions = np.array([0, 0])
            
            #for  pred in predictions:
            for index, pred in enumerate(predictions):
                 pred_cls = self.label_map[pred]                 
                 predcls[index] = pred              
            results.setdefault("predcls", predcls)      
        
        print("- start_processing()")
               
        return results
        
