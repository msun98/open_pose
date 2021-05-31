import argparse
import logging
import math
import cv2, time
from ptz_api import *
from initial import *
import numpy as np

from tf_pose import common
from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh

logger = logging.getLogger('TfPoseEstimator-PTZ')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
#formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
# ch.setFormatter(formatter)
# logger.addHandler(ch)


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")



if __name__ == '__main__':

    vcap=initialize() 
    on_screen_display()
    time.sleep(0.1)
    u,p=0,0
    h_view,w_view = 833,1527
    

    parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
    parser.add_argument('--camera', type=int, default=0)

    parser.add_argument('--resize', type=str, default='320x176')
                        #help='if provided, resize images before they are processed. default=0x0, Recommends : 432x368 or 656x368 or 1312x736 ')
    parser.add_argument('--resize-out-ratio', type=float, default=4.0)
                        #help='if provided, resize heatmaps before they are post-processed. default=1.0')

    parser.add_argument('--model', type=str, default='mobilenet_thin')#, help='cmu / mobilenet_thin / mobilenet_v2_large / mobilenet_v2_small')
    parser.add_argument('--show-process', type=bool, default=False)
                        #help='for debug purpose, if enabled, speed for inference is dropped.')
    
    parser.add_argument('--tensorrt', type=str, default="False")
                        #help='for tensorrt process.')
    args = parser.parse_args()

    logger.debug('initialization %s : %s' % (args.model, get_graph_path(args.model)))
    w, h = model_wh(args.resize)
    if w > 0 and h > 0:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h), trt_bool=str2bool(args.tensorrt))
    else:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(432, 368), trt_bool=str2bool(args.tensorrt))

    logger.debug('cam read+')
    cam = cv2.VideoCapture(args.camera)
    ret_val, image = cam.read()
    logger.info('cam image=%dx%d' % (image.shape[1], image.shape[0]))

    initial_position = get_position()
    if initial_position != (0, 0, 0):
        goto_origin(pp,ps,tp,ts)
    

    while True:
        if vcap.isOpened():
            ret_val, image = vcap.read()
            if not ret_val:
                break

            calibration_image = calibration(image,w_view,h_view)
            #cv2.imshow('tf-pose-estimation result',calibration_image)
            logger.debug('image process+')
            humans = e.inference(calibration_image, resize_to_default=(w > 0 and h > 0), upsample_size=args.resize_out_ratio)
            

            logger.debug('postprocess+')
            draw = TfPoseEstimator.draw_humans(calibration_image, humans, imgcopy=False)


            logger.debug('show+')
            fps_time = time.time()
            cv2.putText(calibration_image,
                        "FPS: %f" % (1.0 / (time.time() - fps_time)),
                        (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 255, 0), 2)
            
            cv2.imshow('tf-pose-estimation result',calibration_image)

    #------------------목의 절점 따는 부분 ---------------- 
            x,y = draw[1]
            print(x,y)
     #------------------목의 절점 따는 부분 ----------------   
        
            #print(point_of_neck) # 목의 점.


            k = key_event()
            
        if k == 27:
            break
        logger.debug('finished+')
    #delete all windows
    else:
        print('open failed!')
    vcap.release()
    cv2.destroyAllWindows()