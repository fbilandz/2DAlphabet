#!/bin/bash
cd /afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/CMSSW_10_6_14/src/2DAlphabet/
eval `scramv1 runtime -sh`

pwd
echo python run_Limit.py configs/WP_0.94_0.98/RunII/SR_unblinded/RunII_LL_1DRpf_DD_NAL_11Rratio.json configs/WP_0.94_0.98/RunII/SR_unblinded/RunII_TT_1DRpf_DD_NAL_11Rratio.json -d RunII_SR_data_11_CR_zeroFail -q MX$1_MY$2 MX1600_MY125:MX$1_MY$2 --unblindData
python run_Limit.py configs/WP_0.94_0.98/RunII/SR_unblinded/RunII_LL_1DRpf_DD_NAL_11Rratio.json configs/WP_0.94_0.98/RunII/SR_unblinded/RunII_TT_1DRpf_DD_NAL_11Rratio.json -d RunII_SR_data_11_CR_zeroFail -q MX$1_MY$2 MX1600_MY125:MX$1_MY$2 --unblindData

echo MX$1_MY$2/higgsCombineTest.AsymptoticLimits.mH120.root /afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/StatAna/limits/obsLimits_1fb_signal/MX$1_MY$2.root

cp MX$1_MY$2/higgsCombineTest.AsymptoticLimits.mH120.root /afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/StatAna/limits/obsLimits_1fb_signal/MX$1_MY$2.root

cd MX$1_MY$2
combine -M Significance workspace.root --saveWorkspace --cminDefaultMinimizerStrategy 0 --pvalue
cp higgsCombineTest.Significance.mH120.root /afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/StatAna/limits/significances_1fb_signal/MX$1_MY$2.root
cd ..

rm -rf limits_condor/MX$1_MY$2
mv MX$1_MY$2 limits_condor/.