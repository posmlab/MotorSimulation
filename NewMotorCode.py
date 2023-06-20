#!usr/bin/env python

from pybear import Manager
import sys
import select
import os
import msvcrt
import time
import numpy as np

bearPort = input("Enter the port of the motor (COM_): ")

error = False
bear = Manager.BEAR(port=bearPort, baudrate=8000000)

m_id = 1

if not(bear.ping(m_id)):
    # BEAR is offline
    print("BEAR is offline. Check power and communication.")
    error = True

if not error:
    
    # torque gains
    bear.set_p_gain_iq((m_id, 0.095)) ##0.099 originally
    bear.set_i_gain_iq((m_id, 0.035)) ##0.039 
    bear.set_d_gain_iq((m_id, 0))
    bear.set_p_gain_id((m_id, 0.095)) ##0.099
    bear.set_i_gain_id((m_id, 0.035)) ##0.039
    bear.set_d_gain_id((m_id, 0))

    # speed gains
    bear.set_p_gain_velocity((m_id, 0.5))
    bear.set_i_gain_velocity((m_id, 0.001))
    bear.set_d_gain_velocity((m_id, 0))

    # motor mode
    bear.set_mode((m_id, 1))  #1 is velocity mode; 3 is Force mode where we can do both velocity and torque stuff in 

 # stuff to make the motor curve
    # motor parameters
    stallCurrent = 5  #initial testing set to 5
    freeSpeed = 5 #5400  ##initial testing set to 20 (check if this should be in rps instead of rpm)

    # get current excitation current
    currentid = bear.get_present_id(m_id)[0][0][0]
    print("Currentid",currentid)
    # calculate desired torque, speed
    goalSpeed = freeSpeed
    goalTorque = stallCurrent*(1-goalSpeed/freeSpeed) 

    # set maximums
    bear.set_limit_velocity_max((m_id,freeSpeed))
    bear.set_limit_i_max((m_id,goalTorque))

    # set up logging array (time, iq, id, maximum torque current, speed, maximum speed)
    loggingArray = []

    input("press enter to start")
    run = True

    startTime = time.time()

    bear.set_torque_enable((m_id, 1)) 

    # run motor at desired torque, speed
    bear.set_goal_velocity((m_id, goalSpeed))

    while run:

        # check current performance
        currentSpeed = bear.get_present_velocity(m_id)[0][0][0]
        currentid = bear.get_present_id(m_id)[0][0][0]
        currentiq = bear.get_present_iq(m_id)[0][0][0]
        currentVoltage = bear.get_input_voltage(m_id)[0][0][0]

        goalTorque = stallCurrent*( 1  - currentSpeed/freeSpeed)
        
        print("goal Torque: ", goalTorque, " Current Torque: ",currentiq, "goal speed: ", goalSpeed, " Current Speed: ", currentSpeed)
        bear.set_limit_i_max((m_id, goalTorque))
                
        currentTime = time.time() - startTime
                
        loggingArray += [[currentTime, currentiq, currentid, goalTorque, currentSpeed, goalSpeed, currentVoltage]]

        #print("Press any key to stop.")

        if msvcrt.kbhit():
            bear.set_torque_enable((m_id, 0))
            a = np.array(loggingArray)
            np.savetxt('NewMotorCodeCurrentOneTorque.csv', a, delimiter=',')
            run = False
            print("Demo terminated by user.")
            break
    
        time.sleep(.01)
