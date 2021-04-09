
from psychopy import core, visual, gui, data, event
from psychopy.tools.filetools import fromFile, toFile
import numpy as np
import random

try:  # try to get a previous parameters file
    expInfo = fromFile('lastParams.pickle')
except:  # if not there then use a default set
    expInfo = {'observer':'jwp', 'refOrientation':0}
expInfo['dateStr'] = data.getDateStr()  # add the current time
# present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='simple JND Exp', fixed=['dateStr'])
if dlg.OK:
    toFile('lastParams.pickle', expInfo)  # save params to file for next time
else:
    core.quit()  # the user hit cancel so exit

# make a text file to save data
fileName = expInfo['observer'] + expInfo['dateStr']
dataFile = open(fileName+'.csv', 'w')  # a simple text file with 'comma-separated-values'
dataFile.write('targetSide,oriIncrement,correct\n')

# create the staircase handler
staircase = data.StairHandler(startVal = 20.0,
                          stepType = 'db', stepSizes=[8,4,4,2],
                          nUp=1, nDown=3,  # will home in on the 80% threshold
                          nTrials=1)


# create window and stimuli
myWin = visual.Window((600, 600), allowGUI=True,
                      monitor='testMonitor', units='deg')

grating1 = visual.GratingStim(myWin, mask="raisedCos", color=[1.0, 1.0, 1.0], opacity=1.0, size=(1.5, 1.5), sf=(7, 0),
                              ori=45)

grating2 = visual.GratingStim(myWin, mask="raisedCos", color=[1.0, 1.0, 1.0], opacity=0.5, size=(1.5, 1.5), sf=(7, 0),
                              ori=135)

# and some handy clocks to keep track of time
globalClock = core.Clock()
trialClock = core.Clock()

# display instructions and wait
message1 = visual.TextStim(win, pos=[0,+3],text='Hit a key when ready.')
message2 = visual.TextStim(win, pos=[0,-3],
    text="Then press left or right to identify the %.1f deg probe." %expInfo['refOrientation'])


t = 0
thisResp=None
while t < 20:
        t = trialClock.getTime()
        grating1.setPhase(2 * t)
        grating1.draw()  # redraw it
        grating2.setPhase(2 * t)
        grating2.draw()  # redraw it
        myWin.flip()

        while thisResp==None:
         allKeys=event.waitKeys()
         for thisKey in allKeys:
            if thisKey=='left':
                thisResp = 1  # correct
              # incorrect
            elif thisKey=='right':
                 thisResp = -1              # incorrect
            elif thisKey in ['q', 'escape']:
                core.quit()  # abort experiment
        event.clearEvents()  # clear other (eg mouse) events - they clog the buffer
        staircase.addData(thisResp)
        dataFile.write('%i\n' %(thisResp))
        core.wait(1)

# staircase has ended
dataFile.close()
staircase.saveAsPickle(fileName)  # special python binary file to save all the info

# give some output to user in the command line in the output window
print('reversals:')
print(staircase.reversalIntensities)
approxThreshold = np.average(staircase.reversalIntensities[-6:])
print('mean of final 6 reversals = %.3f' % (approxThreshold))

# give some on-screen feedback
feedback1 = visual.TextStim(
        win, pos=[0,+3],
        text='mean of final 6 reversals = %.3f' % (approxThreshold))

feedback1.draw()
myWin.flip()
event.waitKeys()  # wait for participant to respond

myWin.close()
core.quit()
