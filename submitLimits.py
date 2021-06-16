import os
import sys

MX = ["1000","1200","1400","1600","1800","2000"]
my = sys.argv[1]

def signalExists(mx,my):
    flag16 = os.path.exists("templates/WP_0.94_0.98/2016/MX{0}_MY{1}.root".format(mx,my))
    flag17 = os.path.exists("templates/WP_0.94_0.98/2017/MX{0}_MY{1}.root".format(mx,my))
    flag18 = os.path.exists("templates/WP_0.94_0.98/2018/MX{0}_MY{1}.root".format(mx,my))
    if(flag16 and flag17 and flag18):
        return True
    else:
        return False

def limitMissing(mx,my):
    limitsFilename = "MX{0}_MY{1}_mu/higgsCombineTest.AsymptoticLimits.mH120.root".format(mx,my)
    flagLimits = os.path.exists(limitsFilename)
    if(flagLimits):
        return False
    else:
        return True

for mx in MX:
    print(mx,my,signalExists(mx,my),limitMissing(mx,my))
    if (signalExists(mx,my) and limitMissing(mx,my)):
     	cmdString = "python run_Limit.py  configs/WP_0.94_0.98/2016/2016_LL_1DRpf_DD_NAL_22Rratio.json configs/WP_0.94_0.98/2016/2016_TT_1DRpf_DD_NAL_22Rratio.json configs/WP_0.94_0.98/2017/2017_LL_1DRpf_DD_NAL_22Rratio.json configs/WP_0.94_0.98/2017/2017_TT_1DRpf_DD_NAL_22Rratio.json configs/WP_0.94_0.98/2018/2018_TT_1DRpf_DD_NAL_22Rratio.json configs/WP_0.94_0.98/2018/2018_LL_1DRpf_DD_NAL_22Rratio.json -d RunII_bkg_est MX1600_MY125:MX{0}_MY{1} -q RunII_MX{0}_MY{1} --freezeFail".format(mx,my)
    	print(cmdString)
    	os.system(cmdString)
