#
# LHC Filling Pattern information from CALS database.
#
# Relevant classes:
#   - LHCFillingPattern (fno)
#
# Created : 20.04.2020 - Ilias Efthymiopoulos
#

version = '3.01 - April 27, 2020 (IE)'

import cl2pd
from cl2pd import importData
pd = importData.pd
cals = importData.cals

import numpy as np

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#               Data From CALS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def getFillInjectionSheme(fno):
    var = 'LHC.STATS:LHC:INJECTION_SCHEME'
    _df = cl2pd.importData.LHCCals2pd(var,fno)
    assert _df.shape[0] != 0 , f'No Injection scheme found for fill {fno}'
    return _df[var].iloc[0]

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

def getFilledBunches(fno, bmode, toffset=pd.Timedelta('0s') ):
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

def bcollPattern(bs1, bs2, verbose):
	'''
		Fill two collision pattern for the beams
		Input
			bs1	[3564] : array with the filled slots of beam1
	'''

	b1ho1, b2ho1, b1c1, b2c1 = headon(bs1, bs2, 'IP1')
	b1ho2, b2ho2, b1c2, b2c2 = headon(bs1, bs2, 'IP2')
	b1ho8, b2ho8, b1c8, b2c8 = headon(bs1, bs2, 'IP8')

	b1coll = np.zeros(len(bs1))
	b1coll[b1ho1] += 2**1 + 2**5
	b1coll[b1ho2] += 2**2
	b1coll[b1ho8] += 2**8

	b2coll = np.zeros(len(bs2))
	b2coll[b2ho1] += 2**1 + 2**5
	b2coll[b2ho2] += 2**2
	b2coll[b2ho8] += 2**8

	return b1coll, b2coll

def getBunchTrains(fbid_b1, fbid_b2, bunchspacing):
    _tmpb1 = getBunchTrainsBeam(fbid_b1, bunchspacing)
    _tmpb1['beam'] = 'b1'
    _tmpb2 = getBunchTrainsBeam(fbid_b2, bunchspacing)
    _tmpb2['beam'] = 'b2'
    return pd.concat([_tmpb1, _tmpb2])

def getBunchTrainsBeam(fbids, bunchspacing=1):
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

def longranges(beam1, beam2, ip, nmax):
    '''
        Calculate the long-range encounters of the two beams in the selected IP
        Input :
            beam1/beam2 [3564] : array with the filled slots for each beam
            ip : the name of the ip
        Return:
            enc[nmax] : the number of encounters from [-nmax, nmax]
    '''
    if (ip == 'IP1') or (ip == 'IP5'):
        iof_bcid = 0
    if (ip == 'IP8') :
        iof_bcid = 891+3
    if (ip == 'IP2') :
        iof_bcid = 891

    enc = np.zeros(nmax)
    j = 1
    while j < nmax/2:
        beam2a = np.roll(beam2,iof_bcid+j)
        tmp = beam1 + beam2a
        aa = np.where(tmp>1)
        enc[int(nmax/2)+j] += np.size(aa)

        beam2a = np.roll(beam2, iof_bcid-j)
        tmp = beam1 + beam2a
        bb = np.where(tmp>1)
        enc[int(nmax/2)-j] += np.size(bb)
        j +=1
    return enc

def headon(bpatb1, bpatb2, ip):
    if (ip == 'IP1') or (ip == 'IP5'):
        iof_bcid = 0
    if (ip == 'IP8') :
        iof_bcid = 891+3
    if (ip == 'IP2') :
        iof_bcid = -891

    bpatb2a = np.roll(bpatb2, iof_bcid)
    tmp1 = bpatb1 + bpatb2a
    hob1 = np.where(tmp1>1)

    bpatb1a = np.roll(bpatb1, -iof_bcid)
    tmp2 = bpatb1a + bpatb2
    hob2 = np.where(tmp2>1)

    bpat1c = np.zeros(3564)
    bpat2c = np.zeros(3564)
    bpat1c[np.transpose(hob1)] = 1
    bpat2c[np.transpose(hob2)] = 1
    return hob1[0], hob2[0], bpat1c, bpat2c

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
        self.name                   = getFillInjectionSheme(fno)

        _tmp                        = self.name.split('_')
        self.bunch_spacing          = int(_tmp[0].replace('ns',''))
        self.no_bunches             = int(_tmp[1].replace('b',''))
        self.bunches_IP15           = int(_tmp[2])
        self.bunches_IP2            = int(_tmp[3])
        self.bunches_IP8            = int(_tmp[4])
        self.bunches_per_injection  = int(_tmp[5].replace('bpi',''))
        # self.no_injections          = int(_tmp[6].replace('inj',''))
        self.no_injections          = int(_tmp[6][:_tmp[6].find('inj')])


    def fsprint(self):
        print (f'''>>>>> LHC Filling pattern for fil {self.fno}''')
        mypprint('name ',self.name)
        mypprint('bunch spacing ', self.bunch_spacing)
        mypprint('bunches ', self.no_bunches)
        mypprint('bunches at IP1/5 ', self.bunches_IP15)
        mypprint('bunches at IP2 ', self.bunches_IP2)
        mypprint('bunches at IP8 ', self.bunches_IP8)
        mypprint('bunches per injection ', self.bunches_per_injection)
        mypprint('no of injections ', self.no_injections)

