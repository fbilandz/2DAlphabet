import os

MX = ["800","900","1000","1200","1400","1600","1800","2000"]
MY = ["125"]
MX = ["1000"]

for mx in MX:
        for my in MY:
		cmdString = "python run_Limit.py configs/2016/RunII_1DMCRpf_31_LL_smoothing_noUnc.json configs/2016/RunII_1DMCRpf_31_TT_smoothing_noUnc.json -d 2016_SR_noUnc MX1600_MY125:MX{0}_MY{1} -q MX{0}_MY{1}".format(mx,my)
		print(cmdString)
		os.system(cmdString)
