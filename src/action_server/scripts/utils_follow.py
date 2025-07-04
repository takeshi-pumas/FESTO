#!/usr/bin/env python3
import cv2
import rospy 
import numpy as np
import pandas as pd
import smach
import smach_ros
import actionlib
import rospkg
import yaml
import tf
import time
import moveit_commander
import moveit_msgs.msg
import tf2_ros
from geometry_msgs.msg import PoseStamped, Point , PointStamped , Quaternion , TransformStamped , Twist
from std_msgs.msg import Bool
from std_srvs.srv import Trigger, TriggerResponse, Empty
from sensor_msgs.msg import Image , LaserScan , PointCloud2
from tf2_sensor_msgs.tf2_sensor_msgs import do_transform_cloud
from object_classification.srv import *
from segmentation.srv import *
from human_detector.srv import Human_detector ,Human_detectorResponse 
from human_detector.srv import Point_detector ,Point_detectorResponse 
from object_classification.srv import *
from face_recog.msg import *
from face_recog.srv import *
#import face_recognition 
from hmm_navigation.msg import NavigateActionGoal, NavigateAction
from cv_bridge import CvBridge, CvBridgeError
from nav_msgs.msg import OccupancyGrid
from hri_msgs.msg import RecognizedSpeech
from rospy.exceptions import ROSException
from ros_whisper_vosk.srv import SetGrammarVosk, GetSpeech
from action_server.msg import FollowActionGoal
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from utils import grasp_utils
from utils.misc_utils import *
from utils.nav_utils import *
from utils import grasp_utils, misc_utils


from geometry_msgs.msg import WrenchStamped
global listener, broadcaster, tfBuffer, tf_static_broadcaster, scene, rgbd, head,train_new_face, wrist, human_detect_server, line_detector, clothes_color , head_mvit
global clear_octo_client, goal,navclient,segmentation_server  , tf_man , omni_base, brazo, speech_recog_server, bridge, map_msg, pix_per_m, analyze_face , arm , set_grammar
global recognize_action , classify_client,pointing_detect_server  , hand_cam , pub_goal, voice
rospy.init_node('follow_action_server', anonymous=True)
#arm =  moveit_commander.MoveGroupCommander('arm')
#head_mvit = moveit_commander.MoveGroupCommander('head')
#gripper =  moveit_commander.MoveGroupCommander('gripper')
#whole_body=moveit_commander.MoveGroupCommander('whole_body')

#broadcaster = tf.TransformBroadcaster()
tfBuffer = tf2_ros.Buffer()
pub_goal= rospy.Publisher('/clicked_point',PointStamped,queue_size=10)
listener = tf2_ros.TransformListener(tfBuffer)
broadcaster = tf2_ros.TransformBroadcaster()
tf_static_broadcaster = tf2_ros.StaticTransformBroadcaster()
clear_octo_client = rospy.ServiceProxy('/clear_octomap', Empty)   ###OGRASPING OBSTACLE 
human_detect_server = rospy.ServiceProxy('/detect_human' , Human_detector)  ####HUMAN FINDER OPPOSEBASED
pointing_detect_server = rospy.ServiceProxy('/detect_pointing' , Point_detector)  ####HUMAN FINDER OPPOSEBASED
segmentation_server = rospy.ServiceProxy('/segment' , Segmentation)    ##### PLANE SEGMENTATION (PARALEL TO FLOOR)
navclient=actionlib.SimpleActionClient('/navigate', NavigateAction)   ### PUMAS NAV ACTION LIB

# scene = moveit_commander.PlanningSceneInterface()
speech_recog_server = rospy.ServiceProxy('/speech_recognition/vosk_service' ,GetSpeech)##############SPEECH VOSK RECOG FULL DICT
set_grammar = rospy.ServiceProxy('set_grammar_vosk', SetGrammarVosk)                   ###### Get speech vosk keywords from grammar (function get_keywords)         
recognize_face = rospy.ServiceProxy('recognize_face', RecognizeFace)                    #FACE RECOG
train_new_face = rospy.ServiceProxy('new_face', RecognizeFace)                          #FACE RECOG
analyze_face = rospy.ServiceProxy('analyze_face', RecognizeFace)    ###DEEP FACE ONLY
classify_client = rospy.ServiceProxy('/classify', Classify)
global hand_pushed
hand_pushed = False
def hand_callback(msg):
    global hand_pushed
    torque = msg.wrench.torque.y
    if np.abs(torque)>1.0:
        hand_pushed = True

hand_suscriber = rospy.Subscriber("/hsrb/wrist_wrench/compensated", WrenchStamped, hand_callback)

enable_mic_pub = rospy.Publisher('/talk_now', Bool, queue_size=10)
#map_msg= rospy.wait_for_message('/augmented_map', OccupancyGrid , 20)####WAIT for nav pumas map .. 
#inflated_map= np.asarray(map_msg.data)
#img_map=inflated_map.reshape((map_msg.info.width,map_msg.info.height))
#pix_per_m=map_msg.info.resolution
#contours, hierarchy = cv2.findContours(img_map.astype('uint8'),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
#contoured=cv2.drawContours(img_map.astype('uint8'), contours, 1, (255,255,255), 1)

rgbd= RGBD()
bridge = CvBridge()
#segmentation_server = rospy.ServiceProxy('/segment_2_tf', Trigger) 
tf_man = TF_MANAGER()
#gripper = GRIPPER()
#omni_base=OMNIBASE()        #  NAV ACTION
#omni_base=NAVIGATION()     #  nav UTILS
#wrist= WRIST_SENSOR()
#head = GAZE()
brazo = grasp_utils.ARM(joint_names = ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6"], 
                      arm_controller_action_client = "/xarm/xarm6_traj_controller/follow_joint_trajectory")
head= grasp_utils.GAZE(arm=brazo)
voice = misc_utils.Talker()

#line_detector = LineDetector()
# arm =  moveit_commander.MoveGroupCommander('arm')



#------------------------------------------------------
def set_pushed_false():
    global hand_pushed
    hand_pushed = False
#------------------------------------------------------
def is_pushed():
    global hand_pushed
    return hand_pushed
#------------------------------------------------------
def get_robot_px():
    trans, rot=tf_man.getTF('base_link')
    robot=np.asarray(trans[:2])
    
    return np.asarray((robot/pix_per_m).round(),dtype='int')

#------------------------------------------------------
def check_point_map(x,y):

    # Quiero saber punto 0,-7 m esta libre?
    ##meters, map (not pixels)
    #x,y=0.2,8
    #px=check_point_map(x,y)  # px is closest safe goal
    #px*pix_per_m
    xrob,yrob=get_robot_px()
    safe_xy=np.asarray((x,-1*y))
    safe_xy_px=point_to_px (x,y)
    delta_px=  safe_xy_px-np.asarray((xrob,yrob))
    delta_px= delta_px / np.linalg.norm(delta_px).round()
    delta_px=np.round(delta_px*10)
    newxy=np.zeros(2)
    
    for i in range(9):
        if (contoured[1024+ safe_xy_px[1].astype('int'),1024-safe_xy_px[0].astype('int')]!=0):   ## axis are twisted cause y sign
                    print ('not safe at', safe_xy_px , safe_xy_px*pix_per_m)
                    
                    xrob,yrob=get_robot_px()
                    delta_px=  safe_xy_px-np.asarray((xrob,yrob))
                    delta_px= delta_px / np.linalg.norm(delta_px).round()
                    delta_px=np.round(delta_px*10)
                    newxy[0]=safe_xy_px[0]-delta_px[0].astype('int')
                    newxy[1]=safe_xy_px[1]-delta_px[1].astype('int')
                    safe_xy_px=newxy
        else:
                print ('safe at', safe_xy_px, safe_xy_px*pix_per_m)
                return safe_xy_px
    return safe_xy_px
    
#------------------------------------------------------
def point_to_px(x,y):
    safe_xy=np.asarray((x,y))
    return np.round(safe_xy/pix_per_m).astype('int')
def px_to_point(px,py):
    return np.asarray((px,py))*pix_per_m

#------------------------------------------------------
def train_face(image, name):
    req=RecognizeFaceRequest()
    strings=Strings()
    string_msg= String()
    string_msg.data=name
    req.Ids.ids.append(string_msg)

    img_msg=bridge.cv2_to_imgmsg(image)
    req.in_.image_msgs.append(img_msg)
    res=train_new_face(req)
    
    return res.Ids.ids[0].data.split(' ')[0] == 'trained'

    #------------------------------------------------------
def wait_for_face(timeout=10 , name=''):
    
    rospy.sleep(0.3)
    
    start_time = rospy.get_time()
    strings=Strings()
    string_msg= String()
    string_msg.data='Anyone'
    while rospy.get_time() - start_time < timeout:
        img=rgbd.get_image()  
        req=RecognizeFaceRequest()
        print ('Got  image with shape',img.shape)
        req.Ids.ids.append(string_msg)
        img_msg=bridge.cv2_to_imgmsg(img)
        req.in_.image_msgs.append(img_msg)

        res= recognize_face(req)


        #NO FACE FOUND
        if res.Ids.ids[0].data == 'NO_FACE':
            print ('No face FOund Keep scanning')
            
            return None, None
        #AT LEAST ONE FACE FOUND
        else:
            print('at least one face found')
            ds_to_faces=[]
            for i , idface in enumerate(res.Ids.ids):
                print (i,idface.data)
                ds_to_faces.append(res.Ds.data[i])    ##
                if (idface.data)==name :
                    new_res= RecognizeFaceResponse()
                    new_res.Ds.data= res.Ds.data[i]
                    new_res.Angs.data= res.Angs.data[i:i+4]
                    new_res.Ids.ids=res.Ids.ids[i].data
                    print('return res,img',new_res)
                    print ('hit',idface.data, 'at' , res.Ds.data[i]  , 'meters')
                    ds_to_faces=[]
                    return new_res , img

            if len (ds_to_faces)!=0:
                i=np.argmin(ds_to_faces)
                new_res= RecognizeFaceResponse()
                new_res.Ds.data= res.Ds.data[i]
                new_res.Angs.data= res.Angs.data[i:i+4]
                new_res.Ids.ids=res.Ids.ids[i].data
                print('return res,img',new_res)
                ds_to_faces=[]
                return new_res , img





#------------------------------------------------------
#def wait_for_face(timeout=10):
#    
#    rospy.sleep(0.3)
#    
#    start_time = rospy.get_time()
#    strings=Strings()
#    string_msg= String()
#    string_msg.data='Anyone'
#    while rospy.get_time() - start_time < timeout:
#        img=rgbd.get_image()  
#        req=RecognizeFaceRequest()
#        print ('Got  image with shape',img.shape)
#        req.Ids.ids.append(string_msg)
#        img_msg=bridge.cv2_to_imgmsg(img)
#        req.in_.image_msgs.append(img_msg)
#
#        res= recognize_face(req)
#
#        if res.Ids.ids[0].data == 'NO_FACE':
#            print ('No face FOund Keep scanning')
#            return None, None
#        
#        else:return res , img
##------------------------------------------------------
def wait_for_push_hand(time=10):
    talk ('push for stop')
    start_time = rospy.get_time()
    time= 10
    print('timeout will be ',time,'seconds')
    while rospy.get_time() - start_time < time:
        torque = wrist.get_torque()
        if np.abs(torque[1])>1.0:
            print(' Hand Pused Ready TO start')
            #takeshi_talk_pub.publish(string_to_Voice())
            talk('Hand Pushed')
            return True
            break

    if (rospy.get_time() - start_time >= time):
        print(time, 'secs have elapsed with no hand push')
        return False
#
##------------------------------------------------------
def analyze_face_from_image(cv2_img,name=''):   
    #USING DEEP FACE SERVICE
    # FIND SOME CHARACTERISTICS FROM A FACE IMAGE
    req=RecognizeFaceRequest()
    strings=Strings()
    string_msg= String()
    string_msg.data='analyze '
    req.Ids.ids.append(string_msg)
    img_msg=bridge.cv2_to_imgmsg(cv2_img)
    req.in_.image_msgs.append(img_msg)
    #res=recognize(req)
    res = analyze_face(req)
    results=[]
    for chars in res.Ids.ids:
        results.append(chars.data)
    if (len(results)==1):return ''  ###NO FACE
    #name= 'Jack'
    pronoun='she'
    gender = results[0]
    age = results[-1]
    state = results[2]
    race = results[1]
    if gender=='Man':pronoun='he'
    takeshi_line = f'{name} has arrived... {pronoun} is a {gender}... I believe {pronoun}.' 
    takeshi_line += f'is  around  {age} years old... I would say he is a bit  {state}.'
    takeshi_line += f'And I might guess {pronoun} is of {race} descent.'
    return takeshi_line

#------------------------------------------------------
def bbox_3d_mean(points,boundRect):
    #Gets the mean of the Points from the pincloud enclosed in the bound Rect of the RGBD image

    xyz=[]
    xyz_n=points[['x','y','z']][boundRect[0]:boundRect[2],boundRect[3]:boundRect[1]]
    for i in range(xyz_n.shape[0]):
        for j in range(xyz_n.shape[1]):
            if ~np.isnan(xyz_n['x'][i,j]) and ~np.isnan(xyz_n['y'][i,j]) and ~np.isnan(xyz_n['z'][i,j]):
                xyz.append(np.asarray([xyz_n['x'][i,j],xyz_n['y'][i,j],xyz_n['z'][i,j]]))
                
    if len(xyz)!=0:
        return np.asarray(xyz).mean(axis=0)
    else:
        return np.ones(3)



#------------------------------------------------------
def read_yaml(known_locations_file='/known_locations.yaml'):
    rospack = rospkg.RosPack()
    file_path = rospack.get_path('config_files') + known_locations_file

    with open(file_path, 'r') as file:
        content = yaml.safe_load(file)
    return content
#----------------------------------------------------------
def yaml_to_df(known_locations_file='/known_locations.yaml'):
    con = read_yaml(known_locations_file)
    values=[]
    locations=[]
    for c in con:
        locations.append(c)

        for i in range(len(con[c])):
            values.append(list(con[c][i].values())[0])

    data=np.asarray(values).reshape((int(len(values)/7),7))    #x , y ,theta  ,quat   since z always 0
    df= pd.DataFrame( data)
    df.columns=['x','y','th','qx','qy','qz','qw']
    df['child_id_frame']=locations
    return df





#------------------------------------------------------
def read_tf(t):
    # trasnform message to np arrays
    pose=np.asarray((
        t.transform.translation.x,
        t.transform.translation.y,
        t.transform.translation.z
        ))
    quat=np.asarray((
        t.transform.rotation.x,
        t.transform.rotation.y,
        t.transform.rotation.z,
        t.transform.rotation.w
        ))
    
    return pose, quat
#------------------------------------------------------

def gaze_to_face():

    return False

#------------------------------------------------------
def seg_res_tf(res):
    origin_map_img=[round(img_map.shape[0]*0.5) ,round(img_map.shape[1]*0.5)]   
    
    #brazo.set_named_target('go')
    if len(res.poses.data)==0:
        print('no objs')
        return False
    else:
        
        poses=np.asarray(res.poses.data)
        quats=np.asarray(res.quats.data)
        poses=poses.reshape((int(len(poses)/3) ,3     )      )  
        quats=quats.reshape((int(len(quats)/4) ,4     )      )  
        num_objs=len(poses)
        print(f'{num_objs} found')

        for i,cent in enumerate(poses):
            x,y,z=cent
            axis=[0,0,1]
            angle = tf.transformations.euler_from_quaternion(quats[i])[0]
            rotation_quaternion = tf.transformations.quaternion_about_axis(angle, axis)
            point_name=f'object_{i}'
            print (f'{point_name} found at {cent}')
            tf_man.pub_tf(pos=cent, rot =[0,0,0,1], point_name=point_name+'_norot', ref='map')## which object to choose   #TODO
            #tf_man.pub_tf(pos=cent, rot =rotation_quaternion, point_name=point_name, ref='map')## which object to choose   #TODO
            #tf_man.pub_static_tf(pos=cent, rot =[0,0,0,1], point_name=point_name+'_norot', ref='map')## which object to choose   #TODO
            tf_man.pub_static_tf(pos=cent, rot =rotation_quaternion, point_name=point_name, ref='map')## which object to choose   #TODO
            rospy.sleep(0.5)                                                                        
            pose,_= tf_man.getTF(point_name)
            print (f'Occupancy map at point object {i}-> pixels ',origin_map_img[1]+ round(pose[1]/pix_per_m),origin_map_img[0]+ round(pose[0]/pix_per_m), img_map[origin_map_img[1]+ round(pose[1]/pix_per_m),origin_map_img[0]+ round(pose[0]/pix_per_m)])
            ## Pixels from augmented image map server published map image
            if img_map[origin_map_img[1]+ round(pose[1]/pix_per_m),origin_map_img[0]+ round(pose[0]/pix_per_m)]!=0:#### Yes axes seem to be "flipped" !=0:
                print ('reject point suggested ( for floor), most likely part of arena, occupied inflated map')
                #tf_man.pub_static_tf(pos=[0,0,0], point_name=point_name, ref='head_rgbd_sensor_rgb_frame')
                #num_objs-=1
            print (f"object found at map coords.{pose} ")
    return True
#------------------------------------------------------
def detect_human_to_tf():
    humanpose=human_detect_server.call()
    print (humanpose)
    if (np.asarray((humanpose.x,humanpose.y,humanpose.z)).all()== np.zeros(3).all()):
        print (np.asarray((humanpose.x,humanpose.y,humanpose.z)))
        return False
    else:
        tf_man.pub_static_tf(np.asarray((humanpose.x,humanpose.x,humanpose.z)),point_name='human', ref='head_rgbd_sensor_link')
        succ=tf_man.change_ref_frame_tf('human')
        _,quat= tf_man.getTF('base_link')
        pose,_= tf_man.getTF('human')
        rot180 = [0, 0, 1, 0]  # This is (x, y, z, w) format for 180° around Z
        # Perform quaternion multiplication
        quat_rotated = tf.transformations.quaternion_multiply(rot180, quat) 
        tf_man.pub_static_tf(pose, quat_rotated,point_name='human')
        return succ
#------------------------------------------------------

def get_keywords_speech(timeout=5):
    enabled_msg = Bool()
    enabled_msg.data = True
    enable_mic_pub.publish(enabled_msg)
    rospy.sleep(0.5)
    try:
        msg = rospy.wait_for_message('/speech_recognition/final_result', String, timeout)
        result = msg.data
        enabled_msg = Bool()
        enabled_msg.data = False
        enable_mic_pub.publish(enabled_msg)
        #rospy.sleep(1.0)
        return result
            
    except ROSException:
        rospy.loginfo('timeout')
        enabled_msg = Bool()
        enabled_msg.data = False
        enable_mic_pub.publish(enabled_msg)
        return 'timeout'

def check_room_px(px_pose,living_room_px_region,kitchen_px_region,bedroom_px_region,dining_room_px_region ):

    
    for i in range(4):
        if i==0:
            px_region=living_room_px_region
            region='living_room'
        if i==1:
            px_region=kitchen_px_region
            region='kitchen'
        if i==2:
            px_region=bedroom_px_region
            region='bedroom'
        if i==3:
            px_region=dining_room_px_region
            region='dining_room'
        #print (region,px_region,px_pose)
        if (px_pose[1]< px_region[1,1]) and (px_pose[1]> px_region[0,1]) and (px_pose[0]> px_region[0,0]) and (px_pose[0]< px_region[1,0]) : 
            print (f'in  {region}')
            return region

def match_speech(speech, to_match):
    for element in to_match:
        if element in speech:
            return True
    return False



navclient = actionlib.SimpleActionClient('/move_base/move', MoveBaseAction)  #TOYOTA NAV

def move_base(goal_x,goal_y,goal_yaw,frame_id='map' ,time_out=10):

    
    
    
    pose = PoseStamped()
    pose.header.stamp = rospy.Time(0)
    pose.header.frame_id = frame_id
    pose.pose.position = Point(goal_x, goal_y, 0)
    quat = tf.transformations.quaternion_from_euler(0, 0, goal_yaw)
    pose.pose.orientation = Quaternion(*quat)


    # create a MOVE BASE GOAL
    goal = MoveBaseGoal()
    goal.target_pose = pose

    # send message to the action server
    navclient.send_goal(goal)
    print ("naving")
    head.to_tf('human')
    # wait for the action server to complete the order
    navclient.wait_for_result(timeout=rospy.Duration(time_out))
    print ( "waited for  res")

    # print result of navigation
    action_state = navclient.get_state()
    return navclient.get_state()

def move_d_to(self, target_distance=0.5, target_link='None'):
    # Face towards Targetlink and get target distance close
    if target_link != 'None':
        target, _ = tf_man.getTF(target_frame=target_link)
        robot, _ = tf_man.getTF(target_frame='base_link')
        pose, _ = tf_man.getTF(target_frame=target_link, ref_frame='base_link')
    else:
        return False
    delta = np.asarray(target) - np.asarray(robot)

    dist = np.linalg.norm(delta)            
    print (dist)
    theta_goal = np.arctan2(delta[1], delta[0])
    if dist <= target_distance:
        x_goal,y_goal=robot[0],robot[1]
    else:
        x_goal = target[0] - target_distance * np.cos(theta_goal)
        y_goal = target[1] - target_distance * np.sin(theta_goal)
    succ = move_base(
        goal_x=x_goal, goal_y=y_goal, goal_yaw=theta_goal)
    return True
