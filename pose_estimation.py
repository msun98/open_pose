import argparse
import logging
import time

import cv2, time
from ptz_api import *
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
sc = 0.8
sh,sw=int(sc*1080),int(sc*1920) # 화면크기
pp,ps,tp,ts=0,80,0,80
target_fps = 30
delay = round(1000 / target_fps)
#---------------------------------------------------------------------------------------------------------------

def key_event():
    k = cv2.waitKey(delay)

    if k==83: # 방향키 방향 전환 0x270000==right 
        move('right', pt_spd)
        stop('right', pt_spd)
        #print(position(data['panpos']))

    elif k==84: # 방향키 방향 전환 0x280000==down 
        move('down', pt_spd)
        stop('down',pt_spd)

    elif k==81: # 방향키 방향 전환 0x250000==left 
        move('left',pt_spd)
        stop('left',pt_spd)

    elif k==82: # 방향키 방향 전환 0x260000==up
        move('up', pt_spd)
        stop('up', pt_spd)

    elif k==110: # 방향키 방향 전환 0x260000==now (현재 상태를 알려줌 (각도정보))
        A=get_position()   
        print('현재 pan:',A[0], ',tilt:',A[1])
        
    elif k==105: # 방향키 방향 전환 0x260000==in(i)
        move('in', pt_spd)
        stop('in', pt_spd)

    elif k==111: # 방향키 방향 전환 0x260000==out(o)
        move('out', pt_spd)
        stop('out', pt_spd)

    elif k==115: # 방향키 방향 전환 0x270000==spherical(s) : 구면 좌표계상의 각도 반환 
        #world2sphere()
        send_theta, send_pi = goto_want_point()
        moveTo('right', int(send_theta*100), int(send_pi*100), pt_spd)

    elif k==48: # 방향키 방향 전환 0x270000==(0,0) a = 35999-a
        goto_origin(pp,ps,tp,ts)
        initialize_pt_variable()

    return k


#---------------------------------------------------------------------------------------------------------------
def initialize():
    global vcap, ax, dots
    rtsp_addr='rtsp://192.168.0.9/stream1'
    web_addr='192.168.0.9'
    PTZ_head='http://'+web_addr+'/cgi-bin/control/'

    # rtsp_addr='rtsp://117.17.187.60:554/stream1'
    # web_addr='117.17.187.60:554'
    # PTZ_head='http://'+web_addr+'/cgi-bin/control/'

    cv2.namedWindow('VIDEO')
    vcap = cv2.VideoCapture(rtsp_addr)
    #cv2.setMouseCallback('VIDEO', mouse_callback)

    # print('default resolution is: {}x{}'.format(\
    #     int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    print('start camera')
    print('zoom factor is {}'.format(int(get_position()[2])))
    print()
    vcap.set(cv2.CAP_PROP_FPS, 30)

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


if __name__ == '__main__':

    initialize() 
    on_screen_display()
    time.sleep(0.1)
    h,w = 833,1527
    pt_spd,zoom_spd=70,70

    parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
    parser.add_argument('--camera', type=int, default=0)

    parser.add_argument('--resize', type=str, default='320x176',
                        help='if provided, resize images before they are processed. default=0x0, Recommends : 432x368 or 656x368 or 1312x736 ')
    parser.add_argument('--resize-out-ratio', type=float, default=4.0,
                        help='if provided, resize heatmaps before they are post-processed. default=1.0')

    parser.add_argument('--model', type=str, default='mobilenet_thin', help='cmu / mobilenet_thin / mobilenet_v2_large / mobilenet_v2_small')
    parser.add_argument('--show-process', type=bool, default=False,
                        help='for debug purpose, if enabled, speed for inference is dropped.')
    
    parser.add_argument('--tensorrt', type=str, default="False",
                        help='for tensorrt process.')
    args = parser.parse_args()

    logger.debug('initialization %s : %s' % (args.model, get_graph_path(args.model)))
    w, h = model_wh(args.resize)
    if w > 0 and h > 0:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h), trt_bool=str2bool(args.tensorrt))
    else:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(432, 368), trt_bool=str2bool(args.tensorrt))
    logger.debug('cam read+')
    #cam = cv2.VideoCapture(rtsp_addr)
    ret_val, image = vcap.read()
    logger.info('cam image=%dx%d' % (image.shape[1], image.shape[0]))

    while True:
        ret_val, image = vcap.read()

        logger.debug('image process+')
        humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size=args.resize_out_ratio)
        print(humans)

        logger.debug('postprocess+')
        image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)

        logger.debug('show+')
        flipped_video = cv2.flip(image,1)
        cv2.putText(flipped_video,
                    "FPS: %f" % (1.0 / (time.time() - fps_time)),
                    (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        cv2.imshow('tf-pose-estimation result', flipped_video)
        fps_time = time.time()
        k = key_event()
        
        if k == 27:
            break
        logger.debug('finished+')

    cv2.destroyAllWindows()