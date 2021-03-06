##################################################################
#            Calibration script used for CASA class              #
#                                                                #
#                                                                #
# Written by: Anh Nguyen (s6tynguy@uni-bonn.de)                  #
# Tutored by: Jackie and Benjamin                                #
#----------------------------------------------------------------#


####IMPORTANT NOTE (0 _ 0#): 
# IT'S REALLY EASY TO FORGET. In order to do the calibration, we use the measurement set '.ms' which stores the u-v data. 
# It contains 4 columns: DATA column, MODEL column, CORRECTED column, FLAGGED column
# After downloading the raw data from the ALMA webpage, remember to convert it to ms by using importasdm (import ALMA Science Data Model):
# importasdm(asdm='uid___A002_X8a5fcf_X125f', asis='Antenna Station Receiver Source CalAtmosphere CalWVR', bdfflags=True)

import os

name = 'uid___A002_X8a5fcf_X125f'    # List the excutable block (EB) to be reduced

# inspect the listobs of the EB (done in the milestone 1)
os.system('rm -rf '+name+'.ms.listobs')
listobs(vis = name+'.ms',
            listfile = name+'.ms.listobs')

#########Basic info of calibration retrieved from listobs - raw-data inspection: necessary for the calibration
# CALIBRATION-----------------------FIELD--------------------------CORRESSPONDING IDs-------------#
# WVR                         J0423-013, J0423-0120, ngc_1614     0,1,2                           #
# CALIBRATE_AMPLI             J0423-013                           1                               #
# CALIBRATE_ATMOSPHERE        J0423-013, J0423-0120, ngc_1614     0,1,2                           #
# CALIBRATE_BANDPASS          J0423-0120                          0                               #
# CALIBRATE_PHASE             J0423-0120                          0                               #
# CALIBRATE_POINTING          J0423-0120                          0                               #
# OBSERVE_TARGET              ngc_1614                            3                               #
# FLUX_CALIBRATE              J0423-013                           1                               #
#-------------------------------------------------------------------------------------------------#


# In the inspection of the configuration of the array, it is important to also determine the reference antenna for the purpose of phase calibration later on. In this data set, I chose DA63 at first but after step 1.4, I switch to PM04
plotants(vis=name+'.ms',
         figfile=name+'_plotants.png')

#______________________ The key flow of this calibration script \(^_^)/___________________________________#
### 1 ### A priori calibration   
#===== 1.1 ## A priori flagging
#===== 1.2 ## Generate WVR caltable
#===== 1.3 ## Generate Tsys caltable
#===== 1.4 ## Flagging antenna
#===== 1.5 ## Apply newly determined WVR and Tsys caltables to all fields
#===== 1.6 ## Check the results by plotms

### 2 ### Preparing the data for later on calibration
#===== 2.1 ## Split out science SpWs
#===== 2.2 ## Inspection of the ms before proceeding w/ the Calibration and do the flagging
#---------- 2.2.1 # amp vs channel
#---------- 2.2.2 # amp vs antenna
#---------- 2.2.3 # amp vs time
#---------- 2.2.4 # phase vs freq/time to check before bandpass calibration

### 3 ### BANDPASS CALIBRATION    
#===== 3.1 ## Correct for global phase variation with time
#===== 3.2 ## Inspect the inferred calibration table (caltable)
#===== 3.3 ## Derive the bandpass caltable for the 1st day
#===== 3.4 ## Derive the bandpass caltable for the 2nd day
#===== 3.5 ## Inspect the bandpass caltable

### 4 ### FLUX AND PHASE CALIBRATION  
#===== 4.1 ## Putting a model for the flux calibrator
#===== 4.2 ## Measuring phase corrections
#===== 4.3 ## Measuring amplitude corrections
#===== 4.4 ## Measuring phase corrections at the scan level 
#===== 4.5 ## Inspect the inferred caltable
#---------- 4.5.1 ## amplitude caltable
#---------- 4.5.2 ## phase caltable

### 5 ### APPLYING CALIBRATION AND PLOTTING RESULT
#===== 5.1 ## apply the bandpass, phase and flux caltables to all fields
#===== 5.2 ## Inspect the effect of uvdist, time and freq on phase/amp
#---------- 5.2.1 # Inspect the effect of uvdist
#---------- 5.2.2 # Inspect the effect of time
#---------- 5.2.3 # Inspect the effect of frequency
#===== 5.3 ## Image the phase calibrator
#__________________________________________________________________________________________________________#


### 1 ###     A priori calibration         ####
#===== 1.1 ## A priori flagging: results of flagging is written to measurement set
flagdata(vis = name+'.ms',
         mode = 'manual',
         spw = '1~24', # all SpWs but that of the WVR (spw=0)
         autocorr = T,
         flagbackup = F)         

flagdata(vis = name+'.ms',
         mode = 'manual',
         intent = '*POINTING*,*ATMOSPHERE*',  # all scan with intent containing *POINTING* or *ATMOSPHERE* , which excludes spw [1, 3, 5, 7, 11, 13, 15] in the caltable. In this observation, *ATMOSPHERE* and *SIDEBAND_RATIO* were done by spws [9~16]. Therefore using *ATMOSPHERE* suffices in this case ?! -------> Now I'm not sure if this explanation is right ...
         flagbackup = F)
 
flagdata(vis=name+'.ms',
         flagbackup = F,
         mode = 'shadow')  # Flag data of shadowed antennas. This mode is not available for caltable. How to unflag to see what happen before and after the flagging? .... :| 

flagdata(vis=name+'.ms',
         flagbackup = F,
         mode = 'shadow') 

# Fun to unflag and see how it looks like
 flagdata(vis = name+'.ms',
         mode = 'unflag',
         intent = '*POINTING*,*ATMOSPHERE*', # all scan with intent containing *POINTING* or *ATMOSPHERE* , which excludes spw [1, 3, 5, 7, 11, 13, 15] in the caltable. In this observation, *ATMOSPHERE* and *SIDEBAND_RATIO* were done by spws [9~16]. Therefore using *ATMOSPHERE* suffices in this case
         flagbackup = F)
flagdata(vis = name+'.ms',
         mode = 'unflag',
         spw = '1~24', # all SpWs but that of the WVR (spw=0)
         autocorr = T,
         flagbackup = F)         

#===== 1.2 ## Generate WVR caltable: Generation and time averaging of the WVR caltable
os.system('rm -rf '+name+'.ms.wvr')   # remove any previous existed file
wvrgcal(vis = name+'.ms',
        caltable = name+'.ms.wvr',    # name of the CALTABLE output 
        spw = [9,11,13,15,17,19,21,23],       # list of the spws for which solutions should be saved into the caltalbe  
        smooth = '6.05s',            # smoothed over the integration time of the science visibilities from the listobs
        toffset = 0,
        segsource = True,
        tie = ['0','1','2'], # Try to find the best solutions for all fields
        refant=['PM04'],              # Choose ref antenna which is PM04 for this data set
        statsource = '3')      # Science target source: ngc_1614

#===== 1.3 ## Generate Tsys caltable
os.system('rm -rf '+name+'.ms.tsys') # remove any previous existed file
gencal(vis = name+'.ms',
       caltable = name+'.ms.tsyscal', # name of the CALTABLE output by gencal
       caltype = 'tsys') # Tell gencal that we want to do a Tsys calibration

#===== 1.4 ## Flagging antenna
# Flagging of the channels at the edge of the SpWs used in sideband ratio calibration which is the group [9~16]
# In this step, all data of antenna 14 is flagged       
flagdata(vis = name+'.ms.tsyscal',
         mode = 'manual',
         spw = '9:0~3;124~127, 11:0~3;124~127, 13:0~3;124~127, 15:0~3;124~127',   # Edges of the Tsys SpW to be flagged
         flagbackup = F)

# When I didn't flag these edges, later plotbandpass cannot plot anything
#flagdata(vis = name+'.ms.tsyscal',
#         mode = 'unflag',
#         spw = '9:0~3;124~127, 11:0~3;124~127, 13:0~3;124~127, 15:0~3;124~127',   # Edges of the Tsys SpW to be flagged
#         flagbackup = F)

# Inspect the Tsys caltable: look at the amplitude (K) vs freq. for different time/antenna, searching for peculiar signatures 
# overlay ='time'
os.system('mkdir '+name+'.ms.tsyscal.bandpassplot') # create new directory for bandpass plots
os.system('rm -rf '+name+'.ms.tsyscal.bandpassplot') # remove any previous existed file
for spw in ['9', '11', '13', '15']: #loop over the "Tsys" SpWs
    plotbandpass(caltable=name+'.ms.tsyscal', xaxis='freq', yaxis='amp',
                 spw=spw, overlay='time', # all scans are plotted together, one plot per antenna
                 plotrange=[0, 0, 0, 180],  # [x0,x1,y0,y1]; x0=x1 -> automatic range determination by CASA
                 figfile=name+'.ms.tsyscal.bandpassplot/cal-tsys_per_spw_'+spw+'_overlaytime_'+name+'.png', interactive=False) 

# overlay = 'antenna'
for spw in ['9', '11', '13', '15']: #loop over the "Tsys" SpWs
    plotbandpass(caltable=name+'.ms.tsyscal', xaxis='freq', yaxis='amp',
                 spw=spw, overlay='antenna', # all scans are plotted together, one plot per antenna
                 plotrange=[0, 0, 0, 180],  # [x0,x1,y0,y1]; x0=x1 -> automatic range determined by CASA
                 figfile=name+'.ms.tsyscal.bandpassplot/cal-tsys_per_spw_'+spw+'_overlayant_'+name+'.png', interactive=False) 

## There are problems with the Tsys of DA50 (7). There might be problems w/ DA41 (0) and DA46 (4) DV11 (21). 
# Note: If there is any problem you have found in antenna, the solution is that you flag the whole antenna in order not to let any bad data into your CALTABLE (calibration table)
# Flagging antenna 07
flagdata(vis=name+'.ms',
         mode='manual',
         antenna='7',
         flagbackup = T)

flagdata(vis=name+'.ms.tsyscal',
         mode='manual',
         antenna='7',
         flagbackup = T)

# Since I got a message that all data from antenna 14 which is DA63 is flagged, to understand what really happened, I unflagged it or for fun if you don't really care the message (_ _#)
#os.system('mkdir '+name+'.ms.tsyscal.notfun') # create new directory for 'not fun' plots
#flagdata(vis=name+'.ms.tsyscal',
#         mode='unflag',
#         antenna='14',
#         flagbackup = T)
#flagdata(vis=name+'.ms',
#         mode='unflag',
#         antenna='14',
#         flagbackup = T)

# and replot 
#for spw in ['9', '11', '13', '15']: #loop over the "Tsys" SpWs
#    plotbandpass(caltable=name+'.ms.tsyscal', xaxis='freq', yaxis='amp',
#                 spw=spw, overlay='antenna', # all scans are plotted together, one plot per antenna
#                 plotrange=[0, 0, 0, 180],  # [x0,x1,y0,y1]; x0=x1 -> automatic range determined by CASA
#                 figfile=name+'.ms.tsyscal.notfun/cal-tsys_per_spw_'+spw+'_overlayant_'+name+'_afterflagging.png', interactive=False) 


# Check after flagging
os.system('mkdir '+name+'.ms.tsyscal.afterflagging1') # create new directory for afterflagged plots
os.system('rm -rf '+name+'.ms.tsyscal.afterflagging1/*png') # create new directory for afterflagged plots

plotbandpass(caltable=name+'.ms.tsyscal', xaxis='freq', yaxis='amp',
                 spw=spw, overlay='antenna', # all scans are plotted together, one plot per antenna
                 plotrange=[0, 0, 0, 180],  # [x0,x1,y0,y1]; x0=x1 -> automatic range determined by CASA
                 figfile=name+'.ms.tsyscal.afterflagging1/cal-tsys_per_spw_'+spw+'_overlayant_'+name+'_afterflagging.png', interactive=False) 
plotbandpass(caltable=name+'.ms.tsyscal', xaxis='freq', yaxis='amp',
                 spw=spw, overlay='time',
                 plotrange=[0, 0, 0, 180],  # [x0,x1,y0,y1]; x0=x1 -> automatic range determined by CASA
                 figfile=name+'.ms.tsyscal.afterflagging1/cal-tsys_per_spw_'+spw+'_overlayant_'+name+'_afterflagging.png', interactive=False) 

# After checking the plot of all antenna over time. There is problem w/ antenna 21 
# Inspect again 0,4,21
plotbandpass(caltable=name+'.ms.tsyscal', xaxis='freq', yaxis='amp',
             spw=spw,
             overlay='time',
             antenna='0,4,21', # all scans are plotted together, one plot per antenna
             plotrange=[0, 0, 0, 180],  # [x0,x1,y0,y1]; x0=x1 -> automatic range determined by CASA
             figfile=name+'.ms.tsyscal.bandpassplot/cal-tsys_per_spw_'+spw+'_overlaytimeant0421_'+name+'.png', interactive=False) 

# There is problem w/ 21 at time= 12:32:25 field 0
flagdata(vis=name+'.ms',
         mode='manual',
         antenna='21',
         field='0',
         timerange='2014/08/30/12:32:24.5~12:32:25.5',
         flagbackup = T)

flagdata(vis=name+'.ms.tsyscal',
         mode='manual',
         antenna='21',
         field='0',
         timerange='2014/08/30/12:32:24.5~12:32:25.5',
         flagbackup = T)


# Check after flagging
os.system('mkdir '+name+'.ms.tsyscal.afterflagging2') # create new directory for afterflagged plots
os.system('rm -rf '+name+'.ms.tsyscal.afterflagging2/*png') 

plotbandpass(caltable=name+'.ms.tsyscal', xaxis='freq', yaxis='amp',
                 spw=spw, overlay='antenna', # all scans are plotted together, one plot per antenna
                 plotrange=[0, 0, 0, 180],  # [x0,x1,y0,y1]; x0=x1 -> automatic range determined by CASA
                 figfile=name+'.ms.tsyscal.afterflagging2/cal-tsys_per_spw_'+spw+'_overlayant_'+name+'_afterflagging.png', interactive=False) 
plotbandpass(caltable=name+'.ms.tsyscal', xaxis='freq', yaxis='amp',
                 spw=spw, overlay='time',
                 plotrange=[0, 0, 0, 180],  # [x0,x1,y0,y1]; x0=x1 -> automatic range determined by CASA
                 figfile=name+'.ms.tsyscal.afterflagging2/cal-tsys_per_spw_'+spw+'_overlayant_'+name+'_afterflagging.png', interactive=False) 

#===== 1.5 ## Apply newly determined WVR and Tsys caltables to all fields
##### J0423-0120 (0), J0423-013 (2), ngc_1614 (3)
# applycal reads the specificed gain calibration tables, applies them to the raw data column (with the specified selection), writes the calibrated results into the corrected column. It will overwrite existing corrected data (if existed)
from recipes.almahelpers import tsysspwmap
tsysmap = tsysspwmap(vis = name+'.ms', tsystable = name+'.ms.tsyscal', tsysChanTol = 1)

# Field 0
        applycal(vis=name+'.ms',
             field = '0', # field to which we want to apply the corrections field
             spw= '17, 19, 21, 23', # SpWs to which we want the corrections to be applied, exclude 1, 3, 5, 7, 11, 13, 15 due to the priori flagging
             gaintable = [name+'.ms.tsyscal', name+'.ms.wvr'], # Gain calibration tables to apply on the fly
             gainfield=['0',''],  # select a subset of calibrators from gaintable. Here I apply the Tsys from field to itself
             interp='linear,linear', # 'Time-interpolation, Frequency-interpolation'
             calwt = T, # applying the weights estimated from the Tsys measurements
             flagbackup=F, # backup the state of the flags before applying calibration. Default is True but we don't need its backup here. why?
             spwmap = [tsysmap,[]])  # tsysmap = [0,17,17,19,19,21,21,23,23] -> we apply Tsys SpW-0 solutions to SpW-0; apply Tsys SpW-17 solutions to SpW-1, apply Tsys SpW-19 solutions to SpW-2, etc. ; for the WVR we use all fields

# Field 1
        applycal(vis=name+'.ms',
             field = '1', # field to which we want to apply the corrections field
             spw= '17, 19, 21, 23', # SpWs to which we want the corrections to be applied, exclude 1, 3, 5, 7, 11, 13, 15 due to the priori flagging
             gaintable = [name+'.ms.tsyscal', name+'.ms.wvr'], # Gain calibration tables to apply on the fly
             gainfield=['1',''],  # select a subset of calibrators from gaintable. Here I apply the Tsys from field to itself
             interp='linear,linear', # 'Time-interpolation, Frequency-interpolation'
             calwt = T, # applying the weights estimated from the Tsys measurements
             flagbackup=F,
             spwmap = [tsysmap,[]])  # tsysmap = [0,17,17,19,19,21,21,23,23] -> we apply Tsys SpW-0 solutions to SpW-0; apply Tsys SpW-17 solutions to SpW-1, apply Tsys SpW-19 solutions to SpW-2, etc.


# Field 3
        applycal(vis=name+'.ms',
             field = '3', # field to which we want to apply the corrections field
             spw= '17, 19, 21, 23', # SpWs to which we want the corrections to be applied, exclude 1, 3, 5, 7, 11, 13, 15 due to the priori flagging
             gaintable = [name+'.ms.tsyscal', name+'.ms.wvr'], # Gain calibration tables to apply on the fly
             gainfield=['2',''],  # select a subset of calibrators from gaintable. Here I apply the Tsys of field 2 to our target source
             interp='linear,linear', # 'Time-interpolation, Frequency-interpolation'
             calwt = T, # applying the weights estimated from the Tsys measurements
             flagbackup=F,
             spwmap = [tsysmap,[]])  # tsysmap = [0,17,17,19,19,21,21,23,23] -> we apply Tsys SpW-0 solutions to SpW-0; apply Tsys SpW-17 solutions to SpW-1, apply Tsys SpW-19 solutions to SpW-2, etc.   

#===== 1.6 ## Check the results by plotms
# look at the difference between the DATA and CORRECTED columns
# Investigate how WVR correction affects on our visibilities
os.system('mkdir '+name+'.ms.wvrcorrection_compared') 
os.system('rm -rf '+name+'.ms.wvrcorrection_compared/'+name+'_phasevstime_rawdata.png') 
plotms(vis=name+'.ms',
       xaxis='time', 
       yaxis='phase',
       ydatacolumn='data',
       spw='17:4~1915', 
       antenna='', 
       correlation='XX', 
       avgchannel='1912',
       coloraxis='baseline', 
       avgscan=T, 
       selectdata=T, # allow to select data parameters flag
       field='0,1,3',
       title='The phase from DATA column vs time',
       overwrite=T, # overwrite plotfile if it already exists
       highres=T, # create plot w/ higher resolution
       plotfile=name+'.ms.wvrcorrection_compared/'+name+'_phasevstime_rawdata.png',
       expformat='png')

plotms(vis=name+'.ms',
       xaxis='time', 
       yaxis='phase',
       ydatacolumn='corrected',
       spw='17:4~1915', 
       antenna='', 
       correlation='XX', 
       avgchannel='1912',
       coloraxis='baseline', 
       avgscan=T, 
       selectdata=T, # allow to select data parameters flag
       field='0,1,3',
       title='The phase from CORRECTED column vs time',
       overwrite=T, # overwrite plotfile if it already exists
       highres=T, # create plot w/ higher resolution
       plotfile=name+'.ms.wvrcorrection_compared/'+name+'_phasevstime_correcteddata.png',
       expformat='png')

# Investigate how Tsys correction affects on our visibilities
os.system('rm -rf '+name+'.ms.wvrcorrection_compared/'+name+'_ampvstime_rawdata.png') 
os.system('rm -rf '+name+'.ms.wvrcorrection_compared/'+name+'_ampvstime_correcteddata.png') 
plotms(vis=name+'.ms',
       xaxis='time', 
       yaxis='amp',
       ydatacolumn='data',
       spw='17:4~1915', 
       antenna='', 
       correlation='XX', 
       avgchannel='1912',
       coloraxis='baseline', 
       avgscan=T, 
       selectdata=T, # allow to select data parameters flag
       field='0,1,3',
       title='The amplitude from DATA column vs time',
       overwrite=T, # overwrite plotfile if it already exists
       highres=T, # create plot w/ higher resolution
       plotfile=name+'.ms.wvrcorrection_compared/'+name+'_ampvstime_rawdata.png',
       expformat='png')

plotms(vis=name+'.ms',
       xaxis='time', 
       yaxis='amp',
       ydatacolumn='corrected',
       spw='17:4~1915', 
       antenna='', 
       correlation='XX', 
       avgchannel='1912',
       coloraxis='baseline', 
       avgscan=T, 
       selectdata=T, # allow to select data parameters flag
       field='0,1,3',
       title='The amplitude from CORRECTED column vs time',
       overwrite=T, # overwrite plotfile if it already exists
       highres=T, # create plot w/ higher resolution
       plotfile=name+'.ms.wvrcorrection_compared/'+name+'_ampvstime_correcteddata.png',
       expformat='png')

# From here, also can see the problem during scan 4,6,7,10. In order to continute, I need to sort out the ms by split scientific spw 
##===== END 1: A PRIORI CALIBRATION =====## 


### 2 ### Preparing the data for later on calibration
#===== 2.1 ## Split out science SpWs
# easier to manage and deal with the scientific data. We get rid of all unncessary SpWs and keep only the corrected column using split
os.system('rm -rf '+name+'.ms.split')
os.system('rm -rf '+name+'.ms.split.flagversions')

split(vis = name+'.ms',
          outputvis = name+'.ms.split', # name of the new measurement
          datacolumn = 'corrected',    # name of the column to split out; WARNING: it will be put in the DATA column of the new MS
          spw = '17,19,21,23', # Name of the SpWs splitted out which are science SpWs. 
          keepflags = T)

# Listobs and save original flags using flagmanager
os.system('rm -rf '+name+'.ms.split.listobs')
listobs(vis = name+'.ms.split',
            listfile = name+'.ms.split.listobs')

if not os.path.exists(name+'.ms.split.flagversions/Original.flags'):   
        flagmanager(vis = name+'.ms.split',                # save the flag table to a separate table for backup      
                    mode = 'save',
                    versionname = 'Original')    # under the name "Original"

### NOTE: Now the ID of the science SPWs is changed from 17, 19, 21, 23 to 0,1,2,3 

###### 2.2 ## Inspection of the ms before proceeding w/ the Calibration and do the flagging
#---------- 2.2.1 # Inspect amp vs channel and do the flagging
plotms(vis=name+'.ms.split',
       xaxis='channel', 
       yaxis='amp',
       averagedata=T, # averaging all data
       avgbaseline=T, # averaging all baslines
       avgscan=T,
       avgtime='1e8',
       coloraxis='field', # colorising each datapoint according to their 'field': 0,1,2,3
       highres=T, # create plot w/ higher resolution
       title='The inspection of splitted ms',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'.ms.split_ampvschannel.png',
       expformat='png') 

# Edges of all SpWs are corrupted (as expected) ------> flagged
flagdata(vis=name+'.ms.split',
         spw='*:0~15;1904~1919', # Alternative syntax: spw = '0:0~10;1909~1919, 1:0~10;1909~1919, 2:0~10;1909~1919, 3:0~10;1909~1919',
         flagbackup = T)

# There is a fluctuation of amp vs channel during the scan 4 (field 0) and scan 6 (field 1) (which are 17 and 23 initially T_T)
# which group of antenna should I rely on?
# Therefore I inspect further by using plotms for scan 4,6 and avg all antenna

# Before doing that, I try ploting for field 0,1 to get a general view
# Field 0
plotms(vis=name+'.ms.split',
       xaxis='channel', 
       yaxis='amp',
       averagedata=T, # averaging all data
       avgantenna=T, # averaging all antenna
       avgscan=T,
       avgtime='1e8',
       field='0',
       highres=T, # create plot w/ higher resolution
       title='The inspection of field 0',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'.ms.split_ampvschannelfield0.png',
       expformat='png') 

# For field 1
plotms(vis=name+'.ms.split',
       xaxis='channel', 
       yaxis='amp',
       averagedata=T, # averaging all data
       avgantenna=T, # averaging all antenna
       avgscan=T,
       avgtime='1e8',
       field='1',
       highres=T, # create plot w/ higher resolution
       title='The inspection of field 1',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'.ms.split_ampvschannelfield1.png',
       expformat='png') 

# Does not visually see any peculiar signatures on field 0 and 1

#---------- 2.2.2 # Inspect the amp vs antenna 
# scan 4
plotms(vis=name+'.ms.split',
       xaxis='antenna1', 
       yaxis='amp',
       averagedata=T, # averaging all data
       avgantenna=T, # averaging all antenna
       avgscan=T,
       avgtime='1e8',
       scan='4',
       highres=T,
       title='The inspection of scan 4',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'.ms.split_ampvsantennascan4.png',
       expformat='png')

# scan 6
plotms(vis=name+'.ms.split',
       xaxis='antenna1', 
       yaxis='amp',
       averagedata=T, # averaging all data
       avgantenna=T, # averaging all antenna
       avgscan=T,
       avgtime='1e8',
       scan='6',
       highres=T,
       title='The inspection of scan 6',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'.ms.split_ampvsantennascan6.png',
       expformat='png')

# scan 7
plotms(vis=name+'.ms.split',
       xaxis='antenna1', 
       yaxis='amp',
       averagedata=T, # averaging all data
       avgantenna=T, # averaging all antenna
       avgscan=T,
       avgtime='1e8',
       scan='7',
       highres=T,
       title='The inspection of scan 7',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'.ms.split_ampvsantennascan7.png',
       expformat='png')

# scan 10
plotms(vis=name+'.ms.split',
       xaxis='antenna1', 
       yaxis='amp',
       averagedata=T, # averaging all data
       avgantenna=T, # averaging all antenna
       avgscan=T,
       avgtime='1e8',
       scan='10',
       highres=T,
       title='The inspection of scan 10',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'.ms.split_ampvsantennascan10.png',
       expformat='png')

# Problems come mostly from scan 4, 7 and 10 (field 0)

#---------- 2.2.3 # Inspect the amp vs time and do the flagging
# First plot amp vs time for field 0
plotms(vis=name+'.ms.split',
       xaxis='time', 
       yaxis='amp',
       spw='0:4~1915',
       antenna='',
       correlation='XX', 
       avgchannel='1912',
       coloraxis='antenna1', # colorising each datapoint according to their 'field': 0,1,2,3
       selectdata=T, # allow to select data parameters flag
       field='0',
       highres=T,
       title='The inspection of field 0',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'.ms.split_ampvstimefield0.png',
       expformat='png')

# inspect field 0 over all scan 4, 7,10 and do flagging
plotms(vis=name+'.ms.split',
       xaxis='time', 
       yaxis='amp',
       spw='0:4~1915',
       antenna='',
       correlation='XX', 
       avgchannel='1912',
       coloraxis='scan', 
       selectdata=T, # allow to select data parameters flag
       field='0',
       scan='4,7,10',
       highres=T,
       title='The inspection of field 0 with color-coded scan',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'.ms.split_ampvstimefield0_scan4710.png',
       expformat='png')

# Done flagging interactively this time T_T

# Scan 4
plotms(vis=name+'.ms.split',
       xaxis='spw', 
       yaxis='amp',
       spw='*:4~1915',
       antenna='',
       correlation='XX', 
       avgchannel='1912',
       coloraxis='antenna1',
       selectdata=T, # allow to select data parameters flag
       scan='4',
       highres=T,
       title='The inspection of scan 4 after flagging',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'.ms.split_ampvsspwscan4_afterflagging.png',
       expformat='png')

# Scan 7
plotms(vis=name+'.ms.split',
       xaxis='spw', 
       yaxis='amp',
       spw='*:4~1915',
       antenna='',
       correlation='XX', 
       avgchannel='1912',
       coloraxis='antenna1',
       selectdata=T, # allow to select data parameters flag
       scan='7',
       highres=T,
       title='The inspection of scan 7 after flagging',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'.ms.split_ampvsspwscan7_afterflagging.png',
       expformat='png')

# Scan 10
plotms(vis=name+'.ms.split',
       xaxis='spw', 
       yaxis='amp',
       spw='*:4~1915',
       antenna='',
       correlation='XX', 
       avgchannel='1912',
       coloraxis='antenna1',
       selectdata=T, # allow to select data parameters flag
       scan='10',
       highres=T,
       title='The inspection of scan 10 after flagging',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'.ms.split_ampvsspwscan10_afterflagging.png',
       expformat='png')

# Done flagging for scan 10 interactively, problem from spw1 of scan 10

# Check field 0 again over scan 4,7,10 after all flagging
plotms(vis=name+'.ms.split',
       xaxis='time', 
       yaxis='amp',
       spw='0:4~1915',
       antenna='',
       correlation='XX', 
       avgchannel='1912',
       coloraxis='scan', 
       selectdata=T, # allow to select data parameters flag
       field='0',
       scan='4,7,10',
       highres=T,
       title='The inspection of field 0 with color-coded scan after flagging',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'.ms.split_ampvstimefield0_scan4710_afterflagging.png',
       expformat='png')

# After getting the error message from 'bandpass', do this flagging
flagdata(vis = name+'.ms.split',
         flagbackup = T,
         mode = 'manual',
         correlation='XX', 
         timerange='2014/08/30/12:37:19.1',
         field='0', 
         spw='0:0~15;1904~1919')

flagdata(vis = name+'.ms.split',
         flagbackup = T,
         mode = 'manual',
         correlation='XX', 
         timerange='2014/08/30/12:37:28.7',
         field='0', 
         spw='1:0~15;1904~1919')

flagdata(vis = name+'.ms.split',
         flagbackup = T,
         mode = 'manual',
         correlation='XX', 
         timerange='2014/08/30/12:37:27.1',
         field='0',
         spw='2:0~15;1904~1919')

flagdata(vis = name+'.ms.split',
         flagbackup = T,
         mode = 'manual',
         correlation='XX', 
         timerange='2014/08/30/12:37:25.6',
         field='0',
         spw='3:0~15;1904~1919')

flagdata(vis = name+'.ms.split',
         flagbackup = T,
         mode = 'manual',
         antenna='0,4')

#---------- 2.2.4 # Inspect phase and amp vs freq to check before bandpass calibration
plotms(vis=name+'.ms.split',
       xaxis='freq', 
       yaxis='phase',
       selectdata=T,
       field='0', # fields used for bandpass calibration
       antenna='',
       avgtime='1e8',
       avgscan=T,
       coloraxis='baseline', # colorising each datapoint according to their 'baseline': 0,...,594
       highres=T, # create plot w/ higher resolution
       iteraxis='antenna',
       title='The inspection of phase vs freq before bandpass calibration',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'_phasevsfreq.png',
       expformat='png') 

plotms(vis=name+'.ms.split',
       xaxis='time', 
       yaxis='phase',
       selectdata=T,
       field='0', # fields used for bandpass calibration
       antenna='',
       avgscan=T,
       coloraxis='baseline', # colorising each datapoint according to their 'baseline': 0,...,594
       highres=T, # create plot w/ higher resolution
       iteraxis='antenna',
       title='The inspection of phase vs time before bandpass calibration',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'_phasevstime.png',
       expformat='png') 

# Additional flaggings for scan 4,10
# cannot do this this time, check later
flagdata(vis=name+'.ms.split', 
         flagbackup=T, 
         mode='manual', 
         scan='4',
         timerange='2011/08/30/12:38:03') 
flagdata(vis=name+'.ms.split', 
         flagbackup=T, 
         mode='manual', 
         scan='4',
         spw='0,1,2,3', 
         correlation='XX', 
         timerange='2011/08/30/12:35:12') 
flagdata(vis=name+'.ms.split', 
         flagbackup=T, 
         mode='manual', 
         scan='10',
         spw='0,1,2,3', 
         correlation='XX', 
         timerange='2011/08/30/12:49:44') 
flagdata(vis=name+'.ms.split', 
         flagbackup=T, 
         mode='manual', 
         scan='10',
         spw='0,1', 
         correlation='XX', 
         timerange='2011/08/30/12:49:56') 
flagdata(vis=name+'.ms.split', 
         flagbackup=T, 
         mode='manual', 
         scan='10',
         spw='0,1,2,3', 
         correlation='XX', 
         timerange='2011/08/30/12:49:32.6880') 

##===== END 2: PREPRATION BEFORE THE CALIBRATION =====## 

### 3 ###    BANDPASS CALIBRATION     ###
#===== 3.1 ## Correct for global (i.e., frequency-independent) phase variation with time
# In order to combine all bandpass scans together for the upcoming bandpass calibration 
os.system('rm -rf ngc1614.ms.split.ap_pre_bandpass')
gaincal(vis = name+'.ms.split', 
        caltable = 'ngc1614.ms.split.ap_pre_bandpass', 
        field ='0', # Field used for bandpass calibration
        spw = '*:20~1020', # Improve the S/N by combining several channels of spws: 0,1,2,3; 
        solint = 'int', # Correction inferred for each integration (many integration per scan)
        refant = 'PM04', # reference antenna selected to be at the center of the array and well-behaved (i.e no jumps)
        calmode = 'p') # Phase calibration

###### 3.2 ## Inspect the inferred calibration table
plotcal(caltable = 'ngc1614.ms.split.ap_pre_bandpass', 
        xaxis = 'time', 
        yaxis = 'phase', 
        poln ='X', # only inspect the XX polarisation for figure readability
        plotsymbol = 'o', 
        plotrange = [0,0,-180,180], 
        iteration = 'spw', # show each SpW separately 
        figfile = 'cal-phasevstime_XX.ap_pre_bandpass.png', # output file
        subplot = 221) 

###### 3.3 ## We derive the bandpass caltable
# while applying on-the-fly (gaintable='my_caltable')
# the time-dependent phase variation corrections stored in ...? 
os.system('rm -rf ngc1614.ms.split.bandpass')
bandpass(vis = name+'.ms.split',
         caltable = 'ngc1614.ms.split.bandpass', # output bandpass caltable
         field = '0',  
         solint = 'inf', # Solution interval in time, with combine='scan,obs', sets the solution interval to the entire observation.  
         combine = 'scan,obs',  
         refant = 'PM04',
         fillgaps=16, # Fill flagged solution channels by interpolation
         minblperant=7,          # Antennas with fewer baaselines are excluded from solutions. Amplitude solutions with fewer than 4 baselines, and phase solutions with fewer than 3 baselines are only trivially constrained, and are no better than baseline-based solutions. 
         minsnr=3,               # Reject solutions below this SNR. Only applies for bandtype B
         solnorm = True,         # Normalize the bandpass amplitudes and phases of the corrections to unity; we don’t know the real flux
         bandtype = 'B',         # Type of bandpass solution which are B or BPOLY. Here we chose B hence the solution will be time-independent (B solutions can be determined at any specified time interval)
         gaintable = 'ngc1614.ms.split.ap_pre_bandpass')   # Gain calibration table to apply


## Got the error message: Insufficient unflagged antennas to proceed with this solve. Try flagging as suggested but didn't work :((

###### 3.4 ## Inspect the bandpass calibration table
plotbandpass(caltable = 'ngc1614.ms.split.bandpass',
             xaxis='freq',
             yaxis='phase',
             plotrange = [0,0,-70,70],
             overlay='antenna',
             solutionTimeThresholdSeconds=11,
             interactive=False,
             figfile='ngc1614.ms.split.bandpass.phase.png')

os.system('mkdir '+name+'.ms.split.bandpasscal')
os.system('rm '+name+'.ms.split.bandpasscal/ngc1614.ms.split.bandpass.phase.png')

for antenna in ['0','1', '2', '3','4','5','6','8','9','10','11','12','13','15','16','17','18','19','20','22','23','24','25','26','27','28','29','30','31','32','33','34']:
plotbandpass(caltable = 'ngc1614.ms.split.bandpass',
             xaxis='freq',
             yaxis='phase',
             antenna=antenna,
             plotrange = [0,0,-70,70],
             solutionTimeThresholdSeconds=11,
             interactive=False,
             figfile=name+'.ms.split.bandpasscal/ngc1614.ms.split.bandpass.phase.png')

# If you see any jumps w/ phase, you need to calibrate them out. The problems from phase vs freq come from the WVR calibration in the first step- a priori flagging. Therefore instead of flagging on the .ms.split, I might have to come back to flag antenna 0,4 on ms and on ms.tsyscal. Will try later after obtainning the image to see how it looks like first

os.system('rm '+name+'.ms.split.bandpasscal/ngc1614.ms.split.bandpass.amp.png')
for antenna in ['0','1', '2', '3','4','5','6','8','9','10','11','12','13','15','16','17','18','19','20','22','23','24','25','26','27','28','29','30','31','32','33','34']:
plotbandpass(caltable = 'ngc1614.ms.split.bandpass',
             xaxis='freq',
             yaxis='amp',
             antenna=antenna,
             plotrange = [0,0,-70,70],
             solutionTimeThresholdSeconds=11,
             interactive=False,
             figfile=name+'.ms.split.bandpasscal/ngc1614.ms.split.bandpass.amp.png')

plotbandpass(caltable = 'ngc1614.ms.split.bandpass', 
             xaxis='freq', 
             yaxis='amp', 
             overlay='antenna', 
             solutionTimeThresholdSeconds=11118, 
             interactive=False, 
             figfile=name+'.ms.split.bandpasscal/bandpass.amplitude.png') 

# END step 3 - BANDPASS CALIBRATION -----------------------------#


### 4 ###    FLUX AND PHASE CALIBRATION     ###
#===== 4.1 ## Putting a model for the flux calibrator
setjy(vis = name+'.ms.split',
      field = '1', 
      fluxdensity=[1.24,0,0,0], # fluxdensity=[I,Q,U,V],  # In the scope of this assignment, Q,U,V - polarization parameters are set to 0
      spix=-3.35, # Spectral index for I flux density (a float or a list of float values):  where S = fluxdensity * (freq/reffreq)**(spix[0]+spix[1]*log(freq/reffreq)+..) 
      reffreq='100GHz',
      spw = '0,1,2,3',
      standard = 'manual')

# If the flux density is being scaled by spectral index, then reffreq must be set to whatever reference frequency is correct for the given fluxdensity and spix.  It cannot be determined from vis.  On the other hand, if spix is 0, then any positive frequency can be used (and ignored).
# Therefore I chose the rest freq of CO transion 1--0 (115.27GHz) to be the reference frequency


#===== 4.2 ## Measuring phase corrections ---> to measure the upcoming amp corrections
os.system('rm -rf ngc1614.ms.split.phaseint')  
gaincal(vis = name+'.ms.split',
        caltable = 'ngc1614.ms.split.phaseint',  # output phase caltable
        field = '0,1', # amp,flux calibrator is field 1, phase calibrator is field 0
        solint = 'int', # Caltable inferred for each integration to correct for fast phase variations 
        refant = 'PM04', # reference antenna
        gaintype = 'G', # Determine gains for each polarization and SpW
        calmode = 'p', # Phase corrections
        minsnr=3.0, # reject solution below this SNR
        gaintable = 'ngc1614.ms.split.bandpass') # We apply on-the-fly our previously inferred Bandpass caltable

#===== 4.3 ## Measuring amplitude corrections
os.system('rm -rf ngc1614.ms.split.ampinf') 
gaincal(vis = name+'.ms.split',
        caltable = 'ngc1614.ms.split.ampinf',  # output amp caltable
        field = '0,1', # amp,flux calibrator is field 1, phase calibrator is field 0
        solint = 'inf', # Caltable inferred for each scan
        refant = 'PM04', # Reference antenna
        gaintype = 'T', # Obtains one solution for both polarizations
        calmode = 'a', # Amplitude corrections
        minsnr=3.0, # reject solution below this SNR
        gaintable = ['ngc1614.ms.split.bandpass', 'ngc1614.ms.split.phaseint']) # We apply on-the-fly our previously inferred Bandpass and Phase caltables

#===== 4.4 ## Measuring phase corrections at the scan level
# Transferring the flux scale from field 1 to the other calibrators which have so far unknown fluxes
fluxscale(vis = name+'.ms.split',
          caltable = 'ngc1614.ms.split.ampinf', # Name of input calibration table
          fluxtable = 'ngc1614.ms.split.fluxinfscaled', # Name of output, flux-scaled calibration table
          reference = '1') 
  
# Measuring phase corrections at the scan level
os.system('rm -rf ngc1614.ms.split.phaseinf') 
gaincal(vis = name+'.ms.split',
        caltable = 'ngc1614.ms.split.phaseinf',
        field = '0,1', # amp,flux calibrator is field 1, phase calibrator is field 0
        solint = 'inf', # Solution interval: Corrections measured for each scan 
        refant = 'PM04', # Reference antenna
        gaintype = 'G', # Determine gains for each polarization and SpW
        calmode = 'p', # Phase corrections
        minsnr=3.0,
        gaintable = 'ngc1614.ms.split.bandpass') # We apply on-the-fly our previously inferred Bandpass caltable
  
#===== 4.5 ## Inspect the inferred caltable
os.system('mkdir '+name+'ms.split.inferredcaltable')
os.system('rm -rf cal-amp_vs_time.png') 
#---------- 4.5.1 ## amplitude caltable
plotcal(caltable = 'ngc1614.ms.split.ampinf', 
        xaxis = 'time', 
        yaxis = 'amp',
        plotsymbol='o', 
        plotrange = [], 
        iteration = 'spw',
        figfile=name+'ms.split.inferredcaltable/cal-amp_vs_time.png',
        subplot = 221)

#---------- 4.5.2 ## phase caltable
plotcal(caltable = 'ngc1614.ms.split.phaseinf', 
        xaxis = 'time', 
        yaxis = 'phase',
        plotsymbol='o', 
        plotrange = [0,0,-180,180], 
        iteration= 'spw', 
        figfile=name+'ms.split.inferredcaltable/cal-phase_vs_time.png',
        subplot = 221)

### 5 ###    APPLYING CALIBRATION AND PLOTTING RESULT    ###
#===== 5.1 ## apply the bandpass, phase and flux caltables to all fields: 0,1,3
# Reminder: Bandpass and phase (field 0), flux (field 1), scientific target (field 3)
applycal(vis = name+'.ms.split',
         field = '0', # used for amp calibration
         gaintable = ['ngc1614.ms.split.bandpass', 'ngc1614.ms.split.phaseinf', 'ngc1614.ms.split.fluxinfscaled'], # apply those three caltables
         gainfield = ['','0', '0'], # Select a subset of calibrators from each gaintable. [bandpass has only one field so '', '1', '1'] 
         interp = 'linear,linear', # type of interpolation to be used in the 'Time,frequency' domains
         calwt = T,
         flagbackup = F)

applycal(vis = name+'.ms.split',
         field = '1', # used for amp calibration
         gaintable = ['ngc1614.ms.split.bandpass', 'ngc1614.ms.split.phaseinf', 'ngc1614.ms.split.fluxinfscaled'], # apply those three caltables
         gainfield = ['','1', '1'], # Select a subset of calibrators from each gaintable. [bandpass has only one field so '', '1', '1'] 
         interp = 'linear,linear', # type of interpolation to be used in the 'Time,frequency' domains
         calwt = T,
         flagbackup = F)

applycal(vis = name+'.ms.split',
         field = '3', 
         gaintable = ['ngc1614.ms.split.bandpass', 'ngc1614.ms.split.phaseinf', 'ngc1614.ms.split.fluxinfscaled'], # apply those three caltables
         gainfield = ['', '0~1', '0~1'], # Select a subset of calibrators from each gaintable.
         interp = 'linear,linear', # using linear interpolation in the 'Time,frequency' domains
         calwt = T,
         flagbackup = F)


#===== 5.2 ## Inspect the effect of uvdist, time and freq on phase/amp
os.system('mkdir '+name+'ms.split.aftercalibration')
os.system('rm -rf cal-amp_vs_time.png') 
#---------- 5.2.1 # Inspect the effect of uvdist, either using phase vs uvdist or amp vs uvdist
# Because we want to inspect the effect of uvdist we usually average all channels and all integrations (i.e., one measurement per scan) together
plotms(vis=name+'.ms.split',
       xaxis='uvdist', 
       yaxis='phase',
       ydatacolumn='data', 
       selectdata=True,
       field='0', # fields used for bandpass calibration
       averagedata=True,
       avgtime='1e8s', # average all integrations together
       avgscan=True, # one measurement per scan
       coloraxis='spw', # colorising each datapoint according to their 'baseline': 0,...,594
       highres=T, # create plot w/ higher resolution
       title='The effect of uvdist before calibration',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'ms.split.aftercalibration/'+name+'_phasevsuvdistdatacol.png',
       expformat='png') 

plotms(vis=name+'.ms.split',
       xaxis='uvdist',
       yaxis='phase',
       ydatacolumn='corrected',
       selectdata=True,
       field='0',
       averagedata=True,
       avgchannel='1000', # average all channels together
       avgtime='1e8s', # average all integrations together
       avgscan=True, # one measurement per scan
       coloraxis='spw',
       highres=T, # create plot w/ higher resolution
       title='The effect of uvdist after calibration',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'ms.split.aftercalibration/'+name+'_phasevsuvdistcorrectedcol.png',
       expformat='png') 

# This looks OK


#---------- 5.2.2 # Inspect the effect of time, either using phase vs time or amp vs time
# Because we want to inspect the effect of time we usually average all channels together
# this time, I used amp vs time for me to be easier to see the additional flaggings
plotms(vis=name+'.ms.split',
       xaxis='time',
       yaxis='amp',
       ydatacolumn='data', 
       selectdata=True,
       field='0',
       averagedata=True,
       avgchannel='1912', # average all channels together
       coloraxis='spw',
       highres=T, # create plot w/ higher resolution
       title='The effect of time before calibration',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'ms.split.aftercalibration/'+name+'_ampvstimedatacol.png',
       expformat='png') 

plotms(vis=name+'.ms.split',
       xaxis='time',
       yaxis='amp',
       ydatacolumn='corrected', 
       selectdata=True,
       field='0',
       averagedata=True,
       avgchannel='1912', # average all channels together
       coloraxis='spw',
       highres=T, # create plot w/ higher resolution
       title='The effect of time after calibration',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'ms.split.aftercalibration/'+name+'_ampvstimecorrectedcol.png',
       expformat='png') 

# Find additional flaggings and need to put them at the end of Step 2


#---------- 5.2.3 # Inspect the effect of frequency
# Because we want to inspect the effect of frequency we usually average all times together
plotms(vis=name+'.ms.split',
       xaxis='freq',
       yaxis='phase',
       ydatacolumn='data', 
       selectdata=True,
       field='0', # field for phase and bandpass calibration
       averagedata=True,
       avgchannel='',
       avgtime='1e8',
       avgscan=True,
       coloraxis='spw',
       highres=T, # create plot w/ higher resolution
       title='The effect of time before calibration',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'ms.split.aftercalibration/'+name+'_phasevsfreqdatacol.png',
       expformat='png') 

plotms(vis=name+'.ms.split',
       xaxis='freq',
       yaxis='phase',
       ydatacolumn='corrected', 
       selectdata=True,
       field='0', # field for phase and bandpass calibration
       averagedata=True,
       avgchannel='',
       avgtime='1e8',
       avgscan=True,
       coloraxis='spw',
       highres=T, # create plot w/ higher resolution
       title='The effect of time before calibration',
       overwrite=T, # overwrite plotfile if it already exists
       plotfile=name+'ms.split.aftercalibration/'+name+'_phasevsfreqdatacol.png',
       expformat='png') 

# This looks OK

# Trick: just flag here interactively on plotms window which will be done on .ms.split and rerun from step 3 onward


#===== 5.3 ## Image the phase calibrator  
os.system('rm -rf result_phasecal_cont*') #  If the image already exists, CASA will clean it further instead of producing a new image
clean(vis=name+'.ms.split',
      imagename='result_phasecal_cont', # name of the output image
      field='0', # Phase calibrator is field 0 
      spw='*:20~120', # we use all SpW and inner channels
      selectdata=T,
      mode='mfs', # Make a continuum image using Multi-frequency synthesis algorithm
      niter=500, # numner of iteration
      threshold='1.0mJy', # Stop cleaning if the maximum residual is below this value, here 1.0mJy ~ 1 sigma
      psfmode='hogbom', # Hogbom is a good choice for poorly-sampled uv-planes
      interactive=False,
      mask=[62, 62, 67, 67], # Limits the clean component placement to the region of the source.
      imsize=128, # size of the output image (~FWHM_primary_beam , i.e. field of view)
      cell='1arcsec', # size of the pixel of the output image (~FWHM_synthesis_beam/4)
      weighting='briggs',robust=0.0) # a weighting scheme that offers a good compromise between sensitivity and resolution


viewer()

