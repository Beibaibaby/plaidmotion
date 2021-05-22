'''
We want to measure spatial suppression curve and spatial summation curve
Spatial suppression curve: contrast=0.99, radius=[0.7, 3, 5]
Spatial summation curve: contrast=0.02, radius=[0.7, 3, 5]

History:
    2021/05/16/ Yunlong Xu motified
    2021/04/26 Ruyuan Zhang Create it

'''
import psychopy
from psychopy import core, monitors, clock, visual, event, data
from psychopy.hardware import keyboard
from psychopy.visual import circle
import numpy as np
from time import localtime, strftime



# ======= paremter you want to change ========
subjID = 'Yunlong Xu' # initials of the subject, to save data
expName = 'cstsizeBehav' # contrast size EEG
wantSave = False # save data or not

# ================ exp setting ==================
stimDir = [-1, 1]  # -1, left;1, right
stimRadius = [0.7, 3, 5] # radius in deg
stimContrast = [0.02, 0.99]
Contrastlist = [0.02, 0.05, 0.1, 0.2, 0.4, 0.99]
Radiuslist = [1, 1.5, 2.2, 3, 5, 8]
Contrastlinear = np.random.rand(10)
for i in Contrastlinear:
    if (i<0.02):i+0.02

speedDeg = 4  # deg/sec, shall convert to deg/frame
sf = 1 # cycle/deg

# ======= setup hardwares =======
mon = monitors.Monitor('motionmonitor')
mon.setDistance(57)  # View distance cm
mon.setSizePix([1920, 1080])
mon.setWidth(52.71)  # cm
myWin = visual.Window([800, 800], units='deg', monitor=mon, checkTiming=True)
#fps = myWin.getActualFrameRate() # sometimes this call fails...
fps=60

##keyboard settings
event.globalKeys.clear()
event.globalKeys.add(key='q', func=core.quit)  # global quit
globalClock = clock.Clock()
kb = keyboard.Keyboard()  # create kb object

# Lets do some calculation before going further
phaseStepFrame = speedDeg * sf / fps # how many cycles / frame

# define staircase handler
priorduration = 5

#  ====== define stimulus components =============
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

Wantlist_R=True
# do it !!!
#  =========== main experiment loop ========
for condition_r in Radiuslist:
  stairs = data.QuestHandler(priorduration, 0.1, pThreshold=0.82, gamma=0.01, nTrials=50, minVal=5, maxVal=1000)
  for thisDur in stairs: # loop trial handler
    # show fixation
    fixation.draw()
    myWin.flip()
    # add 1000ms delay while setting the parameters
    ISI = clock.StaticPeriod(screenHz=fps)
    ISI.start(np.random.rand())  # random (0, 1)s delay
    driftGrating.size = condition_r # set size as diameter
    driftGrating.sf = 5
    ISI.complete()  # finish the delay period

    # Show the motion stimulus and get RT and choice
    dire = np.random.choice(stimDir)
    for iFrame in range(int(thisDur)): # loop frames
        # driftGrating move one step

        driftGrating.contrast = 0.99
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
    if(choice==dire): correct =1;
    else: correct =0;
    stairs.addResponse(correct)

