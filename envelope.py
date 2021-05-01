def envelope(time_sigma, frame_rate=120, cut_off=2, amplitude=128):
    '''
    envelope(time_sigma, frame_rate=120, cut_off=2, amplitude=128):

    Create a temporal profile and mv_length to motion stimulus in the spatial suppression task
    Arg:
        <time_sigma>: in secs, sigma of temporal envelope
        <frame_rate>: int, hz, monitor frame rate
        <cut_off>: default: 2. Whether to cut 
        <amplitude>: int, 128.

    We return the tempora modulation <profile> and an int indicating <mv_length>.

    This function is adoped from Duje Tadin. Some variables here are not clear.
    '''
    import sys
    #sys.path.append('/Users/ruyuan/Documents/Code_git/CodeRepositories')
    from numpy import arange, exp, sqrt, sum, empty, floor, ones
    from RZutilpy.stats import polyfit1d

    time_sigma = time_sigma * 1000 # convert it to millisecs
    if cut_off:
        gauss_only = 0
    else:
        gauss_only = 1

    fr = round(frame_rate/20) # this frame is determined arbitrarily
    xx = arange(fr)+1
    
    k = 0
    tt = arange(7, 25 + 0.25, 0.25)
    x1, cum1 = empty(tt.size), empty(tt.size)
    for k, time1 in enumerate(tt):
        x1[k] = time1
        time = time1/(1000/frame_rate)
        time_gauss = exp(-((xx)/(sqrt(2)*time))**2)
        cum1[k] = sum(time_gauss) * 2
    
    p, _,_ = polyfit1d(cum1, x1, 2) # we obtain a relation between underlying area and time
    area = time_sigma * frame_rate/400
    
    if cut_off > -1:
        uniform = int(floor(area - 3))
        if time_sigma > cut_off & ~gauss_only: # we provide Gaussian edges and a plateao part
            remd = area - uniform
            time = p[2]*remd**2 + p[1] * remd + p[0]
            time = time/(1000/frame_rate) # how many frame
            
            # calculate the gaussian part
            del xx
            xx = arange(fr) + 1
            time_gauss = exp(-((xx)/(sqrt(2)*time))**2)
            
            # add time_gauss to both sides of the temporal profile
            profile = ones(uniform + 2*fr)
            profile[:fr] = time_gauss[::-1]
            profile[-time_gauss.size:] = time_gauss
        
        else: # in this case, we provide a completely Gaussian profile, with no flat part
            time = time_sigma/(1000/frame_rate)
            mv_length = time*(1000/frame_rate)*6
            mv_length = round(((round(mv_length/(1000/frame_rate)))/2))*2 + 1
            xx = arange(mv_length) + 1
            xx = xx-xx.mean()
            profile = exp(-((xx)/(sqrt(2)*time))**2)
                
        # we trim the frame that are very small
        small = (amplitude * profile < .5).sum() / 2
        #import ipdb;ipdb.set_trace();import matplotlib.pyplot as plt;
        profile = profile[int(small): profile.size-int(small)]
        mv_length = profile.size

    else: # in this case, only give a flat envelope
        mv_length = round(area)
        profile = ones(mv_length)

    profile = profile*amplitude
    
    return profile, mv_length
