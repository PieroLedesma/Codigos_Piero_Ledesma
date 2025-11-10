//////////-PDUARTE-//////////
#############################################################
#                                                           #
#    ARCHIVO PARA CREACION DE RELACIONES LTE-> 3G EN RNC COER01   #
#    GENERADO POR : pduarte                       #
#                                                           #
#############################################################
amos COER01
lt all
confb+
gs+
####################################################
#      UtranCell                                   #
####################################################

set UtranCell=U35971 lteMeasEnabled 1
set UtranCell=U35971 psHoToLteEnabled 1
set UtranCell=U35972 lteMeasEnabled 1
set UtranCell=U35972 psHoToLteEnabled 1
set UtranCell=U35973 lteMeasEnabled 1
set UtranCell=U35973 psHoToLteEnabled 1
set UtranCell=U51974 lteMeasEnabled 1
set UtranCell=U51974 psHoToLteEnabled 1
set UtranCell=U51975 lteMeasEnabled 1
set UtranCell=U51975 psHoToLteEnabled 1
set UtranCell=U51976 lteMeasEnabled 1
set UtranCell=U51976 psHoToLteEnabled 1
#############################################################
#      EutranFreqRelation                                   #
#############################################################

cr UtranCell=U35971,EutranFreqRelation=LTE3100
EutraNetwork=1,EutranFrequency=LTE3100
set UtranCell=U35971,EutranFreqRelation=LTE3100 cellReselectionPriority 5
set UtranCell=U35971,EutranFreqRelation=LTE3100 qRxLevMin -126
set UtranCell=U35971,EutranFreqRelation=LTE3100 threshHigh 6
set UtranCell=U35971,EutranFreqRelation=LTE3100 threshlow 0
set UtranCell=U35971,EutranFreqRelation=LTE3100 redirectionOrder 1
set UtranCell=U35971,EutranFreqRelation=LTE3100 thresh2dRwr -93
set UtranCell=U35971,EutranFreqRelation=LTE3100 coSitedCellAvailable 1

cr UtranCell=U35972,EutranFreqRelation=LTE3100
EutraNetwork=1,EutranFrequency=LTE3100
set UtranCell=U35972,EutranFreqRelation=LTE3100 cellReselectionPriority 5
set UtranCell=U35972,EutranFreqRelation=LTE3100 qRxLevMin -126
set UtranCell=U35972,EutranFreqRelation=LTE3100 threshHigh 6
set UtranCell=U35972,EutranFreqRelation=LTE3100 threshlow 0
set UtranCell=U35972,EutranFreqRelation=LTE3100 redirectionOrder 1
set UtranCell=U35972,EutranFreqRelation=LTE3100 thresh2dRwr -93
set UtranCell=U35972,EutranFreqRelation=LTE3100 coSitedCellAvailable 1

cr UtranCell=U35973,EutranFreqRelation=LTE3100
EutraNetwork=1,EutranFrequency=LTE3100
set UtranCell=U35973,EutranFreqRelation=LTE3100 cellReselectionPriority 5
set UtranCell=U35973,EutranFreqRelation=LTE3100 qRxLevMin -126
set UtranCell=U35973,EutranFreqRelation=LTE3100 threshHigh 6
set UtranCell=U35973,EutranFreqRelation=LTE3100 threshlow 0
set UtranCell=U35973,EutranFreqRelation=LTE3100 redirectionOrder 1
set UtranCell=U35973,EutranFreqRelation=LTE3100 thresh2dRwr -93
set UtranCell=U35973,EutranFreqRelation=LTE3100 coSitedCellAvailable 1

cr UtranCell=U51974,EutranFreqRelation=LTE3100
EutraNetwork=1,EutranFrequency=LTE3100
set UtranCell=U51974,EutranFreqRelation=LTE3100 cellReselectionPriority 5
set UtranCell=U51974,EutranFreqRelation=LTE3100 qRxLevMin -126
set UtranCell=U51974,EutranFreqRelation=LTE3100 threshHigh 6
set UtranCell=U51974,EutranFreqRelation=LTE3100 threshlow 0
set UtranCell=U51974,EutranFreqRelation=LTE3100 redirectionOrder 1
set UtranCell=U51974,EutranFreqRelation=LTE3100 thresh2dRwr -85
set UtranCell=U51974,EutranFreqRelation=LTE3100 coSitedCellAvailable 1

cr UtranCell=U51975,EutranFreqRelation=LTE3100
EutraNetwork=1,EutranFrequency=LTE3100
set UtranCell=U51975,EutranFreqRelation=LTE3100 cellReselectionPriority 5
set UtranCell=U51975,EutranFreqRelation=LTE3100 qRxLevMin -126
set UtranCell=U51975,EutranFreqRelation=LTE3100 threshHigh 6
set UtranCell=U51975,EutranFreqRelation=LTE3100 threshlow 0
set UtranCell=U51975,EutranFreqRelation=LTE3100 redirectionOrder 1
set UtranCell=U51975,EutranFreqRelation=LTE3100 thresh2dRwr -85
set UtranCell=U51975,EutranFreqRelation=LTE3100 coSitedCellAvailable 1

cr UtranCell=U51976,EutranFreqRelation=LTE3100
EutraNetwork=1,EutranFrequency=LTE3100
set UtranCell=U51976,EutranFreqRelation=LTE3100 cellReselectionPriority 5
set UtranCell=U51976,EutranFreqRelation=LTE3100 qRxLevMin -126
set UtranCell=U51976,EutranFreqRelation=LTE3100 threshHigh 6
set UtranCell=U51976,EutranFreqRelation=LTE3100 threshlow 0
set UtranCell=U51976,EutranFreqRelation=LTE3100 redirectionOrder 1
set UtranCell=U51976,EutranFreqRelation=LTE3100 thresh2dRwr -85
set UtranCell=U51976,EutranFreqRelation=LTE3100 coSitedCellAvailable 1

cr UtranCell=U35971,EutranFreqRelation=LTE9485
EutraNetwork=1,EutranFrequency=LTE9485
set UtranCell=U35971,EutranFreqRelation=LTE9485 cellReselectionPriority 3
set UtranCell=U35971,EutranFreqRelation=LTE9485 qRxLevMin -122
set UtranCell=U35971,EutranFreqRelation=LTE9485 threshHigh 6
set UtranCell=U35971,EutranFreqRelation=LTE9485 threshlow 0
set UtranCell=U35971,EutranFreqRelation=LTE9485 redirectionOrder 3
set UtranCell=U35971,EutranFreqRelation=LTE9485 thresh2dRwr -120
set UtranCell=U35971,EutranFreqRelation=LTE9485 coSitedCellAvailable 1

cr UtranCell=U35972,EutranFreqRelation=LTE9485
EutraNetwork=1,EutranFrequency=LTE9485
set UtranCell=U35972,EutranFreqRelation=LTE9485 cellReselectionPriority 3
set UtranCell=U35972,EutranFreqRelation=LTE9485 qRxLevMin -122
set UtranCell=U35972,EutranFreqRelation=LTE9485 threshHigh 6
set UtranCell=U35972,EutranFreqRelation=LTE9485 threshlow 0
set UtranCell=U35972,EutranFreqRelation=LTE9485 redirectionOrder 3
set UtranCell=U35972,EutranFreqRelation=LTE9485 thresh2dRwr -120
set UtranCell=U35972,EutranFreqRelation=LTE9485 coSitedCellAvailable 1

cr UtranCell=U35973,EutranFreqRelation=LTE9485
EutraNetwork=1,EutranFrequency=LTE9485
set UtranCell=U35973,EutranFreqRelation=LTE9485 cellReselectionPriority 3
set UtranCell=U35973,EutranFreqRelation=LTE9485 qRxLevMin -122
set UtranCell=U35973,EutranFreqRelation=LTE9485 threshHigh 6
set UtranCell=U35973,EutranFreqRelation=LTE9485 threshlow 0
set UtranCell=U35973,EutranFreqRelation=LTE9485 redirectionOrder 3
set UtranCell=U35973,EutranFreqRelation=LTE9485 thresh2dRwr -120
set UtranCell=U35973,EutranFreqRelation=LTE9485 coSitedCellAvailable 1

cr UtranCell=U51974,EutranFreqRelation=LTE9485
EutraNetwork=1,EutranFrequency=LTE9485
set UtranCell=U51974,EutranFreqRelation=LTE9485 cellReselectionPriority 3
set UtranCell=U51974,EutranFreqRelation=LTE9485 qRxLevMin -122
set UtranCell=U51974,EutranFreqRelation=LTE9485 threshHigh 6
set UtranCell=U51974,EutranFreqRelation=LTE9485 threshlow 0
set UtranCell=U51974,EutranFreqRelation=LTE9485 redirectionOrder 3
set UtranCell=U51974,EutranFreqRelation=LTE9485 thresh2dRwr -120
set UtranCell=U51974,EutranFreqRelation=LTE9485 coSitedCellAvailable 1

cr UtranCell=U51975,EutranFreqRelation=LTE9485
EutraNetwork=1,EutranFrequency=LTE9485
set UtranCell=U51975,EutranFreqRelation=LTE9485 cellReselectionPriority 3
set UtranCell=U51975,EutranFreqRelation=LTE9485 qRxLevMin -122
set UtranCell=U51975,EutranFreqRelation=LTE9485 threshHigh 6
set UtranCell=U51975,EutranFreqRelation=LTE9485 threshlow 0
set UtranCell=U51975,EutranFreqRelation=LTE9485 redirectionOrder 3
set UtranCell=U51975,EutranFreqRelation=LTE9485 thresh2dRwr -120
set UtranCell=U51975,EutranFreqRelation=LTE9485 coSitedCellAvailable 1

cr UtranCell=U51976,EutranFreqRelation=LTE9485
EutraNetwork=1,EutranFrequency=LTE9485
set UtranCell=U51976,EutranFreqRelation=LTE9485 cellReselectionPriority 3
set UtranCell=U51976,EutranFreqRelation=LTE9485 qRxLevMin -122
set UtranCell=U51976,EutranFreqRelation=LTE9485 threshHigh 6
set UtranCell=U51976,EutranFreqRelation=LTE9485 threshlow 0
set UtranCell=U51976,EutranFreqRelation=LTE9485 redirectionOrder 3
set UtranCell=U51976,EutranFreqRelation=LTE9485 thresh2dRwr -120
set UtranCell=U51976,EutranFreqRelation=LTE9485 coSitedCellAvailable 1

cr UtranCell=U35971,EutranFreqRelation=LTE1125
EutraNetwork=1,EutranFrequency=LTE1125
set UtranCell=U35971,EutranFreqRelation=LTE1125 cellReselectionPriority 4
set UtranCell=U35971,EutranFreqRelation=LTE1125 qRxLevMin -122
set UtranCell=U35971,EutranFreqRelation=LTE1125 threshHigh 6
set UtranCell=U35971,EutranFreqRelation=LTE1125 threshlow 0
set UtranCell=U35971,EutranFreqRelation=LTE1125 redirectionOrder 2
set UtranCell=U35971,EutranFreqRelation=LTE1125 thresh2dRwr -93
set UtranCell=U35971,EutranFreqRelation=LTE1125 coSitedCellAvailable 1

cr UtranCell=U35972,EutranFreqRelation=LTE1125
EutraNetwork=1,EutranFrequency=LTE1125
set UtranCell=U35972,EutranFreqRelation=LTE1125 cellReselectionPriority 4
set UtranCell=U35972,EutranFreqRelation=LTE1125 qRxLevMin -122
set UtranCell=U35972,EutranFreqRelation=LTE1125 threshHigh 6
set UtranCell=U35972,EutranFreqRelation=LTE1125 threshlow 0
set UtranCell=U35972,EutranFreqRelation=LTE1125 redirectionOrder 2
set UtranCell=U35972,EutranFreqRelation=LTE1125 thresh2dRwr -93
set UtranCell=U35972,EutranFreqRelation=LTE1125 coSitedCellAvailable 1

cr UtranCell=U35973,EutranFreqRelation=LTE1125
EutraNetwork=1,EutranFrequency=LTE1125
set UtranCell=U35973,EutranFreqRelation=LTE1125 cellReselectionPriority 4
set UtranCell=U35973,EutranFreqRelation=LTE1125 qRxLevMin -122
set UtranCell=U35973,EutranFreqRelation=LTE1125 threshHigh 6
set UtranCell=U35973,EutranFreqRelation=LTE1125 threshlow 0
set UtranCell=U35973,EutranFreqRelation=LTE1125 redirectionOrder 2
set UtranCell=U35973,EutranFreqRelation=LTE1125 thresh2dRwr -93
set UtranCell=U35973,EutranFreqRelation=LTE1125 coSitedCellAvailable 1

cr UtranCell=U51974,EutranFreqRelation=LTE1125
EutraNetwork=1,EutranFrequency=LTE1125
set UtranCell=U51974,EutranFreqRelation=LTE1125 cellReselectionPriority 4
set UtranCell=U51974,EutranFreqRelation=LTE1125 qRxLevMin -122
set UtranCell=U51974,EutranFreqRelation=LTE1125 threshHigh 6
set UtranCell=U51974,EutranFreqRelation=LTE1125 threshlow 0
set UtranCell=U51974,EutranFreqRelation=LTE1125 redirectionOrder 2
set UtranCell=U51974,EutranFreqRelation=LTE1125 thresh2dRwr -85
set UtranCell=U51974,EutranFreqRelation=LTE1125 coSitedCellAvailable 1

cr UtranCell=U51975,EutranFreqRelation=LTE1125
EutraNetwork=1,EutranFrequency=LTE1125
set UtranCell=U51975,EutranFreqRelation=LTE1125 cellReselectionPriority 4
set UtranCell=U51975,EutranFreqRelation=LTE1125 qRxLevMin -122
set UtranCell=U51975,EutranFreqRelation=LTE1125 threshHigh 6
set UtranCell=U51975,EutranFreqRelation=LTE1125 threshlow 0
set UtranCell=U51975,EutranFreqRelation=LTE1125 redirectionOrder 2
set UtranCell=U51975,EutranFreqRelation=LTE1125 thresh2dRwr -85
set UtranCell=U51975,EutranFreqRelation=LTE1125 coSitedCellAvailable 1

cr UtranCell=U51976,EutranFreqRelation=LTE1125
EutraNetwork=1,EutranFrequency=LTE1125
set UtranCell=U51976,EutranFreqRelation=LTE1125 cellReselectionPriority 4
set UtranCell=U51976,EutranFreqRelation=LTE1125 qRxLevMin -122
set UtranCell=U51976,EutranFreqRelation=LTE1125 threshHigh 6
set UtranCell=U51976,EutranFreqRelation=LTE1125 threshlow 0
set UtranCell=U51976,EutranFreqRelation=LTE1125 redirectionOrder 2
set UtranCell=U51976,EutranFreqRelation=LTE1125 thresh2dRwr -85
set UtranCell=U51976,EutranFreqRelation=LTE1125 coSitedCellAvailable 1

cr UtranCell=U35971,EutranFreqRelation=LTE693
EutraNetwork=1,EutranFrequency=LTE693
set UtranCell=U35971,EutranFreqRelation=LTE693 cellReselectionPriority 4
set UtranCell=U35971,EutranFreqRelation=LTE693 qRxLevMin -122
set UtranCell=U35971,EutranFreqRelation=LTE693 threshHigh 6
set UtranCell=U35971,EutranFreqRelation=LTE693 threshlow 0
set UtranCell=U35971,EutranFreqRelation=LTE693 redirectionOrder 2
set UtranCell=U35971,EutranFreqRelation=LTE693 thresh2dRwr -93
set UtranCell=U35971,EutranFreqRelation=LTE693 coSitedCellAvailable 1

cr UtranCell=U35972,EutranFreqRelation=LTE693
EutraNetwork=1,EutranFrequency=LTE693
set UtranCell=U35972,EutranFreqRelation=LTE693 cellReselectionPriority 4
set UtranCell=U35972,EutranFreqRelation=LTE693 qRxLevMin -122
set UtranCell=U35972,EutranFreqRelation=LTE693 threshHigh 6
set UtranCell=U35972,EutranFreqRelation=LTE693 threshlow 0
set UtranCell=U35972,EutranFreqRelation=LTE693 redirectionOrder 2
set UtranCell=U35972,EutranFreqRelation=LTE693 thresh2dRwr -93
set UtranCell=U35972,EutranFreqRelation=LTE693 coSitedCellAvailable 1

cr UtranCell=U35973,EutranFreqRelation=LTE693
EutraNetwork=1,EutranFrequency=LTE693
set UtranCell=U35973,EutranFreqRelation=LTE693 cellReselectionPriority 4
set UtranCell=U35973,EutranFreqRelation=LTE693 qRxLevMin -122
set UtranCell=U35973,EutranFreqRelation=LTE693 threshHigh 6
set UtranCell=U35973,EutranFreqRelation=LTE693 threshlow 0
set UtranCell=U35973,EutranFreqRelation=LTE693 redirectionOrder 2
set UtranCell=U35973,EutranFreqRelation=LTE693 thresh2dRwr -93
set UtranCell=U35973,EutranFreqRelation=LTE693 coSitedCellAvailable 1

cr UtranCell=U51974,EutranFreqRelation=LTE693
EutraNetwork=1,EutranFrequency=LTE693
set UtranCell=U51974,EutranFreqRelation=LTE693 cellReselectionPriority 4
set UtranCell=U51974,EutranFreqRelation=LTE693 qRxLevMin -122
set UtranCell=U51974,EutranFreqRelation=LTE693 threshHigh 6
set UtranCell=U51974,EutranFreqRelation=LTE693 threshlow 0
set UtranCell=U51974,EutranFreqRelation=LTE693 redirectionOrder 2
set UtranCell=U51974,EutranFreqRelation=LTE693 thresh2dRwr -85
set UtranCell=U51974,EutranFreqRelation=LTE693 coSitedCellAvailable 1

cr UtranCell=U51975,EutranFreqRelation=LTE693
EutraNetwork=1,EutranFrequency=LTE693
set UtranCell=U51975,EutranFreqRelation=LTE693 cellReselectionPriority 4
set UtranCell=U51975,EutranFreqRelation=LTE693 qRxLevMin -122
set UtranCell=U51975,EutranFreqRelation=LTE693 threshHigh 6
set UtranCell=U51975,EutranFreqRelation=LTE693 threshlow 0
set UtranCell=U51975,EutranFreqRelation=LTE693 redirectionOrder 2
set UtranCell=U51975,EutranFreqRelation=LTE693 thresh2dRwr -85
set UtranCell=U51975,EutranFreqRelation=LTE693 coSitedCellAvailable 1

cr UtranCell=U51976,EutranFreqRelation=LTE693
EutraNetwork=1,EutranFrequency=LTE693
set UtranCell=U51976,EutranFreqRelation=LTE693 cellReselectionPriority 4
set UtranCell=U51976,EutranFreqRelation=LTE693 qRxLevMin -122
set UtranCell=U51976,EutranFreqRelation=LTE693 threshHigh 6
set UtranCell=U51976,EutranFreqRelation=LTE693 threshlow 0
set UtranCell=U51976,EutranFreqRelation=LTE693 redirectionOrder 2
set UtranCell=U51976,EutranFreqRelation=LTE693 thresh2dRwr -85
set UtranCell=U51976,EutranFreqRelation=LTE693 coSitedCellAvailable 1

#############################################################
#      ExternalEutranCell                                   #
#############################################################

cr EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24664
22466
1
8103
set EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24664 physicalCellIdentity 57

cr EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24665
22466
2
8103
set EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24665 physicalCellIdentity 58

cr EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24666
22466
3
8103
set EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24666 physicalCellIdentity 59

cr EutraNetwork=1,EutranFrequency=LTE1125,ExternalEutranCell=P24664
22466
7
8103
set EutraNetwork=1,EutranFrequency=LTE1125,ExternalEutranCell=P24664 physicalCellIdentity 57

cr EutraNetwork=1,EutranFrequency=LTE1125,ExternalEutranCell=P24665
22466
8
8103
set EutraNetwork=1,EutranFrequency=LTE1125,ExternalEutranCell=P24665 physicalCellIdentity 58

cr EutraNetwork=1,EutranFrequency=LTE1125,ExternalEutranCell=P24666
22466
9
8103
set EutraNetwork=1,EutranFrequency=LTE1125,ExternalEutranCell=P24666 physicalCellIdentity 59

cr EutraNetwork=1,EutranFrequency=LTE693,ExternalEutranCell=Q24664
22466
17
8103
set EutraNetwork=1,EutranFrequency=LTE693,ExternalEutranCell=Q24664 physicalCellIdentity 57

cr EutraNetwork=1,EutranFrequency=LTE693,ExternalEutranCell=Q24665
22466
18
8103
set EutraNetwork=1,EutranFrequency=LTE693,ExternalEutranCell=Q24665 physicalCellIdentity 58

cr EutraNetwork=1,EutranFrequency=LTE693,ExternalEutranCell=Q24666
22466
19
8103
set EutraNetwork=1,EutranFrequency=LTE693,ExternalEutranCell=Q24666 physicalCellIdentity 59

#############################################################
#      EutranCellRelation                                   #
#############################################################

cr RncFunction=1,UtranCell=U35971,EutranFreqRelation=LTE3100,EutranCellRelation=L24664
EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24664

cr RncFunction=1,UtranCell=U35972,EutranFreqRelation=LTE3100,EutranCellRelation=L24664
EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24664

cr RncFunction=1,UtranCell=U35973,EutranFreqRelation=LTE3100,EutranCellRelation=L24664
EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24664

cr RncFunction=1,UtranCell=U35971,EutranFreqRelation=LTE3100,EutranCellRelation=L24665
EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24665

cr RncFunction=1,UtranCell=U35972,EutranFreqRelation=LTE3100,EutranCellRelation=L24665
EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24665

cr RncFunction=1,UtranCell=U35973,EutranFreqRelation=LTE3100,EutranCellRelation=L24665
EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24665

cr RncFunction=1,UtranCell=U35971,EutranFreqRelation=LTE3100,EutranCellRelation=L24666
EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24666

cr RncFunction=1,UtranCell=U35972,EutranFreqRelation=LTE3100,EutranCellRelation=L24666
EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24666

cr RncFunction=1,UtranCell=U35973,EutranFreqRelation=LTE3100,EutranCellRelation=L24666
EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24666

cr RncFunction=1,UtranCell=U35971,EutranFreqRelation=LTE1125,EutranCellRelation=P24664
EutraNetwork=1,EutranFrequency=LTE1125,ExternalEutranCell=P24664

cr RncFunction=1,UtranCell=U35972,EutranFreqRelation=LTE1125,EutranCellRelation=P24665
EutraNetwork=1,EutranFrequency=LTE1125,ExternalEutranCell=P24665

cr RncFunction=1,UtranCell=U35973,EutranFreqRelation=LTE1125,EutranCellRelation=P24666
EutraNetwork=1,EutranFrequency=LTE1125,ExternalEutranCell=P24666

cr RncFunction=1,UtranCell=U51974,EutranFreqRelation=LTE3100,EutranCellRelation=L24664
EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24664

cr RncFunction=1,UtranCell=U51975,EutranFreqRelation=LTE3100,EutranCellRelation=L24664
EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24664

cr RncFunction=1,UtranCell=U51976,EutranFreqRelation=LTE3100,EutranCellRelation=L24664
EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24664

cr RncFunction=1,UtranCell=U51974,EutranFreqRelation=LTE3100,EutranCellRelation=L24665
EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24665

cr RncFunction=1,UtranCell=U51975,EutranFreqRelation=LTE3100,EutranCellRelation=L24665
EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24665

cr RncFunction=1,UtranCell=U51976,EutranFreqRelation=LTE3100,EutranCellRelation=L24665
EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24665

cr RncFunction=1,UtranCell=U51974,EutranFreqRelation=LTE3100,EutranCellRelation=L24666
EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24666

cr RncFunction=1,UtranCell=U51975,EutranFreqRelation=LTE3100,EutranCellRelation=L24666
EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24666

cr RncFunction=1,UtranCell=U51976,EutranFreqRelation=LTE3100,EutranCellRelation=L24666
EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24666

cr RncFunction=1,UtranCell=U51974,EutranFreqRelation=LTE1125,EutranCellRelation=P24664
EutraNetwork=1,EutranFrequency=LTE1125,ExternalEutranCell=P24664

cr RncFunction=1,UtranCell=U51975,EutranFreqRelation=LTE1125,EutranCellRelation=P24665
EutraNetwork=1,EutranFrequency=LTE1125,ExternalEutranCell=P24665

cr RncFunction=1,UtranCell=U51976,EutranFreqRelation=LTE1125,EutranCellRelation=P24666
EutraNetwork=1,EutranFrequency=LTE1125,ExternalEutranCell=P24666

confb-
gs-
