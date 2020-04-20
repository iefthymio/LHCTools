#
# Read the LPC Filling Scheme information 
#
# access to LPC web page : https://lpc.web.cern.ch/
#
# Created : 20.04.2020 - Ilias Efthymiopoulos
#

import requests
import json
import pandas as pd
import urllib

version = 1.04

class LPCFillingScheme:
    
    def __init__(self, fno):
        self.fno            = fno
        self.url            = 'http://lpc.web.cern.ch/lpc/cgi-bin/schemeInfo.py'
        self.fmt            = 'json'

        self.request_data   = self.urlRequest()
        self.name           = self.getFSchemeName()
        self.csv_data       = self.getFSchemeCsv()
        self.csv_blocks     = self.getFSchemeBlocks()

        self.injectionsDF   = self.getFSchemeInjections()
        self.bunches        = self.getFSchemeBunches()
        self.bcollisions    = self.getFSchemeCollisions()
        self.longrangeDF    = self.getFSchemeLongRangeCollisions()
        self.lrbeamDF       = self.getFSchemeLongRangeBeam()
        self.hobeamDF       = self.getFSchemeHeadOnBeam()

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
        csv_raw = self.request_data['fills'][str(self.fno)]['csv']
        return [x.strip() for x in csv_raw.split('\n')[1:-1]]

    def getFSchemeBlocks(self):
        from itertools import groupby
        return [list(g) for k, g in groupby(self.csv_data, key=bool) if k]

    def getFSchemeInjections(self):
        '''
        Bu Spac : space in ns between bunches in the same PS train,
        SPS Batch Spac : space in ns between 2 first bunches of consecutive PS trains in the SPS
        '''
        injdata = self.csv_blocks[0]
        columns = injdata[0].replace('\t','').split(',')
        injschemeDF = pd.DataFrame([raw.replace('\t','').split(',') for raw in injdata[1:-2]], columns=columns)
        injschemeDF.set_index('idx',drop=True, inplace=True)
        return injschemeDF

    def getFSchemeBunches(self):
        bdata = self.csv_blocks[1]
        bunches = {}
        for i,beam in enumerate(['B1','B2']):
            assert bdata[i].find(beam) > 0 , 'Wrong beam assignment'
            _tmp = bdata[i].split(':')[1]
            bunches[beam] = {'probe':int(_tmp.split('/')[0]), 'Nominal':int(_tmp.split('/')[1])}
        return bunches

    def getFSchemeCollisions(self):
        bcoll = {}
        bdata = self.csv_blocks[2:6]
        for iblock in bdata:
            for j in iblock:   
                bcoll[j.split(':')[0]] = int(j.split(':')[1])
        return bcoll

    @staticmethod
    def getFSchemeLongRangeIP(bdata):
        assert bdata[0].find('LONG RANGE COLL') == 0, 'Wrong block for Long Range Colissions at IP'
        columns = bdata[1].replace('\t','').split(',')
        _lrdf = pd.DataFrame([raw.replace('\t','').split(',') for raw in bdata[2:]], columns=columns)
        _lrdf['ip'] = bdata[0].replace('LONG RANGE COLL IN IR','')
        return _lrdf

    def getFSchemeLongRangeCollisions(self):
        bdata = self.csv_blocks[6:10]
        _dflist = []
        for iblock in bdata:
            _tmp = self.getFSchemeLongRangeIP(iblock)
            _dflist.append(_tmp)
        return pd.concat(_dflist)

    def getFSchemeLongRangeBeam(self):
        _dflist = []
        bdata = self.csv_blocks[10:12]
        for iblock in bdata:
            columns = iblock[1].replace('\t','').split(',')
            _df = pd.DataFrame([raw.replace('\t','').split(',') for raw in iblock[2:]], columns=columns)
            _df['beam'] = iblock[0].replace('LONG RANGE FOR BEAM ','B')
            _dflist.append(_df)
        return pd.concat(_dflist)

    def getFSchemeHeadOnBeam(self):
        _dflist = []
        bdata = self.csv_blocks[12:14]
        for iblock in bdata:
            columns = iblock[1].replace('\t','').split(',')
            columns[0] = columns[0][3:]
            _df = pd.DataFrame([raw.replace('\t','').split(',') for raw in iblock[2:]], columns=columns)
            _df['beam'] = iblock[0].replace('HEAD ON COLLISIONS FOR ','')
            _dflist.append(_df)
        return pd.concat(_dflist)