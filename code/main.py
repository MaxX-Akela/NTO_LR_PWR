#!/usr/bin/env python3
import rospy
import math
from geometry_msgs.msg import Point
from visualization_msgs.msg import Marker, MarkerArray
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from clover import srv
from clover import long_callback
import cv2
import numpy as np

rospy.init_node('cv')
bridge = CvBridge()

get_telemetry = rospy.ServiceProxy('get_telemetry', srv.GetTelemetry)
navigate = rospy.ServiceProxy('navigate', srv.Navigate)
navigate_global = rospy.ServiceProxy('navigate_global', srv.NavigateGlobal)
set_position = rospy.ServiceProxy('set_position', srv.SetPosition)
set_velocity = rospy.ServiceProxy('set_velocity', srv.SetVelocity)
set_attitude = rospy.ServiceProxy('set_attitude', srv.SetAttitude)
set_rates = rospy.ServiceProxy('set_rates', srv.SetRates)
land = rospy.ServiceProxy('land', Trigger)


marker_pub = rospy.Publisher('/pipeline_markers', MarkerArray, queue_size=10)

junctions = []  
main_pipe_points = [] 

def navigate_wait(x=0, y=0, z=0, yaw=float('nan'), speed=0.5, frame_id='', auto_arm=False, tolerance=0.2):
    navigate(x=x, y=y, z=z, yaw=yaw, speed=speed, frame_id=frame_id, auto_arm=auto_arm)

    while not rospy.is_shutdown():
        telem = get_telemetry(frame_id='navigate_target')
        if math.sqrt(telem.x ** 2 + telem.y ** 2 + telem.z ** 2) < tolerance:
            break
        rospy.sleep(0.2)

def land_wait():
    land()
    while get_telemetry().armed:
        rospy.sleep(0.2)

@long_callback
def image_callback(msg):
    global junctions
    img = bridge.imgmsg_to_cv2(msg, 'bgr8')
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower = (35, 80, 50)
    upper = (85, 255, 255)

    mask = cv2.inRange(img_hsv, lower, upper)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for c in contours:
        area = cv2.contourArea(c)
        if area < 300:
            continue

        telem = get_telemetry(frame_id='aruco_map')
        p = Point(telem.x, telem.y, 0)

        if not any(math.hypot(p.x-j.x, p.y-j.y)<0.5 for j in junctions):
            junctions.append(p)

    markers = MarkerArray()

    if len(main_pipe_points) > 1:
        line_marker = Marker()
        line_marker.header.frame_id = 'aruco_map'
        line_marker.header.stamp = rospy.Time.now()
        line_marker.ns = 'main_pipe'
        line_marker.id = 0
        line_marker.type = Marker.LINE_STRIP
        line_marker.action = Marker.ADD
        line_marker.scale.x = 0.05 
        line_marker.color.r = 0.0
        line_marker.color.g = 1.0
        line_marker.color.b = 0.0
        line_marker.color.a = 1.0
        line_marker.points = main_pipe_points
        markers.markers.append(line_marker)

    for idx, j in enumerate(junctions):
        m = Marker()
        m.header.frame_id = 'aruco_map'
        m.header.stamp = rospy.Time.now()
        m.ns = 'junctions'
        m.id = idx+1
        m.type = Marker.SPHERE
        m.action = Marker.AD 
        m.pose.position = j
        m.pose.orientation.w = 1.0
        m.scale.x = 0.1
        m.scale.y = 0.1
        m.scale.z = 0.1
        m.color.r = 1.0
        m.color.g = 0.0
        m.color.b = 0.0
        m.color.a = 1.0
        markers.markers.append(m)

    marker_pub.publish(markers)

rospy.Subscriber('main_camera/image_raw', Image, image_callback)



rospy.spin()
