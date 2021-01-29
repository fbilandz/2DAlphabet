import os

MX = ["800","900","1000","1200","1400","1600","1800","2000"]
MY = ["90","125","200","300","400"]

for mx in MX:
        for my in MY:
            cpString = "cp MX{0}_MY{1}/higgsCombineTest.AsymptoticLimits.mH120.root /afs/cern.ch/work/m/mrogulji/X_YH_4b/StatAna/limits/WP_0.8_0.95/2DAlphabet/AsymptoticLimits/higgsCombine_2016_2017_2018_MX{0}_MY{1}_LL_TT.AsymptoticLimits.mH125.root".format(mx,my)
            print(cpString)
            os.system(cpString)
