import os

MY = ["125"]
MX = ["1000","1200","1400","1600","1800","2000"]#,"2200","2400","2600","2800","3000"]

for mx in MX:
        for my in MY:
            cpString = "cp RunII_MX{0}_MY{1}/higgsCombineTest.AsymptoticLimits.mH120.root /afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/StatAna/limits/RunII_mu_e/higgsCombine_2016_2017_2018_MX{0}_MY{1}.AsymptoticLimits.mH125.root".format(mx,my)
            print(cpString)
            os.system(cpString)