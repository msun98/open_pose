import argparse
import logging
import time

import cv2
import numpy as np

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh

logger = logging.getLogger('TfPoseEstimator-WebCam')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

fps_time = 0

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
    parser.add_argument('--camera', type=int, default=0)

    parser.add_argument('--resize', type=str, default='320x176')
    parser.add_argument('--resize-out-ratio', type=float, default=4.0)

    parser.add_argument('--model', type=str, default='mobilenet_thin')
    parser.add_argument('--show-process', type=bool, default=False)
    
    parser.add_argument('--tensorrt', type=str, default="False")
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

    while True:
        ret_val, image = cam.read()
        flip_image = cv2.flip(image,1)
        logger.debug('image process+')
        humans = e.inference(flip_image, resize_to_default=(w > 0 and h > 0), upsample_size=args.resize_out_ratio)

        logger.debug('postprocess+')
        image = TfPoseEstimator.draw_humans(flip_image, humans, imgcopy=False)

        logger.debug('show+')
        fps_time = time.time()
        cv2.putText(flip_image,
                    "FPS: %f" % (1.0 / (time.time() - fps_time)),
                    (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)

 #------------------목의 절점 따는 부분 ----------------       
        cv2.imshow('tf-pose-estimation result', flip_image)
        x,y=image[1]
        print(x,y)
 #------------------목의 절점 따는 부분 ----------------   
    
        if cv2.waitKey(1) == 27:
            break
        logger.debug('finished+')

    cv2.destroyAllWindows()
#320x176