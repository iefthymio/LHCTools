# LHCTools
Python scripts to use for LHC Analysis Data.

The tools are organized in modules - see documentation in each on how to use them.

## Instructions how to use and isntall the package:

### Installation

Use the command from your terminal : 

```
pip install --user git+https://github.com/iefthymio/LHCTools.git
```

or for upgrades:

```
pip install --upgrade --user git+https://github.com/iefthymio/LHCTools.git
```

### Usage

```
import LHCTools as LHCTools

LHCTools.my_cool_test_method()
LHCTools - It works!
```

## Acknowledgments

Instructions how to setup this project were found in : https://dev.to/rf_schubert/how-to-create-a-pip-package-and-host-on-private-github-repo-58pa

To overcome the permission error I had to set the remote directory as

git remote set-url origin https://github.com/iefthymio/LHCTools.git