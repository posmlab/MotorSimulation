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
    bear.set_p_gain_iq((m_id, .099))##0.099 originally
    bear.set_i_gain_iq((m_id, .039))##0.039 
    bear.set_d_gain_iq((m_id, 0))
    bear.set_p_gain_id((m_id, .099))##0.099 originally
    bear.set_i_gain_id((m_id, 0.039))##0.039 
    bear.set_d_gain_id((m_id, 0))

    bear.set_p_gain_velocity((m_id, 0.5))
    bear.set_i_gain_velocity((m_id, 0.001))
    bear.set_d_gain_velocity((m_id, 0))

    # motor parameters
    #stallCurrent = 5  #initial testing set to 5
    freeSpeed = 5 ##initial testing set to 20
    # set maximums
    #bear.set_limit_velocity_max((m_id,freeSpeed))
    #bear.set_limit_i_max((m_id,stallCurrent))

    # set up logging array (time, iq, id, maximum torque current, speed, maximum speed)
    loggingArray = []

    input("press enter to start")
    run = True

    startTime = time.time()

    bear.set_mode((m_id, 1))  #velocity mode

    bear.set_torque_enable((m_id, 1))

    goalvelocity = freeSpeed
    bear.set_goal_velocity((m_id, goalvelocity))

    while run:
        # check current performance
        currentSpeed = bear.get_present_velocity(m_id)[0][0][0]
        currentid = bear.get_present_id(m_id)[0][0][0]
        currentiq = bear.get_present_iq(m_id)[0][0][0]

        currentTime = time.time() - startTime
                
        loggingArray += [[currentTime, currentiq, currentid, currentSpeed, goalvelocity]]

        #print("Press any key to stop.")

        if msvcrt.kbhit():
            bear.set_torque_enable((m_id, 0))
            a = np.array(loggingArray)
            np.savetxt('VelocityMode5radsaavideo1.csv', a, delimiter=',')
            run = False
            print("Demo terminated by user.")
            break
    
        time.sleep(.01)
