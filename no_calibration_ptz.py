import cv2, time
import numpy as np
from ptz_api import *

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


#---------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    initialize() 
    on_screen_display()
    time.sleep(0.1)
    h,w = 833,1527
    pt_spd,zoom_spd=70,70

    while True:
        if vcap.isOpened():
            ret, raw = vcap.read()
            if not ret:
                break

            frame = cv2.resize(raw, dsize=(sw, sh), interpolation=cv2.INTER_AREA) # 화면 크기에 관함.
            cv2.imshow('VIDEO',frame)

            k = key_event()
        if k == 27: # ESCAPE
            break
    else:
        print('open failed!')
    vcap.release()
    cv2.destroyAllWindows()