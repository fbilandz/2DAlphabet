import os
import sys

MX = [900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600,2800,3000,3500,4000]
MY = [60,70,80,90,100,125,150,200,250,300,350,400,450,500,600]
MY = [125]

def signalExists(mx,my):
    flag16 = os.path.exists("../../templates/WP_0.94_0.98/2016//MX{0}_MY{1}.root".format(mx,my))
    flag17 = os.path.exists("../../templates/WP_0.94_0.98/2017/MX{0}_MY{1}.root".format(mx,my))
    flag18 = os.path.exists("../../templates/WP_0.94_0.98/2018/MX{0}_MY{1}.root".format(mx,my))
    if(flag16 and flag17 and flag18):
        return True
    else:
        return False

def limitMissing(mx,my):
    limitsFilename = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/StatAna/limits/obsLimits_1fb_signal/MX{0}_MY{1}.root".format(mx,my)
    flagLimits = os.path.exists(limitsFilename)
    if(flagLimits):
        return False
    else:
        return True

f = open("args.txt", "w")

for mx in MX:
    for my in MY:
        if (signalExists(mx,my) and limitMissing(mx,my)):
            print(mx,my)

            # print("python run_Limit.py configs/WP_0.94_0.98/RunII/SR_unblinded/RunII_LL_1DRpf_DD_NAL_11Rratio.json configs/WP_0.94_0.98/RunII/SR_unblinded/RunII_TT_1DRpf_DD_NAL_11Rratio.json  -d RunII_SR_data_11_CR_zeroFail/ -q MX{0}_MY{1} MX1600_MY125:MX{0}_MY{1} --unblindData".format(mx,my))
            # print("cp MX{0}_MY{1}/higgsCombineTest.AsymptoticLimits.mH120.root /afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/StatAna/limits/obsLimits/MX{0}_MY{1}.root".format(mx,my))
            # print("rm -rf limits_condor/MX{0}_MY{1}".format(mx,my))
            # print("mv MX{0}_MY{1} limits_condor/.".format(mx,my))
            f.write("{0} {1}\n".format(mx,my))

f.close()


