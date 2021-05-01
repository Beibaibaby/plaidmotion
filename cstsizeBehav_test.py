'''
We want to measure spatial suppression curve and spatial summation curve
Spatial suppression curve: contrast=0.99, radius=[0.7, 3, 5]
Spatial summation curve: contrast=0.02, radius=[0.7, 3, 5]

History:
    2021/04/30 RYZ create it

To do:

'''
import psychopy
from psychopy import core, monitors, clock, visual, event, data
from psychopy.hardware import keyboard
from psychopy.visual import circle
import numpy as np
from time import localtime, strftime
from envelope import envelope


# ======= paremter you want to change ========
subjID = 'RYZ' # initials of the subject, to save data
expName = 'cstsizeBehav' # contrast size EEG 
wantSave = False # save data or not

# ================ exp setting ==================
stimDir = [-1, 1]  # -1, left;1, right
stimRadius = [0.7, 3, 5] # radius in deg
stimContrast = [0.02, 0.99]
speedDeg = 4  # deg/sec, shall convert to deg/frame
sf = 1 # cycle/deg

# ======= setup hardwares =======
mon = monitors.Monitor('hospital6')
mon.setDistance(57)  # View distance cm
mon.setSizePix([1920, 1080])
mon.setWidth(52.71)  # cm
myWin = visual.Window([800, 800], units='deg', monitor=mon, checkTiming=True)
#fps = myWin.getActualFrameRate() # sometimes this call fails...
fps=60

event.globalKeys.clear()
event.globalKeys.add(key='q', func=core.quit)  # global quit
globalClock = clock.Clock()
kb = keyboard.Keyboard()  # create kb object

# Lets do some calculation before going further
phaseStepFrame = speedDeg * sf / fps # how many cycles / frame

# define staircase handler
conditions = []
conditions.append({'label':'c0r0', 'stimContrast':stimContrast[0], 'stimRadius':stimRadius[0], 'startVal':90, 'startValSd':20}) # start value in millisecs
conditions.append({'label':'c0r1', 'stimContrast':stimContrast[0], 'stimRadius':stimRadius[1],'startVal': 70, 'startValSd':20})
conditions.append({'label':'c0r2', 'stimContrast':stimContrast[0], 'stimRadius':stimRadius[2],'startVal': 50, 'startValSd':15})
conditions.append({'label':'c1r0', 'stimContrast':stimContrast[1], 'stimRadius':stimRadius[0],'startVal': 50, 'startValSd':15})
conditions.append({'label':'c1r1', 'stimContrast':stimContrast[1], 'stimRadius':stimRadius[1],'startVal': 70, 'startValSd':20})
conditions.append({'label':'c1r2', 'stimContrast':stimContrast[1], 'stimRadius':stimRadius[2],'startVal': 90, 'startValSd':20})
stairs = data.MultiStairHandler(stairType='quest',conditions=conditions, nTrials=2)

#  ====== define stimulus components =======
# define fixation
fixation = circle.Circle(myWin, units='deg', radius=0.15, lineColor=1, fillColor=1)
# define drift grating
driftGrating = visual.GratingStim(myWin, tex='sin', units='deg', mask='raisedCos', sf=sf)


# define welcome instruction interface
instrText = \
    '欢迎参加这个实验!\n \
    您将在屏幕上看到一个运动的光栅\n \
    光栅运动过后, \n \
    您需要按方向键(左/右)来判断光栅运动方向。\n \
    请您尽可能准确的反应, 反应时并不重要! \n \
    如果您理解了以上的话，请按空格键继续'
tex = visual.TextStim(win=myWin, text=instrText, font='SimHei', wrapWidth=25)
tex.draw()
myWin.flip()
kb.start()
kb.waitKeys(keyList=['space'], waitRelease=True)
kb.stop()
myWin.flip()

# do it !!!
#  =========== main experiment loop ========
for thisDur, thisCon in stairs: # loop trial handler
    # show fixation
    fixation.draw()
    myWin.flip()
    
    # add 1000ms delay while setting the parameters
    ISI = clock.StaticPeriod(screenHz=fps)
    ISI.start(np.random.rand())  # random (0, 1)s delay
    driftGrating.size = thisCon['stimRadius'] * 2 # set size as diameter
    profile, nFrame = envelope(thisDur, frame_rate=fps, amplitude=1)
    # from staircases get stimulus duration
    # trials.addData('stimDur', dur)
    # trials.addData('stimFrames', nFrame) 
    ISI.complete()  # finish the delay period

    # Show the motion stimulus and get RT and choice
    dire = np.random.choice(stimDir)
    for iFrame in range(nFrame): # loop frames
        # driftGrating move one step 
        driftGrating.contrast = profile * thisCon['stimContrast']
        driftGrating.phase = phaseStepFrame * iFrame * dire
        driftGrating.draw()
        myWin.flip()        
    myWin.flip()
    # collect response
    kb.clock.reset()
    kb.start()
    keys=kb.waitKeys(keyList=['left','right'], waitRelease=True)
    kb.stop()

    # save data for this trial
    choice = -1 if keys[0].name=='left' else 1    
    correct = (choice==dire)
    stairs.addOtherData('direction', dire) # we only record the 1st key
    stairs.addOtherData('choice', correct) # we only record the 1st key
    stairs.addResponse(correct, intensity=thisDur)

    # update staircases


# ====cleanup and save data to csv======
if wantSave: # save data
    # we want to save trialHandler
    fileName = strftime('%Y%m%d%H%M%S', localtime())
    fileName = f'{fileName}_{expName}_{subjID}'

    # Save more information into a numpy file 
    expInfo = '''    
        stimDir: stimulus direction, -1,left; 1, right \n 
        stimRadius: stimulus radius deg \n
        stimDur: stimulus duration in secs
        contrast: stimulus contrast, 0~1
        choice: -1, left; 1, right \n
        correct: 1, correct; 0, wrong
    '''
    # create a result dict
    trials.extraInfo={
        'subjID': subjID,
        'time': strftime('%Y-%m-%d-%H-%M-%S', localtime()),
        'expInfo': expInfo,
        'expName': expName
    }
    trials.saveAsExcel(fileName=fileName, sheetName='rawData') # save data as excel
    trials.saveAsPickle(fileName=fileName) # save data as pickle

