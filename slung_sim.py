# -*- coding: utf-8 -*-
"""
Created on Sun Jul  4 16:49:33 2021

@author: aviat
"""

from physics_manager import PhysicsManager
from gui import GUI

import signal
import argparse

# Constants
HEADLESS = False
TIME_SCALING = 3.0 # Any positive number(Smaller is faster). 1.0->Real Time, 0.0->Run as fast as possible
PHYSICAL_DYNAMICS_UPDATE = 0.0005 # seconds
CONTROLLER_DYNAMICS_UPDATE = 0.005 # seconds
run = True

def Slung_Stationary():
    # Set goals to go to
    GOALS_1 = [{'time': 0,  'position': (-1,-1,4)},
               {'time': 8,  'position': ( 1, 1,2)}]
    SIM_DURATION = 16 # simulated seconds
    # Define the quadcopters
    QUADCOPTER_DEFS={
        'q1':{'position':[1,0,4],'orientation':[0,0,0],'L':0.3,'r':0.1,'prop_size':[10,4.5],'mass':1.0},
    }
    PAYLOAD_DEFS={
        'p1':{'position':[1,0,2],'orientation':[0,0,0],'x':0.4,'y':0.4,'z':0.2,'mass':0.4,
              #'hardpoints':[[0.2,0.2,0],[-0.2,0.2,0],[-0.2,-0.2,0],[0.2,-0.2,0]]}
              'hardpoints':[[0.3,0,0],[0,0.3,0],[-0.3,0,0],[0,-0.3,0]]}
    }
    # Controller parameters
    CONTROLLER_DEFS={
        'q1':{
            'Type':'pid_p2p',
            'Goals':GOALS_1,
            'Motor_limits':[4000,9000],
            'Tilt_limits':[-10,10],
            'Yaw_Control_Limits':[-900,900],
            'Z_XY_offset':500,
            'Linear_PID':{'P':[300,300,7000],'I':[0.04,0.04,4.5],'D':[450,450,5000]},
            'Linear_To_Angular_Scaler':[1,1,0],
            'Yaw_Rate_Scaler':0.18,
            'Angular_PID':{'P':[22000,22000,1500],'I':[0,0,1.2],'D':[12000,12000,0]},
        }
    }
    # Make objects for dynamics (quadcopters/controllers) and gui
    phys = PhysicsManager(QUADCOPTER_DEFS, CONTROLLER_DEFS, PAYLOAD_DEFS)
    if not HEADLESS:
        gui = GUI(QUAD_DEFS=QUADCOPTER_DEFS, LOAD_DEFS=PAYLOAD_DEFS, get_data=phys.visual_data, get_time=phys.get_time)
    # Catch Ctrl+C to stop threads
    signal.signal(signal.SIGINT, phys.on_keyboard_interrupt)
    # Start the threads
    phys.start_threads(phys_dt=PHYSICAL_DYNAMICS_UPDATE, ctrl_dt=CONTROLLER_DYNAMICS_UPDATE, time_scaling=TIME_SCALING)
    # Update the GUI while switching between destination poitions
    if not HEADLESS:
        gui.animate(duration=SIM_DURATION, pause_sim=phys.pause_threads, frame_rate=30)
        gui.close()
    # Stop threads once animations are done, and when sim is done
    #phys.wait_until_time(SIM_DURATION, check_quit)
    phys.stop_threads()

def parse_args():
    parser = argparse.ArgumentParser(description="Quadcopter Simulator")
    parser.add_argument("--headless", help='Run without GUI', action='store_true')
    parser.add_argument("--sim", help='slung_stat', default='slunt_stat')
    parser.add_argument("--time_scale", type=float, default=-1.0, help='Time scaling factor. 0.0:fastest,1.0:realtime,>1:slow, ex: --time_scale 0.1')
    parser.add_argument("--quad_update_time", type=float, default=0.0, help='delta time for quadcopter dynamics update(seconds), ex: --quad_update_time 0.002')
    parser.add_argument("--controller_update_time", type=float, default=0.0, help='delta time for controller update(seconds), ex: --controller_update_time 0.005')
    return parser.parse_args()

def check_quit():
    global run
    return not run

if __name__ == "__main__":
    args = parse_args()
    if args.headless: HEADLESS = True
    if args.time_scale>=0: TIME_SCALING = args.time_scale
    if args.quad_update_time>0: QUAD_DYNAMICS_UPDATE = args.quad_update_time
    if args.controller_update_time>0: CONTROLLER_DYNAMICS_UPDATE = args.controller_update_time
    Slung_Stationary()
    # if args.sim == 'slung_stat':
    #     Slung_Stationary()