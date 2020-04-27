# Software to analyze the LHC filling scheme/pattern.

(c) - Ilias Efthymiopoulos, 2020

Two packages offered: 
- LPC_FillingScheme.py  : to retrieve the FS information form the LPC web
- LHC_FillingPattern.py : to retrieve the FP inforamtion from CALS, i.e. the actual fill data.

## Usage

To initialize the tools : 
```
import LHCTools as ltools
from LHCTools import LPC_FillingScheme
from LHCTools import LHC_FillingPattern

ltools.my_cool_test_method()

```

then to access the functions and the information:

```
fno = 7334
lpcfscheme = LPC_FillingScheme.LPCFillingScheme(fno)   # -- for the LPC info

l

## Data information and variables

### LPC data:

The main class is *LPCFillingScheme(fno)*  : initialization as ``` lpcfscheme = LPC_FillingScheme.LPCFillingScheme(fno)```

Variables:
- lpcfscheme.injSchemeDF    : DF with the schedueld injection scheme 
- lpcfscheme.fsprint        : to print the class data
- lpcfscheme.longrangeDF    : DF with the long range schedule per IP.
- lpcfscheme.lrbeamDF       : DF with the HO and LR schedule per beam
- lpcfscheme.hobeamDF       : DF with the HO schedule per beam at the various IPs

**Note**:
- LPC uses RF bucket numbers instead of slots. The conversion is easy, RF = SLOT*10+1 
- LPC estimates LR ecnountes up to approx. 55m, while the **theoretically** possible max is ~140 m from the IP (TAN Y chamber separation)

### LHC data:

The main class is *LHCFillingPattern(fno)* : initialization as ```lhcfpatttern = LHC_FillingPattern.LHCFillingPatter(fno)```

Variables:
- lhcfpatt.setBunchPatternAtMode(bmode='STABLE', dt=pd.Timedelta('0s'))     : DF with the filled bunche list and pattern
- lhcfpatt.setBunchTrains()                                                 : DF with the bunch train data
- lhcfpatt.setLongRangeEncounters(nmax=38)                                  : DF with the long-range encounters up to nmax x-sings around the IPs


## Dependences

Standard pyhton libraries and,

- pytimber
- cl2pd

