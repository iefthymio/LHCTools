# Software to analyze the LHC filling scheme/pattern.

(c) - Ilias Efthymiopoulos, 2020

Two packages offered: 
- LPC_FillingScheme.py  : to retrieve the FS information form the LPC web
- LHC_FillingPattern.py : to retrieve the FP inforamtion from CALS, i.e. the actual fill data.

## Usage

```
import LHCTools as ltools
from LHCTools import LPC_FillingScheme
from LHCTools import LHC_FillingPattern

```

## Data information and variables

### LPC data:

The main class is *LPCFillingScheme(fno)*  : initialization as ``` lpcfscheme=LPC_FillingScheme.LPCFillingScheme(fno)```

Variables:
- lpcfscheme.injSchemeDF    : DF with the schedueld injection scheme 
- lpcfscheme.fsprint        : to print the class data
- lpcfscheme.longrangeDF    : DF with the long range schedule per IP.
- lpcfscheme.lrbeamDF       : DF with the HO and LR schedule per beam
- lpcfscheme.hobeamDF       : DF with the HO schedule per beam at the various IPs

**Note**:
- LPC uses RF bucket numbers instead of slots. The conversion is easy, RF = SLOT*10+1 
- LPC estimates LR ecnountes up to approx. 55m, while the **theoretically** possible max is ~140 m from the IP (TAN Y chamber separation)

## Dependences

Standard python libraries