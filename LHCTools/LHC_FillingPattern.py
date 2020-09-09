#
# LHC Filling Pattern information from CALS database.
#
# Relevant classes:
#   - LHCFillingPattern (fno)
#
# Created : 20.04.2020 - Ilias Efthymiopoulos
#

version = '3.20 - May 9, 2020 (IE)'

import cl2pd
from cl2pd import importData
pd = importData.pd
cals = importData.cals

<<<<<<< HEAD
import pytimber
logdb = pytimber.LoggingDB()

=======
>>>>>>> 68260e76ebd8ca472d436a227a43a42b75820665
import numpy as np
from collections import OrderedDict

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#               Data From CALS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

<<<<<<< HEAD
def _FillInjectionSheme(fno):
    var = 'LHC.STATS:LHC:INJECTION_SCHEME'
    _fill = logdb.getLHCFillData(fno)

=======
def FillInjectionSheme(fno):
    var = 'LHC.STATS:LHC:INJECTION_SCHEME'
>>>>>>> 68260e76ebd8ca472d436a227a43a42b75820665
    _df = cl2pd.importData.LHCCals2pd(var,fno)
    assert _df.shape[0] != 0 , f'No Injection scheme found for fill {fno}'
    return _df[var].iloc[0]

<<<<<<< HEAD
def FillInjectionSheme(fno):
    var = 'LHC.STATS:LHC:INJECTION_SCHEME'

    _tfill = logdb.getLHCFillData(fno)
    _data = logdb.get(var, _tfill['startTime'], _tfill['endTime'])
    assert _data[var][1] != 0 , f'No Injection scheme found for fill {fno}'
    return _data[var][1][0]



=======
>>>>>>> 68260e76ebd8ca472d436a227a43a42b75820665
def InjectionsPerFill(fno):
    '''
        Get the number of injections per beam for the selected fill(s)
        Returns separately the probe and physics bunch injections.

        For fills with multiple injection periods the last is considered and
        the numbers have a negative sign.

        Filling pattern from fast-BCT device: 
            'LHC.BCTFR.A6R4.B1:BUNCH_FILL_PATTERN'
            'LHC.BCTFR.A6R4.B2:BUNCH_FILL_PATTERN'
    '''
    injections = {'b1':{'INJPROT':0, 'INJPHYS':0}, 'b2':{'INJPROT':0, 'INJPHYS':0}}
    afilldf = importData.LHCFillsByNumber(fno)
    for mode in ['INJPROT', 'INJPHYS']:
        injdf = afilldf[afilldf['mode'].str.contains(mode)]
        if not injdf.empty:
            t1 = injdf['startTime'].iloc[-1]
            t2 = injdf['endTime'].iloc[-1]
            dur = injdf['duration'].iloc[-1]

            for ib in ['b1','b2']:
                var = 'LHC.BCTFR.A6R4.'+ib.upper()+':BUNCH_FILL_PATTERN'
                fbdf = importData.cals2pd(var, t1, t2, split=int(dur/pd.Timedelta(20,'m')))
                fbdf['nfb'] = fbdf.apply(lambda row: np.sum(row[var]), axis=1)
                no_increase = np.diff(fbdf['nfb'].values)
                nprot = len(np.where(no_increase>0)[0])
                if injdf.shape[0] > 1 :
                    injections[ib][mode] = -nprot
                else:
                    injections[ib][mode] = nprot
    return injections

def FilledBunches(fno, bmode, toffset=pd.Timedelta('0s') ):
    vlist = ['LHC.BCTFR.A6R4.B1:BUNCH_FILL_PATTERN','LHC.BCTFR.A6R4.B2:BUNCH_FILL_PATTERN']
    fldbdf = importData.LHCCals2pd(vlist, fno, beamModeList=bmode, fill_column=True, beamMode_column=True, flag='next', offset=toffset)
    fldbdf['nobunches_b1'] = fldbdf.apply(lambda row: np.sum(row['LHC.BCTFR.A6R4.B1:BUNCH_FILL_PATTERN']), axis=1 )
    fldbdf['nobunches_b2'] = fldbdf.apply(lambda row: np.sum(row['LHC.BCTFR.A6R4.B2:BUNCH_FILL_PATTERN']), axis=1 )
    fldbdf['fpatt_b1'] = fldbdf.apply(lambda row: np.array(row['LHC.BCTFR.A6R4.B1:BUNCH_FILL_PATTERN']), axis=1 )
    fldbdf['fpatt_b2'] = fldbdf.apply(lambda row: np.array(row['LHC.BCTFR.A6R4.B2:BUNCH_FILL_PATTERN']), axis=1 )
    fldbdf['bid_b1'] = fldbdf.apply(lambda row: np.where(row['fpatt_b1']>0)[0], axis=1 )
    fldbdf['bid_b2'] = fldbdf.apply(lambda row: np.where(row['fpatt_b2']>0)[0], axis=1 )
    return fldbdf

def FilledSlotsAtTime(tt):
    '''
        Obtain the list of filled BID slots at a time (as array and as filled slots with 0/1)

        Returns:
            fb1/fb2 [n]     : array with the filled bucket IDs
            b1/b2   [3564]  : arrays with the filled buckets 
            fslots          : dictionary with all the data
    '''
    # vlist = ['LHC.BQM.B1:NO_BUNCHES','LHC.BQM.B2:NO_BUNCHES','LHC.BQM.B1:FILLED_BUCKETS','LHC.BQM.B2:FILLED_BUCKETS']
    # - use the BCT data that are more reliable
    vlist = ['LHC.BCTFR.A6R4.B1:BUNCH_FILL_PATTERN','LHC.BCTFR.A6R4.B2:BUNCH_FILL_PATTERN']

    _fbct = importData.cals2pd(vlist,tt,'last')
    beam1 = _fbct.iloc[0]['LHC.BCTFR.A6R4.B1:BUNCH_FILL_PATTERN']
    beam2 = _fbct.iloc[0]['LHC.BCTFR.A6R4.B2:BUNCH_FILL_PATTERN']

    if _fbct.index.year <= 2015 : # --- it seems for 2015 the B1 and B2 had a +1 difference
        beam2 = np.roll(beam2, -1)
    b1 = np.array(beam1)
    b2 = np.array(beam2)
    fb1 = np.where(b1>0)[0]
    fb2 = np.where(b2>0)[0]

    fslots = {}
    fslots['B1'] = {}
    fslots['B2'] = {}
    fslots['B1']['Filled'] = np.array(beam1)
    fslots['B2']['Filled'] = np.array(beam2)
    fslots['B1']['FilledBID'] = fb1
    fslots['B2']['FilledBID'] = fb2
    return fb1, fb2, b1, b2, fslots

def offsetB1toB2(ip):
    offset = {'IP1':0, 'IP5':0, 'IP2':-891, 'IP8':891+3}
    return offset[ip.upper()]

def bid2pat(abid):
    bidpat = np.zeros(3564)
    bidpat[np.transpose(abid)] = 1 
    return bidpat

def pat2bid(apat, flag):
    return np.where(apat>flag)[0]


def bcollPattern(bs1, bs2):

    b1ho1, b2ho1 = headon(bs1, bs2, 'IP1')
    b1ho2, b2ho2 = headon(bs1, bs2, 'IP2')
    b1ho8, b2ho8 = headon(bs1, bs2, 'IP8')

    b1coll = bs1.copy()
    b1coll[b1ho1] += 2**1 + 2**5
    b1coll[b1ho2] += 2**2
    b1coll[b1ho8] += 2**8

    b2coll = bs2.copy()
    b2coll[b2ho1] += 2**1 + 2**5
    b2coll[b2ho2] += 2**2
    b2coll[b2ho8] += 2**8

    return b1coll, b2coll

def headonBeamPairIP(hobids, ip, beam='B1'):
    ip = ip.upper()
    iof_bcid = offsetB1toB2(ip)
    if beam == 'B2' : iof_bcid = -iof_bcid
    return np.array([(i-iof_bcid)%3564 for i in hobids])

def BunchTrains(fbid_b1, fbid_b2, bunchspacing):
    _tmpb1 = BeamBunchTrains(fbid_b1, bunchspacing)
    _tmpb1['beam'] = 'b1'
    _tmpb2 = BeamBunchTrains(fbid_b2, bunchspacing)
    _tmpb2['beam'] = 'b2'
    return pd.concat([_tmpb1, _tmpb2])

def BeamBunchTrains(fbids, bunchspacing=1):
    btrains = group_consecutives(fbids, step=bunchspacing)
    btrainA = [x[0] for x in btrains]
    btrainZ = [x[-1] for x in btrains]
    nobunch = [len(x) for x in btrains]
    deltatr = np.roll(btrainZ,1)
    deltatr[0] = deltatr[0]-3564
    trdat = {'id':np.arange(0,len(btrains)),
            'bid_first':btrainA,
            'bid_last':btrainZ,
            'bids':btrains,
            'nbunches':nobunch,
            'gap':btrainA-deltatr}
    return pd.DataFrame(trdat)

def LongRangeEncounters(fbid_b1, fbid_b2, fpat1, fpat2, nmax):
    bidB1df = pd.DataFrame({'bid':fbid_b1, 'beam':'b1'})
    bidB2df = pd.DataFrame({'bid':fbid_b2, 'beam':'b2'})
    for ip in ['ip1', 'ip2', 'ip5', 'ip8']:
        ho1_ip, ho2_ip = headon(fpat1, fpat2, ip.upper())
        bidB1df['ho'+ip]            = bidB1df.apply(lambda row: 1 if row['bid'] in ho1_ip else 0, axis=1)
        bidB1df['lr'+ip+'enc']      = bidB1df.apply(lambda row: bidlrencounters(row['bid'], fbid_b2, ip, nmax), axis=1)
        bidB1df['lr'+ip+'enc_pos']  = bidB1df.apply(lambda row: bidlrencpos(row['lr'+ip+'enc'],nmax), axis=1)
        bidB1df['lr'+ip+'enc_no']   = bidB1df.apply(lambda row: len(row['lr'+ip+'enc_pos']), axis=1)

        bidB2df['ho'+ip]            = bidB2df.apply(lambda row: 1 if row['bid'] in ho2_ip else 0, axis=1)
        bidB2df['lr'+ip+'enc']      = bidB2df.apply(lambda row: bidlrencounters(row['bid'], fbid_b1, ip, nmax), axis=1)
        bidB2df['lr'+ip+'enc_pos']  = bidB2df.apply(lambda row: bidlrencpos(row['lr'+ip+'enc'],nmax), axis=1)
        bidB2df['lr'+ip+'enc_no']   = bidB2df.apply(lambda row: len(row['lr'+ip+'enc_pos']), axis=1)
    return pd.concat([bidB1df, bidB2df])

def bidlrencounters(bid, bid2, ip, nmax):
    offset = -1*offsetB1toB2(ip)
        
    lr_left = np.zeros(nmax)
    lr_right = np.zeros(nmax)
    for j in np.arange(1, nmax):
        if (bid+offset+j)%3564 in bid2 :
            lr_right[j]= 1
        if (bid+offset-j)%3564 in bid2 :
            lr_left[j] = 1
    ip_left = lr_left[1:]
    ip_right = lr_right[1:]
    return np.concatenate((ip_left[::-1],ip_right))

def bidlrencpos(enc, nmax):
    spos = np.concatenate(((np.arange(1,nmax)*-1)[::-1], np.arange(1,nmax)))
    _enc = np.where(enc>0)[0]
    return spos[_enc]

def headon(bpatb1, bpatb2, ip):
    ip = ip.upper()
    iof_bcid = offsetB1toB2(ip)
    
    bpatb2a = np.roll(bpatb2, iof_bcid)
    tmp1 = bpatb1 + bpatb2a
    hob1 = pat2bid(tmp1,1)
    
    bpatb1a = np.roll(bpatb1, -iof_bcid)
    tmp2 = bpatb1a + bpatb2
    hob2 = pat2bid(tmp2, 1)
    return hob1, hob2

import itertools 

def cflagID():
    ips = [1, 2, 5, 8]
    d2 = {}
    _cflagdict = {}
    for i in [1,2,3,4]:
        for j in itertools.combinations(ips,i):
            key = ''
            value = 1
            for k in j:
                key += 'ip'+str(k)+'-'
                value += 2**k
            key = key[:-1]
            _cflagdict[key] = value
    _cflagdict['nc'] = 1
    cflagID = OrderedDict(sorted(_cflagdict.items(), key=lambda t: t[1]))
    cflagIDinv = dict(map(reversed, cflagID.items()))
    return cflagID, cflagIDinv

def HeadOnPattern(bpatb1, bpatb2):
    ip = ['ip1', 'ip2','ip5','ip8']
    ipflag = {'ip1':2**1, 'ip2':2**2, 'ip5':2**5, 'ip8':2**8}
    
    cpattB1AllIPs, cpattB2AllIPs = bcollPattern(bpatb1, bpatb2)

    dflist = []
    for i in ip:
        hob1, hob2 = headon(bpatb1, bpatb2, i)
        hob1p = headonBeamPairIP(hob1, i, beam='B1')
        hob2p = headonBeamPairIP(hob2, i, beam='B2')
        
        _b1  = [cpattB1AllIPs[j] for j in hob1]
        _b1p = [cpattB2AllIPs[j] for j in hob1p]
        _aux = pd.DataFrame({'ho':hob1, 
                             'hop':hob1p,
                             'cflag':_b1,
                             'cflagp':_b1p})
        _aux['beam'] = 'B1'
        _aux['ip'] = i
        dflist.append(_aux)
        
        _b2  = [cpattB2AllIPs[j] for j in hob2]
        _b2p = [cpattB1AllIPs[j] for j in hob2p]
        _aux = pd.DataFrame({'ho':hob2,
                             'hop':hob2p,
                             'cflag':_b2,
                             'cflagp':_b2p})
        _aux['beam'] = 'B2'
        _aux['ip'] = i

        dflist.append(_aux)

    hoPatDF = pd.concat(dflist)

    flagID, flagIDinv = cflagID()

    hoPatDF['cflagID']  = hoPatDF['cflag'].apply(lambda x : flagIDinv[int(x)])
    hoPatDF['cflagIDp'] = hoPatDF['cflagp'].apply(lambda x : flagIDinv[int(x)])

    return hoPatDF

def commonel(list1, list2):
	'''
		Return list of common elements in the two input lists
	'''
	return [element for element in list1 if element in list2]

def group_consecutives(vals, step=1):
	'''Return list of consecutive lists of numbers from vals (number list) '''
	run = []
	result = [run]
	expect = None
	for v in vals:
		if (v == expect) or (expect is None):
			run.append(v)
		else:
			run = [v]
			result.append(run)
		expect = v + step
	return result

def bucket2slot(buck):
	'''
		LHC bucket to slot number converter
	'''
	return [(x-1)/10 for x in buck]

def slot2bucket(slot):
	'''
		LHC slot to bucket number converter
	'''
	return [x*10+1 for x in slot]

mypprint = lambda txt,val : print (f'''{txt:_<35s} {val}''')

###############################################################################
class LHCFillingPattern:
    def __init__(self, fno):
        self.fno                    = fno
        self.name                   = FillInjectionSheme(fno)

        _tmp                        = self.name.split('_')
        self.bunch_spacing          = int(_tmp[0].replace('ns',''))
        self.no_bunches             = int(_tmp[1].replace('b',''))
        self.bunches_IP15           = int(_tmp[2])
        self.bunches_IP2            = int(_tmp[3])
        self.bunches_IP8            = int(_tmp[4])
        self.bunches_per_injection  = int(_tmp[5].replace('bpi',''))
        # self.no_injections          = int(_tmp[6].replace('inj',''))
        self.no_injections          = int(_tmp[6][:_tmp[6].find('inj')])

        self.filledBunchesDF        = None
        self.headOnDF               = None
        self.bunchTrainsDF          = None
        self.lrencountersDF         = None

    def setBunchPatternAtMode(self, bmode, dt):
        self.filledBunchesDF        = FilledBunches(self.fno, bmode, dt)
        self.filledSlots_b1         = self.filledBunchesDF['bid_b1'].values[0]
        self.filledSlots_b2         = self.filledBunchesDF['bid_b2'].values[0]
        self.filledPattern_b1       = self.filledBunchesDF['fpatt_b1'].values[0]
        self.filledPattern_b2       = self.filledBunchesDF['fpatt_b2'].values[0]

        self.setHeadOn()
        self.setBunchTrains()
        return 

    def setHeadOn(self):
        self.headOnDF               = HeadOnPattern(self.filledPattern_b1, 
                                                    self.filledPattern_b2
                                                    )
        return 

    def setBunchTrains(self):
        self.bunchTrainsDF          = BunchTrains(self.filledSlots_b1,
                                                 self.filledSlots_b2,
                                                 self.bunch_spacing/25
                                                 )
        return

    def setLongRangeEncounters(self, nmax):
        self.lrencountersDF         = LongRangeEncounters(self.filledSlots_b1,
                                                          self.filledSlots_b2,
                                                          self.filledPattern_b1,
                                                          self.filledPattern_b2,
                                                          nmax
                                                          )
        return
   
    def getBunchPatternAtMode(self):
        return self.filledBunchesDF

    def getHeadOnPattern(self):
        return self.headOnDF

    def getBunchTrains(self):
        return self.bunchTrainsDF

    def getLongRangeEncounters(self):
        return self.lrencountersDF

    def info(self):
        print (f'''>>>>> LHC Filling pattern for fil {self.fno}''')
        mypprint('name ',self.name)
        mypprint('bunch spacing ', self.bunch_spacing)
        mypprint('bunches ', self.no_bunches)
        mypprint('bunches at IP1/5 ', self.bunches_IP15)
        mypprint('bunches at IP2 ', self.bunches_IP2)
        mypprint('bunches at IP8 ', self.bunches_IP8)
        mypprint('bunches per injection ', self.bunches_per_injection)
        mypprint('no of injections ', self.no_injections)

