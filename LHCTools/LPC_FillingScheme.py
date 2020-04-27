#
# LHC Filling Scheme information from LPC data: 
#   LPC web https://lpc.web.cern.ch/

# Relevant classes:
#   - LPCFillingScheme (fno)
#
# Created : 27.04.2020 - Ilias Efthymiopoulos
#

version = '1.01 - April 27, 2020 (IE)'

import requests
import json
import pandas as pd
import urllib
import numpy as np

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#               Data From LPC web
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def getFSchemeInjections(injdata):
        '''
        Bu Spac : space in ns between bunches in the same PS train,
        SPS Batch Spac : space in ns between 2 first bunches of consecutive PS trains in the SPS
        '''
        columns = injdata[0].replace('\t','').split(',')
        injschemeDF = pd.DataFrame([raw.replace('\t','').split(',') for raw in injdata[1:-2]], columns=columns)
        for i in injschemeDF.columns:
            if i == 'Ring' : continue
            injschemeDF[i] = injschemeDF[i].astype(int)
        injschemeDF.set_index('idx',drop=True, inplace=True)
        return injschemeDF

def getFSchemeBunches(bdata):
    bunches = {}
    for i,beam in enumerate(['B1','B2']):
        assert bdata[i].find(beam) > 0 , 'Wrong beam assignment'
        _tmp = bdata[i].split(':')[1]
        bunches[beam] = {'probe':int(_tmp.split('/')[0]), 'Nominal':int(_tmp.split('/')[1])}
    return bunches

def getFSchemeCollisions(bdata):
    bcoll = {}
    for iblock in bdata:
        for j in iblock:   
            bcoll[j.split(':')[0]] = int(j.split(':')[1])
    return bcoll

def getFSchemeLongRangeIP(bdata):
    assert bdata[0].find('LONG RANGE COLL') == 0, 'Wrong block for Long Range Colissions at IP'
    columns = bdata[1].replace('\t','').split(',')
    _lrdf = pd.DataFrame([raw.replace('\t','').split(',') for raw in bdata[2:]], columns=columns)
    for i in _lrdf.columns:
        if i == 'z-pos/m' : _lrdf[i] = _lrdf[i].astype(float)
        else : _lrdf[i] = _lrdf[i].astype(int)
    _lrdf['ip'] = bdata[0].replace('LONG RANGE COLL IN IR','')
    return _lrdf

def getFSchemeLongRangeCollisions(bdata):
    _dflist = []
    for iblock in bdata:
        _tmp = getFSchemeLongRangeIP(iblock)
        _dflist.append(_tmp)
    return pd.concat(_dflist)

def getFSchemeLongRangeBeam(bdata):
    _dflist = []
    for iblock in bdata:
        columns = iblock[1].replace('\t','').split(',')
        _df = pd.DataFrame([raw.replace('\t','').split(',') for raw in iblock[2:]], columns=columns)
        _df = _df.astype(int)
        _df['beam'] = iblock[0].replace('LONG RANGE FOR BEAM ','B')
        _dflist.append(_df)
    return pd.concat(_dflist)

def getFSchemeHeadOnBeam(bdata):
    _dflist = []
    for iblock in bdata:
        columns = iblock[1].replace('\t','').split(',')
        columns[0] = columns[0][3:]
        _df = pd.DataFrame([raw.replace('\t','').split(',') for raw in iblock[2:]], columns=columns)
        _df['beam'] = iblock[0].replace('HEAD ON COLLISIONS FOR ','')
        _dflist.append(_df)
    return pd.concat(_dflist)

mypprint = lambda txt,val : print (f'''{txt:_<35s} {val}''')

###############################################################################
class LPCFillingScheme:
    ''' Class to get the Filling Scheme Information from the LPC web for a fill '''
    def __init__(self, fno):
        self.fno            = fno
        self.url            = 'http://lpc.web.cern.ch/lpc/cgi-bin/schemeInfo.py'
        self.fmt            = 'json'

        self.request_data   = self.urlRequest()
        self.name           = self.getFSchemeName()
        self.csv_data       = self.getFSchemeCsv()
        self.csv_blocks     = self.getFSchemeBlocks()

        self.injectionsDF   = getFSchemeInjections(self.csv_blocks[0])
        self.bunches        = getFSchemeBunches(self.csv_blocks[1])
        self.bcollisions    = getFSchemeCollisions(self.csv_blocks[2:6])
        self.longrangeDF    = getFSchemeLongRangeCollisions(self.csv_blocks[6:10])
        self.lrbeamDF       = getFSchemeLongRangeBeam(self.csv_blocks[10:12])
        self.hobeamDF       = getFSchemeHeadOnBeam(self.csv_blocks[12:14])

    def set_url(self, url):
        self._url = url

    def set_fmt(self, fmt):
        self._fmt = fmt

    def urlRequest(self):
        r = urllib.request.urlopen(f'''{self.url}?fill={self.fno}&fmt={self.fmt}''')
        data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        return data

    def getFSchemeName(self):
        return self.request_data['fills'][str(self.fno)]['name']

    def getFSchemeCsv(self):
        return self.request_data['fills'][str(self.fno)]['csv'].splitlines()[2:]

    def getFSchemeBlocks(self):
        from itertools import groupby
        return [list(g) for k, g in groupby(self.csv_data, key=bool) if k]

    def fsprint(self):
        print (f'''>>>>> LPC Filling scheme for fil {self.fno}''')
        mypprint('name ',self.name)
        mypprint('csv blocs ', len(self.csv_blocks))
        mypprint('injections (both beams) ',self.injectionsDF.shape[0])
        mypprint('bunches ', self.bunches)
        mypprint('collisions ', '')
        for key in self.bcollisions:
            mypprint(f'''{2*' '}{key:_<33s}''', self.bcollisions[key])
        mypprint('long ranges (2 beams, all IPs) ', self.longrangeDF.shape[0])
        mypprint('long ranges (2 beams) ', self.lrbeamDF.shape[0])
        mypprint('head on (2 beams) ', self.lrbeamDF.shape[0])