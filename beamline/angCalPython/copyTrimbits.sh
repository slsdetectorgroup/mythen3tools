for i in $(ls /dls/i11/data/2024/cm37253-2/mythen3_commissioning/standard/defaultGain/standard_defaultGain_10000eV_200V_2000ms_0.sn*); 

do 
sn=$(awk '{sub(/^.*\./, "")} 1' <<< $i); 
echo $i $sn; 
cp $i /dls_sw/p29/epics/mythen3/settingsdir/standard/10000eV/trim.$sn; 

done
