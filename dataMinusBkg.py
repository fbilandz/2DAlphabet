import ROOT as r

fData = r.TFile.Open("templates/WP_0.8_0.9/2017/JetHT.root")
fTTbar = r.TFile.Open("templates/WP_0.8_0.9/2017/TTbar.root")

hVRP = fData.Get("JetHT_mJY_mJJ_VRP_nom").Clone("dataMinusTT_VRP")
hVRF = fData.Get("JetHT_mJY_mJJ_VRF_nom").Clone("dataMinusTT_VRF")

hVRP.Add(fTTbar.Get("TTbar_mJY_mJJ_VRP_nom"),-1)
hVRF.Add(fTTbar.Get("TTbar_mJY_mJJ_VRF_nom"),-1)

fOut = r.TFile.Open("templates/WP_0.8_0.9/2017/dataMinusTT.root","RECREATE	")
fOut.cd()
hVRP.Write()
hVRF.Write()
fOut.Close()