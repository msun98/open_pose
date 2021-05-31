import cv2, time, math
from ptz_api import *
import numpy as np

fps_time = 0
sc = 0.8
sh,sw=int(sc*1080),int(sc*1920) # 화면크기
pp,ps,tp,ts=0,80,0,80
target_fps = 30
delay = round(1000 / target_fps)
mtx = np.matrix([[1.38131962e+03, 0.00000000e+00, 7.92518109e+02],[0.00000000e+00, 1.38572510e+03, 4.12779024e+02],[0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
dist = np.matrix([[-1.94343750e-01, -1.89498296e-01, -1.58584191e-03, -3.29181495e-04, 7.83809624e-01]])

pt_spd,zoom_spd=70,70

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
    rtsp_addr='rtsp://192.168.0.9/stream1'
    web_addr='192.168.0.9'
    PTZ_head='http://'+web_addr+'/cgi-bin/control/'

    # rtsp_addr='rtsp://117.17.187.60:554/stream1'
    # web_addr='117.17.187.60:554'
    # PTZ_head='http://'+web_addr+'/cgi-bin/control/'

    cv2.namedWindow('VIDEO')
    vcap = cv2.VideoCapture(rtsp_addr)
    cv2.setMouseCallback('VIDEO', mouse_callback)

    # print('default resolution is: {}x{}'.format(\
    #     int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    print('start camera')
    print('zoom factor is {}'.format(int(get_position()[2])))
    print()
    vcap_set = vcap.set(cv2.CAP_PROP_FPS, 30)
    return vcap

#--------------------------------------------------------------------------------------------------
def mouse_callback(event, u_p, v_p, flags, param): # 마우스 왼쪽을 눌렀을 경우 발생.
    if event != cv2.EVENT_LBUTTONDOWN:
        return

    angle = tuple(x//100 for x in get_position())   # (pan, tilt, zoom)
    print("움직이기 전 API 각도 데이터 : [{:5.2f}, {:5.2f}, {:5.2f}]".format(*angle))
    view2sphere(u_p,v_p)
    send_theta, send_pi = camera2world()
    moveTo('right', int(send_theta*100), int(send_pi*100), pt_spd)
    print()

#--------------------------------------------------------------------------------------------------
def calibration(image,w,h):
	frame = cv2.resize(image, dsize=(sw, sh), interpolation=cv2.INTER_AREA) # 화면 크기에 관함.
	newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),0,(w,h))
	mapx,mapy = cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,(w,h),5)
	dst = cv2.remap(frame,mapx,mapy,cv2.INTER_LINEAR)
	dst = cv2.line(dst, (0, h//2), (w, h//2), (109, 113, 116), 3)
	dst = cv2.line(dst, (w//2, 0), (w//2, h), (109, 113, 116), 3)
	dst = cv2.line(dst,(763,416),(763,416),(180,130,130),30)
	flip_video = cv2.flip(dst,1)
	return flip_video