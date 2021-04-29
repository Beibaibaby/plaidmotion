'''
for motion EEG experiment
Behavioral measurement of visual sensitivity.
The strategy is to set stimulus to maximum size and vary five levels of contrast
We then determine the middle contrast corresponding to the average thresholds of min and max contrast

History:
    2021/04/26 RYZ create it
To do:

'''

from psychopy import core, monitors, clock, visual, event, data
from psychopy.hardware import keyboard
from psychopy.visual import circle
import numpy as np
from time import localtime, strftime

# ======= parameter you want to change ========
subjID = 'RYZ' # initials of the subject, to save data
expName = 'cstsizeBehav' # contrast size EEG 
wantSave = True # save data or not
# from egi import simple as egi

# To send markers, we can use egi package or use pylsl package
"""
from pylsl import StreamInfo, StreamOutlet
info = StreamInfo(name='my_stream_name', type='Markers', channel_count=1,
                  channel_format='int32', source_id='uniqueid12345')
# Initialize the stream.
outlet = StreamOutlet(info)
"""

# ================ exp setting ==================
stimDir = [-1, 1]  # -1, left;1, right
stimRadius = 8  # in this regime, we use maximum size
stimContrast = [0.02, 0.05, 0.1, 0.2, 0.45, 0.99]
nTrialsPerCond = 1
speedDeg = 4  # deg/sec, shall convert to deg/frame
sf = 1 # cycle/deg

# ======= setup hardwares =======
mon = monitors.Monitor('hospital6')
mon.setDistance(57)  # View distance cm
mon.setSizePix([1920, 1080])
mon.setWidth(52.71)  # cm
myWin = visual.Window([400, 400], units='deg', monitor=mon, checkTiming=True)
fps = myWin.getActualFrameRate() # sometimes this call fails...

event.globalKeys.clear()
event.globalKeys.add(key='q', func=core.quit)  # global quit
globalClock = clock.Clock()
kb = keyboard.Keyboard()  # create kb object

# let's do some calculation before going further
phaseStepFrame = speedDeg * sf / fps # how many cycles / frame
stimFrames = [round(i / myWin.monitorFramePeriod) for i in stimDur]

# define trial handler
stimList = []
for dire in stimDir:
        for c in stimContrast:
            stimList.append({'stimDir': dire, 'stimContrast':c})
trials=data.TrialHandler(trialList=stimList, nReps=nTrialsPerCond)

#  ====== define stimulus components =======
# define fixation
fixation = circle.Circle(myWin, units='deg', radius=0.15, lineColor=1, fillColor=1)
# define drift grating
driftGrating = visual.GratingStim(myWin, tex='sin', size=stimRadius*2, units='deg', mask='raisedCos', sf=sf)


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
for trial in trials: # loop trial handler
    # show fixation
    fixation.draw()
    myWin.flip()
    
    # add 1000ms delay while calculating stim
    ISI = clock.StaticPeriod(screenHz=fps)
    ISI.start(np.random.rand()+1)  # 1-2s delay
    driftGrating.contrast = trial['stimContrast'] # set contrast
    # from staircases get stimulus duration
    # trials.addData('stimDur', dur)
    # trials.addData('stimFrames', nFrame) 
    ISI.complete()  # finish the delay period

    # show the motion stimulus and get RT and choice
    for iFrame in range(nFrame): # loop frames
        # driftGrating move one step 
        driftGrating.phase = phaseStepFrame * iFrame * trial['stimDir']
        driftGrating.draw()
        myWin.flip()        
    myWin.flip()
    # collect response
    kb.clock.reset()
    kb.start()
    keys=kb.waitKeys(keyList=['left','right'], waitRelease=True)
    kb.stop()

    # save data for this trial
    trials.addData('choice', -1 if keys[0].name=='left' else 1) # we only record the 1st key
    trials.addData('correct', 1 if trials.data['choice'][trials.thisIndex]==trial['stimDir'] else 0)

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

