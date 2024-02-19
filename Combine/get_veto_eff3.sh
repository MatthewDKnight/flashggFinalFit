#!/usr/bin/env bash

mx=$1
my=$2
mh=$3
m="mx${mx}my${my}"
mo="mx${mx}my${my}mh${mh}"

combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M MultiDimFit -m ${mh} -d Datacard_ggtt_resonant_${m}_ggtt_resonant.root -n _eff_check${mo} --freezeParameters MH,MX,MY --setParameters MX=${mx},MY=${my} --algo grid -P veto_eff --points 20 --autoRange 3

combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M MultiDimFit -m ${mh} -d Datacard_ggtt_resonant_${m}_ggtt_resonant.root -n _eff_check${mo}_freeze --freezeParameters MH,MX,MY,CMS_nuisance_veto_eff --setParameters MX=${mx},MY=${my} --algo grid -P veto_eff --points 20 --autoRange 3

workspace=higgsCombine_eff_check${mo}.MultiDimFit.mH${mh}.root
python get_veto_eff3.py $workspace > veto_eff_${mo}.txt

workspace=higgsCombine_eff_check${mo}_freeze.MultiDimFit.mH${mh}.root
python get_veto_eff3.py $workspace > veto_eff_${mo}_freeze.txt