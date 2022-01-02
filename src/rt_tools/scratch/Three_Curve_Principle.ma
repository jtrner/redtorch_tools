//Maya ASCII 2019 scene
//Name: Three_Curve_Principle.ma
//Last modified: Thu, Nov 12, 2020 12:34:03 AM
//Codeset: 1252
requires maya "2019";
requires "stereoCamera" "10.0";
requires "mtoa" "3.3.0.2";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2019";
fileInfo "version" "2019";
fileInfo "cutIdentifier" "202004141915-92acaa8c08";
fileInfo "osv" "Microsoft Windows 10 Technical Preview  (Build 18362)\n";
createNode transform -n "Curves_Three_Principle";
	rename -uid "B092FA30-4E3C-C6DA-6CC0-4F97805FD619";
	addAttr -ci true -sn "EXTRA" -ln "EXTRA" -min 0 -max 0 -en "________" -at "enum";
	addAttr -ci true -sn "curvature" -ln "curvature" -at "double";
	addAttr -ci true -sn "straight_vis" -ln "straight_vis" -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "x_vis" -ln "x_vis" -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "circle_vis" -ln "circle_vis" -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "up_crv_vis" -ln "up_crv_vis" -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "low_crv_vis" -ln "low_crv_vis" -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "Up_Sub_Crv_Vis" -ln "Up_Sub_Crv_Vis" -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "Low_Sub_Crv_Vis" -ln "Low_Sub_Crv_Vis" -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "lips_annotations" -ln "lips_annotations" -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "Brow_Annotations" -ln "Brow_Annotations" -min 0 -max 1 -at "bool";
	setAttr -k off ".sz";
	setAttr -l on -k on ".EXTRA";
	setAttr -k on ".curvature";
	setAttr -k on ".straight_vis" yes;
	setAttr -k on ".x_vis" yes;
	setAttr -k on ".circle_vis" yes;
	setAttr -k on ".up_crv_vis" yes;
	setAttr -k on ".low_crv_vis" yes;
	setAttr -k on ".Up_Sub_Crv_Vis" yes;
	setAttr -k on ".Low_Sub_Crv_Vis" yes;
	setAttr -k on ".lips_annotations" yes;
	setAttr -k on ".Brow_Annotations" yes;
createNode transform -n "Curves_Circles_Grp" -p "Curves_Three_Principle";
	rename -uid "FCA9BAF5-4C27-00CA-F79A-8298EF0B3767";
	setAttr ".ovdt" 1;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".it" no;
createNode transform -n "Curves_R_circle_Grp" -p "Curves_Circles_Grp";
	rename -uid "D6D2462A-4A6C-DD7C-1F42-8594A2437B11";
	setAttr -l on ".v";
	setAttr ".rp" -type "double3" -0.60001602007625654 0 0 ;
	setAttr ".sp" -type "double3" -0.60001602007625654 0 0 ;
createNode parentConstraint -n "Curves_nurbsCircle1_parentConstraint1" -p "Curves_R_circle_Grp";
	rename -uid "E0822682-4A0D-DA90-52B1-C3A45C91FF40";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "R_FlcW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".tg[0].tor" -type "double3" 0 0 179.99999646732809 ;
	setAttr ".rst" -type "double3" -3.9504291460268348e-07 4.1140216922030959e-07 -2.9582079409770904e-31 ;
	setAttr -k on ".w0";
createNode transform -n "Curves_L_circle" -p "Curves_R_circle_Grp";
	rename -uid "F2CA2149-4BD0-64DF-F142-61948609605F";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 7.9008582876127754e-07 -1.7902834770211484e-09 3.9443045261050573e-31 ;
	setAttr ".rp" -type "double3" 0.60001602007625654 0 0 ;
	setAttr ".sp" -type "double3" 0.60001602007625654 0 0 ;
createNode nurbsCurve -n "Curves_L_circleShape" -p "Curves_L_circle";
	rename -uid "70B26E8E-4EEC-B630-0FD9-58BEB8640A92";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 22;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		0.99183229378685756 0.39181627371060657 -3.9443045261050599e-31
		0.60001602007625687 0.55411188824002267 -7.8886090522101181e-31
		0.20819974636565577 0.39181627371060668 -3.9443045261050599e-31
		0.045904131836235991 0 0
		0.20819974636565572 -0.39181627371060301 0
		0.60001602007625643 -0.55411188824001911 -7.8886090522101181e-31
		0.99183229378685778 -0.39181627371060307 -3.9443045261050599e-31
		1.1541279083162774 5.2939559203393771e-23 0
		0.99183229378685756 0.39181627371060657 -3.9443045261050599e-31
		0.60001602007625687 0.55411188824002267 -7.8886090522101181e-31
		0.20819974636565577 0.39181627371060668 -3.9443045261050599e-31
		;
createNode transform -n "Curves_R_Out_circle" -p "Curves_R_circle_Grp";
	rename -uid "4793B74C-4F9C-C3D4-820A-F290233C9961";
	setAttr -l on ".v";
	setAttr ".t" -type "double3" 7.9008582876127754e-07 -1.7902834770211484e-09 3.9443045261050573e-31 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".rp" -type "double3" -0.60001760024791406 -2.6469779601696886e-22 -7.348076984235216e-17 ;
	setAttr ".sp" -type "double3" -0.60001760024791406 -2.6469779601696886e-22 -7.348076984235216e-17 ;
createNode nurbsCurve -n "Curves_R_Out_circleShape" -p "Curves_R_Out_circle";
	rename -uid "E5950E45-46A7-B5CF-E3AE-5F8E445BF9DE";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 22;
	setAttr ".cc" -type "nurbsCurve" 
		3 4 0 no 3
		9 4.0007343210000004 4.0007343210000004 4.0007343210000004 5 6 7 7.9931295340000004
		 7.9931295340000004 7.9931295340000004
		7
		-0.60030531915069452 -0.50001326255559009 -7.351600524568718e-17
		-0.73081481680276406 -0.49993387805094042 -8.9498809101480839e-17
		-0.99187359965116761 -0.39172036740462723 -1.214692893819407e-16
		-1.154129488487935 -1.5881867761018131e-22 -1.4133990487261591e-16
		-0.99220555612570627 0.39091895358168149 -1.2150994232534071e-16
		-0.73241585938709264 0.49926818004029611 -8.9694880269100502e-17
		-0.60270954822876566 0.5000056943131751 -7.3810438390174921e-17
		;
createNode transform -n "Curves_C_circle_Grp" -p "Curves_Circles_Grp";
	rename -uid "2408201B-42F5-F0F3-F5E5-93ADE93A5E0C";
	setAttr -l on ".v" no;
createNode parentConstraint -n "Curves_nurbsCircle3_parentConstraint1" -p "Curves_C_circle_Grp";
	rename -uid "478E1B33-4AA2-3FD2-DF7C-A0A404C21A92";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "Three_Curve_PrincipleW0" -dv 1 -min 
		0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode transform -n "Curves_C_circle" -p "Curves_C_circle_Grp";
	rename -uid "FF7844CA-4A1D-9759-CA16-96B58FD4C10C";
	setAttr -l on ".v" no;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr ".s" -type "double3" 1.0000000000000002 1.0000000000000002 1.0000000000000002 ;
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode nurbsCurve -n "Curves_C_circleShape" -p "Curves_C_circle";
	rename -uid "3A32CD29-487C-EBD8-588D-B4B4651DF24A";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 22;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		0.39181627371060079 0.39181627371060657 -3.9443045261050599e-31
		7.3955709864469857e-32 0.55411188824002267 -7.8886090522101181e-31
		-0.39181627371060085 0.39181627371060668 -3.9443045261050599e-31
		-0.55411188824002044 0 -3.9443045261050599e-31
		-0.39181627371060085 -0.39181627371060301 -3.9443045261050599e-31
		7.3955709864469857e-32 -0.55411188824001911 0
		0.39181627371060074 -0.39181627371060307 -3.9443045261050599e-31
		0.55411188824002089 -3.9443045261050599e-31 -3.9443045261050599e-31
		0.39181627371060079 0.39181627371060657 -3.9443045261050599e-31
		7.3955709864469857e-32 0.55411188824002267 -7.8886090522101181e-31
		-0.39181627371060085 0.39181627371060668 -3.9443045261050599e-31
		;
createNode transform -n "Curves_L_circle_Grp" -p "Curves_Circles_Grp";
	rename -uid "7E2B7FB5-4598-CBFE-11EC-3FADF33532BC";
	setAttr -l on ".v";
	setAttr ".rp" -type "double3" 0.60001602007625654 0 0 ;
	setAttr ".sp" -type "double3" 0.60001602007625654 0 0 ;
createNode parentConstraint -n "Curves_nurbsCircle2_parentConstraint1" -p "Curves_L_circle_Grp";
	rename -uid "759A6ED2-4511-D48D-464A-8DBE2CB4AE74";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "L_FlcW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".tg[0].tot" -type "double3" 0 -5.9557004103817993e-23 0 ;
	setAttr ".tg[0].tor" -type "double3" 0 0 -179.99999646733889 ;
	setAttr ".rst" -type "double3" 3.9504291460268348e-07 4.0961188574328849e-07 0 ;
	setAttr -k on ".w0";
createNode transform -n "Curves_L_Out_circle" -p "Curves_L_circle_Grp";
	rename -uid "CCCDAFCE-4EDE-2A25-F33C-929543DD4F00";
	setAttr -l on ".v";
	setAttr ".t" -type "double3" 1.5881867761018131e-22 -1.5881867761018131e-22 -8.7581154020301047e-47 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".rp" -type "double3" 0.60001602007625654 0 0 ;
	setAttr ".sp" -type "double3" 0.60001602007625654 0 0 ;
createNode nurbsCurve -n "Curves_L_Out_circleShape" -p "Curves_L_Out_circle";
	rename -uid "C33BBADA-4B0B-88F2-FDB8-D4B90DC5AF0F";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 22;
	setAttr ".cc" -type "nurbsCurve" 
		3 4 0 no 3
		9 4.0007343210000004 4.0007343210000004 4.0007343210000004 5 6 7 7.9931295340000004
		 7.9931295340000004 7.9931295340000004
		7
		0.60030373897903699 -0.50001326255559009 -5.9179017924452492e-31
		0.73081323663110653 -0.49993387805094042 -6.5719099530791553e-31
		0.99187201947951009 -0.39172036740462723 -3.9433390642237545e-31
		1.1541279083162774 5.2939559203393771e-23 0
		0.99220397595404874 0.39091895358168149 -3.9352714560583092e-31
		0.73241427921543512 0.49926818004029611 -6.5557747367482648e-31
		0.60270796805710813 0.5000056943131751 -6.5736551190306116e-31
		;
createNode transform -n "Curves_L_In_circle_Grp" -p "Curves_Circles_Grp";
	rename -uid "A61F55F9-4C91-2CF2-E8C1-DD994E6FDA35";
	setAttr -l on ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 17;
	setAttr ".rp" -type "double3" 0.60001602007626276 5.4738221262688167e-48 0 ;
	setAttr ".sp" -type "double3" 0.60001602007626265 -3.2933402049021722e-32 0 ;
	setAttr ".spt" -type "double3" 1.1102230246252031e-16 3.2933402049021728e-32 0 ;
createNode transform -n "Curves_L_In_circle" -p "Curves_L_In_circle_Grp";
	rename -uid "EBBCD654-4F04-27A8-6F79-E4A2D6214FB3";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr ".s" -type "double3" 0.99999999999999989 1 0.99999999999999989 ;
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".rp" -type "double3" 3.9504291404757192e-07 4.0961188575586508e-07 0 ;
	setAttr ".sp" -type "double3" 3.9504291404757197e-07 4.0961188575586508e-07 0 ;
	setAttr ".spt" -type "double3" -1.0587911840678753e-22 0 0 ;
createNode nurbsCurve -n "Curves_L_In_circleShape" -p "Curves_L_In_circle";
	rename -uid "CCC1383E-4C2C-0873-0FCF-EB938C62BCEE";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_L_In_circleShapeOrig" -p "Curves_L_In_circle";
	rename -uid "9987531D-463A-C6AF-56B4-AD8625DE1F5C";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".cc" -type "nurbsCurve" 
		3 6 0 no 3
		11 7.9931295340000004 7.9931295340000004 7.9931295340000004 8 9 10 11 12 12.000734320999999
		 12.000734320999999 12.000734320999999
		9
		0.60270836310002218 0.50000610392506084 1.1102230246251565e-16
		0.60181105537702118 0.50001120604574389 1.1102230246251565e-16
		0.47030831067789575 0.50038544184262768 0
		0.20820014140856988 0.39181668332249242 0
		0.045904526879150045 4.096118857554315e-07 -1.1102230246251565e-16
		0.20820014140856982 -0.39181586409871727 0
		0.46950689685494623 -0.50005266614431365 0
		0.60020822773112237 -0.50001291128025094 1.1102230246251565e-16
		0.60030413402195104 -0.50001285294370434 1.1102230246251565e-16
		;
createNode parentConstraint -n "Curves_L_In_circle_Grp_parentConstraint1" -p "Curves_L_In_circle_Grp";
	rename -uid "EF23785C-4F33-CC75-C5F2-3983EDEFD744";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "Curves_Three_PrincipleW0" -dv 1 -min 
		0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".tg[0].tot" -type "double3" 0.60001602007626276 5.4738221262688167e-48 
		0 ;
	setAttr -k on ".w0";
createNode transform -n "Curves_R_In_circle_Grp" -p "Curves_Circles_Grp";
	rename -uid "30D3681A-4068-A914-0CDD-56925D7B0014";
	setAttr -l on ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 17;
	setAttr ".rp" -type "double3" -0.60001602007626276 5.4738221262688167e-48 0 ;
	setAttr ".sp" -type "double3" -0.60001602007626276 5.4738221262688167e-48 0 ;
createNode transform -n "Curves_R_In_circle" -p "Curves_R_In_circle_Grp";
	rename -uid "0CA7C535-4149-6C6D-5BD6-108190C2D869";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".rp" -type "double3" -3.9504291404757197e-07 4.0961188575586518e-07 0 ;
	setAttr ".sp" -type "double3" -3.9504291404757192e-07 4.0961188575586518e-07 0 ;
createNode nurbsCurve -n "Curves_R_In_circleShape" -p "Curves_R_In_circle";
	rename -uid "AA4F512A-4BF6-D001-2E87-81BFC286F47B";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_R_In_circleShapeOrig" -p "Curves_R_In_circle";
	rename -uid "80EEDA54-4DF4-B9B5-9F36-83BF742B3A0F";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".cc" -type "nurbsCurve" 
		3 6 0 no 3
		11 7.9931295340000004 7.9931295340000004 7.9931295340000004 8 9 10 11 12 12.000734320999999
		 12.000734320999999 12.000734320999999
		9
		0.60270836310002218 0.50000610392506084 1.1102230246251565e-16
		0.60181105537702118 0.50001120604574389 1.1102230246251565e-16
		0.47030831067789575 0.50038544184262768 0
		0.20820014140856988 0.39181668332249242 0
		0.045904526879150045 4.096118857554315e-07 -1.1102230246251565e-16
		0.20820014140856982 -0.39181586409871727 0
		0.46950689685494623 -0.50005266614431365 0
		0.60020822773112237 -0.50001291128025094 1.1102230246251565e-16
		0.60030413402195104 -0.50001285294370434 1.1102230246251565e-16
		;
createNode nurbsCurve -n "Curves_R_In_circleShapeOrig1" -p "Curves_R_In_circle";
	rename -uid "DD422D15-4189-0A84-9958-14B6F703A69A";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".cc" -type "nurbsCurve" 
		3 6 0 no 3
		11 7.9931295340000004 7.9931295340000004 7.9931295340000004 8 9 10 11 12 12.000734320999999
		 12.000734320999999 12.000734320999999
		9
		-0.60270836310002218 0.50000610392506095 1.1102230246251526e-16
		-0.60181105537702118 0.50001120604574401 1.1102230246251565e-16
		-0.47030831067789575 0.50038544184262779 -3.9443045261050599e-31
		-0.20820014140856991 0.39181668332249253 0
		-0.045904526879150045 4.0961188575543166e-07 -1.1102230246251605e-16
		-0.20820014140856985 -0.39181586409871738 0
		-0.46950689685494623 -0.50005266614431376 0
		-0.60020822773112237 -0.50001291128025105 1.1102230246251526e-16
		-0.60030413402195115 -0.50001285294370446 1.1102230246251565e-16
		;
createNode parentConstraint -n "Curves_R_In_circle_Grp_parentConstraint1" -p "Curves_R_In_circle_Grp";
	rename -uid "7E679B3C-43A3-B9B1-A71D-EC8B47D54DE4";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "Curves_Three_PrincipleW0" -dv 1 -min 
		0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".tg[0].tot" -type "double3" -0.60001602007626276 5.4738221262688167e-48 
		0 ;
	setAttr -k on ".w0";
createNode transform -n "Curves_Grp" -p "Curves_Three_Principle";
	rename -uid "8ECE10FA-46A9-E374-9694-5A8510D2D8E4";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode transform -n "Curves_Straight_Grp" -p "Curves_Grp";
	rename -uid "BDDD384F-41C2-97C5-9BAB-078ACAA4C438";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode transform -n "Curves_Neutral" -p "Curves_Straight_Grp";
	rename -uid "B35FB6A2-4DA8-D299-D4B1-8A8288D07846";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode nurbsCurve -n "Curves_NeutralShape" -p "Curves_Neutral";
	rename -uid "D6771072-4E40-D4AA-3EA7-71877960D882";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".ove" yes;
	setAttr ".ovc" 9;
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_NeutralShapeOrig" -p "Curves_Neutral";
	rename -uid "CC685C82-4BB5-B8FB-8120-3DBC3963B11B";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".ove" yes;
	setAttr ".ovc" 9;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 0.5 1 1 1
		5
		0.60001602007626276 9.9475983006414026e-14 0
		0.2938602840427893 8.526512829121201e-14 0
		1.9984014443252818e-15 3.5527136788005009e-14 -1.9721522630525295e-31
		-0.29386028404278214 2.4868995751603503e-14 -1.9721522630525295e-31
		-0.60001602007625654 0 -1.9721522630525295e-31
		;
createNode transform -n "Curves_Up" -p "Curves_Straight_Grp";
	rename -uid "3826CE34-498F-1170-65AA-77BD4C71A75E";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode nurbsCurve -n "Curves_UpShape" -p "Curves_Up";
	rename -uid "C68F100B-48E0-0F3C-AF26-5C80775FA15E";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".ove" yes;
	setAttr ".ovc" 9;
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_UpShapeOrig" -p "Curves_Up";
	rename -uid "6A9CAF41-470D-C94F-67D5-BF95183DBFF6";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".ove" yes;
	setAttr ".ovc" 9;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 0.5 1 1 1
		5
		0.60001602007626254 0.49996335186045826 0
		0.2938602840427893 0.49996335186044405 -1.9721522630525295e-31
		1.9984014443252818e-15 0.49996335186038721 -1.9721522630525295e-31
		-0.29386028404278208 0.499963351860373 -1.9721522630525295e-31
		-0.60001602007625654 0.49996335186035873 0
		;
createNode transform -n "Curves_Down" -p "Curves_Straight_Grp";
	rename -uid "2FFD6332-40E1-DBED-896A-8DA4D5C23518";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode nurbsCurve -n "Curves_DownShape" -p "Curves_Down";
	rename -uid "D17BB643-4345-9084-748B-7E88B77739F3";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".ove" yes;
	setAttr ".ovc" 9;
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_DownShapeOrig" -p "Curves_Down";
	rename -uid "9D973CD6-475B-53EB-F7EF-3AAC5057F4DE";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".ove" yes;
	setAttr ".ovc" 9;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 0.5 1 1 1
		5
		0.60001602007626276 -0.49996335186034813 0
		0.29386028404278924 -0.49996335186035878 0
		1.9984014443252818e-15 -0.49996335186040852 -1.9721522630525295e-31
		-0.29386028404278214 -0.49996335186042989 0
		-0.60001602007625654 -0.49996335186044405 0
		;
createNode transform -n "Curves_X_Grp" -p "Curves_Grp";
	rename -uid "DAAD765F-4BA9-A487-26FB-E0B187245B29";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode transform -n "Curves_Out_Up_Linear" -p "Curves_X_Grp";
	rename -uid "FDABC9F7-4D90-7A60-E3B1-5898507F72A0";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".rp" -type "double3" 0 -2.1316282072803006e-14 4.4408920985006262e-15 ;
	setAttr ".sp" -type "double3" 0 -2.1316282072803006e-14 4.4408920985006262e-15 ;
createNode nurbsCurve -n "Curves_Out_Up_LinearShape" -p "Curves_Out_Up_Linear";
	rename -uid "E3AC20C8-443D-E7F2-A12C-1D9B6F625948";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_Out_Up_LinearShapeOrig" -p "Curves_Out_Up_Linear";
	rename -uid "7253D5A1-49AE-5773-1F8A-FDB347A2AA89";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 0.5 1 1 1
		5
		0.60001602007625654 0.49996452063480135 3.9968028886505635e-15
		0.29386027051866631 0.37240984546844308 4.4408920985006262e-15
		-4.9303806576313238e-32 0.24998226031738824 4.4408920985006262e-15
		-0.29386027051866631 0.12755162332703662 4.4408920985006262e-15
		-0.60001602007625654 -2.486899575160351e-14 4.4408920985006262e-15
		;
createNode transform -n "Curves_Inn_Up_Linear" -p "Curves_X_Grp";
	rename -uid "9AACCC1E-435A-C4F6-7E17-5B8184967446";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode nurbsCurve -n "Curves_Inn_Up_LinearShape" -p "Curves_Inn_Up_Linear";
	rename -uid "D1A640DD-4A02-7C71-AD69-E0B31101CE4F";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_Inn_Up_LinearShapeOrig" -p "Curves_Inn_Up_Linear";
	rename -uid "C60CD27E-4640-7530-F7B8-60ADFBF4F307";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 0.5 1 1 1
		5
		0.60001602007625654 1.9721522630525295e-31 0
		0.29386027051866637 0.12755162332706504 -1.9721522630525295e-31
		0 0.24998226031742021 -1.9721522630525295e-31
		-0.29386027051866642 0.372409845468475 0
		-0.60001602007625654 0.49996452063483332 0
		;
createNode transform -n "Curves_Inn_Down_Linear" -p "Curves_X_Grp";
	rename -uid "0556756D-4E60-6EFC-E742-D0BBB70E4ED9";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode nurbsCurve -n "Curves_Inn_Down_LinearShape" -p "Curves_Inn_Down_Linear";
	rename -uid "E4D0C50B-4358-161A-BDC6-F581A38CB144";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_Inn_Down_LinearShapeOrig" -p "Curves_Inn_Down_Linear";
	rename -uid "32AD5799-407D-8B03-2BBA-328DC8E46D50";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 0.5 1 1 1
		5
		0.60001602007625654 1.9721522630525295e-31 0
		0.29386027051866631 -0.12755162332706149 -1.9721522630525295e-31
		4.9303806576313238e-32 -0.24998226031741314 -1.9721522630525295e-31
		-0.29386027051866631 -0.37241289730776828 0
		-0.60001602007625654 -0.4999675724741231 0
		;
createNode transform -n "Curves_Out_Down_Linear" -p "Curves_X_Grp";
	rename -uid "D446C3D9-4644-1A5C-EE29-A6B4260F54C9";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".rp" -type "double3" 0 -3.5527136788005009e-15 0 ;
	setAttr ".sp" -type "double3" 0 -3.5527136788005009e-15 0 ;
createNode nurbsCurve -n "Curves_Out_Down_LinearShape" -p "Curves_Out_Down_Linear";
	rename -uid "4F905987-4054-3F8E-C1E5-8FAD731C352A";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_Out_Down_LinearShapeOrig" -p "Curves_Out_Down_Linear";
	rename -uid "E425F3B5-4826-31AF-48B5-07AEC2916A39";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 0.5 1 1 1
		5
		0.60001602007625676 -0.49996452063482621 0
		0.29386027051866637 -0.37240984546847145 -1.9721522630525295e-31
		4.9303806576313238e-32 -0.24998226031741314 -1.9721522630525295e-31
		-0.29386027051866637 -0.12755162332706149 0
		-0.60001602007625654 0 -1.9721522630525295e-31
		;
createNode transform -n "Curves_Up_Grp" -p "Curves_Grp";
	rename -uid "6EA14793-469A-D87E-A5C8-4FAB091D02E7";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode transform -n "Curves_Neutral1" -p "Curves_Up_Grp";
	rename -uid "21767422-4E98-DE8F-BA15-889CF6E92FDC";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode nurbsCurve -n "Curves_Neutral1Shape" -p "Curves_Neutral1";
	rename -uid "6ECC5E46-4B87-EE11-69DE-28940254286A";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".ove" yes;
	setAttr ".ovc" 20;
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_Neutral1ShapeOrig" -p "Curves_Neutral1";
	rename -uid "3FD3D2B6-4F25-C50F-595F-D39833E57738";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".ove" yes;
	setAttr ".ovc" 20;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 0.5 1 1 1
		5
		0.60001602007626276 9.9475983006414013e-14 -3.9443045261050599e-31
		0.29386028404278935 0.50181727548643451 4.4408920985006262e-15
		1.9984014443252814e-15 0.50068883097886285 -7.8886090522101181e-31
		-0.29386028404278203 0.50181727548647004 -3.9443045261050599e-31
		-0.60001602007625665 0 -7.8886090522101181e-31
		;
createNode transform -n "Curves_Neutral3" -p "Curves_Up_Grp";
	rename -uid "B5EE67CF-4F81-0DD7-508B-F6BA0172716E";
	setAttr -l on ".v";
	setAttr ".t" -type "double3" 0 0.5 0 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr ".s" -type "double3" 1 -1 1 ;
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode nurbsCurve -n "Curves_Neutral3Shape" -p "Curves_Neutral3";
	rename -uid "5100C457-4A17-FB61-9497-298B6D64C868";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".ove" yes;
	setAttr ".ovc" 18;
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_Neutral3ShapeOrig" -p "Curves_Neutral3";
	rename -uid "2EB20920-4AAB-5310-4A38-C086CD112A51";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".ove" yes;
	setAttr ".ovc" 18;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 0.5 1 1 1
		5
		0.60001602007626276 9.9475983006414013e-14 -3.9443045261050599e-31
		0.29386028404278935 0.50181727548643451 4.4408920985006262e-15
		1.9984014443252814e-15 0.50068883097886285 -7.8886090522101181e-31
		-0.29386028404278203 0.50181727548647004 -3.9443045261050599e-31
		-0.60001602007625665 0 -7.8886090522101181e-31
		;
createNode transform -n "Curves_Down_Grp" -p "Curves_Grp";
	rename -uid "D22F41B3-4D60-86E9-42E7-85B6352144DE";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode transform -n "Curves_Neutral2" -p "Curves_Down_Grp";
	rename -uid "778E54E7-4941-C6E2-D48D-43886AD7E33C";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr ".s" -type "double3" 1 -1 1 ;
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode nurbsCurve -n "Curves_Neutral2Shape" -p "Curves_Neutral2";
	rename -uid "E7A0FB8E-49D3-D80D-D152-A08A8CD75141";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".ove" yes;
	setAttr ".ovc" 20;
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_Neutral2ShapeOrig" -p "Curves_Neutral2";
	rename -uid "54CBA5BD-48CA-C010-0275-B49AB96C0E44";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".ove" yes;
	setAttr ".ovc" 20;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 0.5 1 1 1
		5
		0.60001602007626276 9.9475983006414013e-14 -3.9443045261050599e-31
		0.29386028404278935 0.50181727548643451 4.4408920985006262e-15
		1.9984014443252814e-15 0.50068883097886285 -7.8886090522101181e-31
		-0.29386028404278203 0.50181727548647004 -3.9443045261050599e-31
		-0.60001602007625665 0 -7.8886090522101181e-31
		;
createNode transform -n "Curves_Neutral4" -p "Curves_Down_Grp";
	rename -uid "D846777E-4387-CFE4-FD68-BB9553BB135B";
	setAttr -l on ".v";
	setAttr ".t" -type "double3" 0 -0.5 0 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode nurbsCurve -n "Curves_Neutral4Shape" -p "Curves_Neutral4";
	rename -uid "43DF7011-40D4-2C0A-481E-6B9C540EFED6";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".ove" yes;
	setAttr ".ovc" 18;
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_Neutral4ShapeOrig" -p "Curves_Neutral4";
	rename -uid "443ED219-4442-F24B-B221-969C5DC89445";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".ove" yes;
	setAttr ".ovc" 18;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 0.5 1 1 1
		5
		0.60001602007626276 9.9475983006414013e-14 -3.9443045261050599e-31
		0.29386028404278935 0.50181727548643451 4.4408920985006262e-15
		1.9984014443252814e-15 0.50068883097886285 -7.8886090522101181e-31
		-0.29386028404278203 0.50181727548647004 -3.9443045261050599e-31
		-0.60001602007625665 0 -7.8886090522101181e-31
		;
createNode transform -n "Curves_Up_Sub_Grp" -p "Curves_Grp";
	rename -uid "C4F7D9D7-4F27-247E-6219-54BC4D0CFCA2";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode transform -n "Curves_Inn_Up1" -p "Curves_Up_Sub_Grp";
	rename -uid "521C6B41-4B83-DB1F-EBF1-BC9A359BAB80";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode nurbsCurve -n "Curves_Inn_Up1Shape" -p "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Inn_Up1";
	rename -uid "01A427D6-4665-30DD-0B8E-33995AEF767F";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_Inn_Up1ShapeOrig" -p "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Inn_Up1";
	rename -uid "9A1867CD-4DDC-994E-DA7F-F2BB27EE24A7";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 0.5 1 1 1
		5
		0.60001602007626276 9.9475983006414026e-14 0
		0.2938602840427893 0 0
		1.9984014443252818e-15 0 -1.9721522630525295e-31
		-0.29386028404278208 0.45046806417586538 -1.9721522630525295e-31
		-0.60001602007625654 0 -1.9721522630525295e-31
		;
createNode transform -n "Curves_Mid_Up" -p "Curves_Up_Sub_Grp";
	rename -uid "095BF035-4935-532B-E32F-08A95E30CD53";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode nurbsCurve -n "Curves_Mid_UpShape" -p "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Mid_Up";
	rename -uid "0A5F7E7A-4D2E-0BE8-0BA2-359C6BF09C57";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_Mid_UpShapeOrig" -p "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Mid_Up";
	rename -uid "64CE3743-4F26-097A-0F09-8F87F73380AA";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 0.5 1 1 1
		5
		0.60001602007626276 9.9475983006414026e-14 0
		0.2938602840427893 0.051349211310629521 0
		1.9984014443252818e-15 0.50068883097886285 -1.9721522630525295e-31
		-0.29386028404278208 0.051349211310629528 -1.9721522630525295e-31
		-0.60001602007625654 0 -1.9721522630525295e-31
		;
createNode transform -n "Curves_Out_Up2" -p "Curves_Up_Sub_Grp";
	rename -uid "828F2AD3-4FCE-227A-AB45-87B5FBE660C8";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode nurbsCurve -n "Curves_Out_Up2Shape" -p "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Out_Up2";
	rename -uid "8F4408AA-496C-EB00-2007-CB85B767FEFF";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_Out_Up2ShapeOrig" -p "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Out_Up2";
	rename -uid "DB3C7D08-4957-071C-D116-26831F113354";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 0.5 1 1 1
		5
		0.60001602007626276 1.2434497875801753e-13 4.4408920985006262e-15
		0.2938602840427893 0.45046806417589025 4.4408920985006262e-15
		1.9984014443252814e-15 2.4868995751603503e-14 4.4408920985006262e-15
		-0.29386028404278214 2.4868995751603503e-14 4.4408920985006262e-15
		-0.60001602007625654 2.4868995751603503e-14 4.4408920985006262e-15
		;
createNode transform -n "Curves_Down_Sub_Grp" -p "Curves_Grp";
	rename -uid "0E22E8A8-45B1-6C7D-F369-F0AC7A64420D";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode transform -n "Curves_Out_Up2" -p "Curves_Down_Sub_Grp";
	rename -uid "144DA5A2-4E19-31FF-3C73-4DB3D0CED94C";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode nurbsCurve -n "Curves_Out_Up2Shape" -p "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Out_Up2";
	rename -uid "81DC6771-4C3D-884F-40C6-F9B161EEC23D";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_Out_Up2ShapeOrig" -p "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Out_Up2";
	rename -uid "6768ADDE-429A-A9EE-DA89-E4BF0A4E5EC4";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 0.5 1 1 1
		5
		0.60001602007626276 -1.2434497875801753e-13 4.4408920985006262e-15
		0.29386028404278924 -0.45046806417589025 4.4408920985006262e-15
		1.9984014443252814e-15 -2.486899575160351e-14 4.4408920985006262e-15
		-0.29386028404278214 -2.4868995751603507e-14 4.4408920985006262e-15
		-0.60001602007625654 -2.486899575160351e-14 4.4408920985006262e-15
		;
createNode transform -n "Curves_Inn_Up1" -p "Curves_Down_Sub_Grp";
	rename -uid "5F90F899-47B8-8FF3-F42F-D8B788ED345D";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode nurbsCurve -n "Curves_Inn_Up1Shape" -p "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Inn_Up1";
	rename -uid "5207AB9C-40F6-75BA-D512-069558355BED";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_Inn_Up1ShapeOrig" -p "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Inn_Up1";
	rename -uid "C724D624-45DE-F8E3-40E8-499FD018EDB9";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 0.5 1 1 1
		5
		0.60001602007626276 -9.9475983006414026e-14 0
		0.2938602840427893 0 0
		1.9984014443252818e-15 0 -1.9721522630525295e-31
		-0.29386028404278214 -0.45046806417586538 0
		-0.60001602007625654 0 -1.9721522630525295e-31
		;
createNode transform -n "Curves_Mid_Up" -p "Curves_Down_Sub_Grp";
	rename -uid "6997AECE-41D8-413C-B019-60A45537CBB2";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode nurbsCurve -n "Curves_Mid_UpShape" -p "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Mid_Up";
	rename -uid "F2C8FBCE-4459-767D-DF67-BBAE9D8D2873";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".tw" yes;
createNode nurbsCurve -n "Curves_Mid_UpShapeOrig" -p "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Mid_Up";
	rename -uid "D4F89D97-41EB-0167-4ED1-85AB5653B040";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 0.5 1 1 1
		5
		0.60001602007626276 -9.9475983006414026e-14 0
		0.29386028404278924 -0.051349211310629528 0
		1.9984014443252818e-15 -0.50068883097886285 -1.9721522630525295e-31
		-0.29386028404278214 -0.051349211310629521 -3.9443045261050599e-31
		-0.60001602007625654 0 -1.9721522630525295e-31
		;
createNode transform -n "Curves_Rig_Grp" -p "Curves_Three_Principle";
	rename -uid "C548094F-4D10-CB02-D35A-FE97AEC0F92B";
	setAttr -l on -k off -cb on ".v" no;
	setAttr ".sech" no;
	setAttr -cb on ".t";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -cb on ".r";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -cb on ".s";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode transform -n "Curves_Top_Loc" -p "Curves_Rig_Grp";
	rename -uid "0BA8F636-48C5-BFC0-8808-41ABFD3B1FEC";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr ".s" -type "double3" 1 1.0000000000000002 1 ;
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".rp" -type "double3" 0 0.50000000000000011 0 ;
	setAttr ".sp" -type "double3" 0 0.5 0 ;
	setAttr ".spt" -type "double3" 0 1.1102230246251568e-16 0 ;
createNode locator -n "Curves_Top_LocShape" -p "Curves_Top_Loc";
	rename -uid "1CB7496B-49FF-90FC-4FE1-0697A17C9EA0";
	setAttr -k off ".v";
	setAttr ".lp" -type "double3" 0 0.5 0 ;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "Curves_Bot_Loc" -p "Curves_Rig_Grp";
	rename -uid "DD0356D2-4C23-9C0A-A12B-4E88BA10F841";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr ".s" -type "double3" 1 1.0000000000000002 1 ;
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".rp" -type "double3" 0 -0.50000000000000011 0 ;
	setAttr ".sp" -type "double3" 0 -0.5 0 ;
	setAttr ".spt" -type "double3" 0 -1.1102230246251568e-16 0 ;
createNode locator -n "Curves_Bot_LocShape" -p "Curves_Bot_Loc";
	rename -uid "DAEE15D7-487B-ADCA-0B7C-0D89811A5781";
	setAttr -k off ".v";
	setAttr ".lp" -type "double3" 0 -0.5 0 ;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "Curves_BendHandle" -p "Curves_Rig_Grp";
	rename -uid "0D058934-4A78-046E-DD6C-F08DFDF3AFF3";
	setAttr -l on ".v";
	setAttr ".t" -type "double3" 1.1102230246251565e-16 1.7763568394002513e-15 2.2204460492503131e-15 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr ".r" -type "double3" -90.000000000000071 89.999999999999986 0 ;
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr ".s" -type "double3" 1.1541279083162772 1.1541279083162772 1.1541279083162777 ;
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".rp" -type "double3" -4.5522319324760568e-31 -1.4225724788987677e-32 -2.2761159662380293e-31 ;
	setAttr ".rpt" -type "double3" 4.6944891803659352e-31 -2.1338587183481517e-31 6.8283478987140869e-31 ;
	setAttr ".sp" -type "double3" -3.9443045261050599e-31 -1.2325951644078309e-32 -1.9721522630525295e-31 ;
	setAttr ".spt" -type "double3" -6.0792740637099775e-32 -1.899773144909368e-33 -3.0396370318549975e-32 ;
	setAttr ".smd" 7;
createNode deformBend -n "Curves_BendHandleShape" -p "Curves_BendHandle";
	rename -uid "15C519E4-4513-37F2-78E2-F1AAFFAD6161";
	setAttr -k off ".v";
	setAttr ".dd" -type "doubleArray" 3 -1 1 0 ;
	setAttr ".hw" 1.219046154128046;
createNode transform -n "Curves_L_Flc_Surf" -p "Curves_Rig_Grp";
	rename -uid "9DBEA13A-4908-327C-AE83-FE85D28C6160";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr ".s" -type "double3" 0.99999999999999989 1 0.99999999999999989 ;
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".rp" -type "double3" 2.9802322387695306e-08 0 0 ;
	setAttr ".sp" -type "double3" 2.9802322387695313e-08 0 0 ;
	setAttr ".spt" -type "double3" -6.6174449004242207e-24 0 0 ;
createNode mesh -n "Curves_L_Flc_SurfShape" -p "Curves_L_Flc_Surf";
	rename -uid "817E4962-42C5-6CF7-1E11-408F136BB539";
	setAttr -k off ".v";
	setAttr -s 6 ".iog[0].og";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".pv" -type "double2" 0.50000008207280189 0.50000008207280189 ;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".dr" 3;
	setAttr ".dsm" 2;
createNode mesh -n "Curves_L_Flc_SurfShapeOrig" -p "Curves_L_Flc_Surf";
	rename -uid "3CD225A6-447A-53C3-0FDF-7A95532E95BB";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 3 ".uvst[0].uvsp[0:2]" -type "float2" 0.016639322 0.016639322
		 0.98336083 0.016639382 0.49999997 0.98336083;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr -s 3 ".vt[0:2]"  0.58019125 -0.019824803 0 0.6198408 -0.019824803 0
		 0.600016 0.019824803 0;
	setAttr -s 3 ".ed[0:2]"  0 1 0 0 2 0 1 2 0;
	setAttr -ch 3 ".fc[0]" -type "polyFaces" 
		f 3 0 2 -2
		mu 0 3 0 1 2;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
createNode transform -n "Curves_R_Flc_Surf" -p "Curves_Rig_Grp";
	rename -uid "E023069D-4F3D-4EDF-300D-E488A2137223";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr ".s" -type "double3" 0.99999999999999989 1 0.99999999999999989 ;
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".rp" -type "double3" 2.9802322387695306e-08 0 0 ;
	setAttr ".sp" -type "double3" 2.9802322387695313e-08 0 0 ;
	setAttr ".spt" -type "double3" -6.6174449004242207e-24 0 0 ;
createNode mesh -n "Curves_R_Flc_SurfShape" -p "Curves_R_Flc_Surf";
	rename -uid "59ECF6F4-4CA4-78AA-3F5F-6688F8F4A884";
	setAttr -k off ".v";
	setAttr -s 6 ".iog[0].og";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".pv" -type "double2" 0.50000008207280189 0.50000008207280189 ;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".dr" 3;
	setAttr ".dsm" 2;
createNode mesh -n "Curves_R_Flc_SurfShapeOrig" -p "Curves_R_Flc_Surf";
	rename -uid "866D6476-41B2-B22A-2890-A68D382E6974";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 3 ".uvst[0].uvsp[0:2]" -type "float2" 0.016639322 0.016639322
		 0.98336083 0.016639382 0.49999997 0.98336083;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr -s 4 ".pt[0:3]" -type "float3"  -1.1603825 0 0 -1.2396815 
		0 0 -1.200032 0 0 0 0 0;
	setAttr -s 3 ".vt[0:2]"  0.58019125 -0.019824803 0 0.6198408 -0.019824803 0
		 0.600016 0.019824803 0;
	setAttr -s 3 ".ed[0:2]"  0 1 0 0 2 0 1 2 0;
	setAttr -ch 3 ".fc[0]" -type "polyFaces" 
		f 3 1 -3 -1
		mu 0 3 0 2 1;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
createNode transform -n "Curves_L_Flc" -p "Curves_Rig_Grp";
	rename -uid "E22BCE32-4976-8C68-7F0D-CD866E8CAF34";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999989 0.99999999999999978 ;
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".it" no;
createNode follicle -n "Curves_L_FlcShape" -p "Curves_L_Flc";
	rename -uid "DC5E744F-435F-72D5-F1B3-7DB1D8D9B1CB";
	setAttr -k off ".v";
	setAttr ".pu" 0.50001007450580592;
	setAttr ".pv" 0.50001007450580592;
	setAttr ".sim" 0;
	setAttr -s 2 ".sts[0:1]"  0 1 3 1 0.2 3;
	setAttr -s 2 ".cws[0:1]"  0 1 3 1 0.2 3;
	setAttr -s 2 ".ats[0:1]"  0 1 3 1 0.2 3;
createNode transform -n "Curves_R_Flc" -p "Curves_Rig_Grp";
	rename -uid "D79F9E54-4188-5C7D-2FBC-D299367CCB09";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr ".s" -type "double3" 0.99999999999999978 1 0.99999999999999989 ;
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".it" no;
createNode follicle -n "Curves_R_FlcShape" -p "Curves_R_Flc";
	rename -uid "18ABE42A-44BF-8B94-E092-F08A46E25054";
	setAttr -k off ".v";
	setAttr ".pu" 0.50001007450580592;
	setAttr ".pv" 0.50001007450580592;
	setAttr ".sim" 0;
	setAttr -s 2 ".sts[0:1]"  0 1 3 1 0.2 3;
	setAttr -s 2 ".cws[0:1]"  0 1 3 1 0.2 3;
	setAttr -s 2 ".ats[0:1]"  0 1 3 1 0.2 3;
createNode transform -n "Curves_Lip_Annotations" -p "Curves_Three_Principle";
	rename -uid "E92EF506-4481-DDF0-27A9-2A8D16D9BF54";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode transform -n "Curves_annotationLocator1" -p "Curves_Lip_Annotations";
	rename -uid "6620DE5E-4BD1-0124-E979-E8964BB8B74A";
	setAttr -l on ".v";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode locator -n "Curves_annotationLocator1Shape" -p "Curves_annotationLocator1";
	rename -uid "DBA44D81-404A-AAFE-2379-A0B5F7FDAE8F";
	setAttr -k off ".v";
	setAttr ".los" -type "double3" 0.001 0.001 0.001 ;
createNode transform -n "Curves_annotation3" -p "Curves_annotationLocator1";
	rename -uid "0516CDB4-4AF6-A1E9-F473-609199ED86A4";
	setAttr -l on -k off -cb on ".v";
	setAttr -cb on ".t" -type "double3" 0.16303362795138232 0.10991951207811759 0 ;
	setAttr -cb on ".t";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -cb on ".r";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -cb on ".s";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode annotationShape -n "Curves_annotationShape3" -p "|Curves_Three_Principle|Curves_Lip_Annotations|Curves_annotationLocator1|Curves_annotation3";
	rename -uid "22A43EEA-4762-9627-90D0-9E8607D847F8";
	setAttr -k off ".v";
	setAttr ".txt" -type "string" "Lip Corner";
createNode pointConstraint -n "Curves_annotationLocator1_pointConstraint1" -p "Curves_annotationLocator1";
	rename -uid "C7E87C7A-435D-2B57-8487-75BFBF58D68D";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "Curves_L_FlcW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 0.60001641511917103 4.0961188574328844e-07 0 ;
	setAttr -k on ".w0";
createNode transform -n "Curves_annotationLocator2" -p "Curves_Lip_Annotations";
	rename -uid "ACB74A87-4930-5054-24A2-DCB67A2C33E2";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode locator -n "Curves_annotationLocator2Shape" -p "Curves_annotationLocator2";
	rename -uid "2B3A48AB-49B8-71E5-B98C-CD84DA4A841E";
	setAttr -k off ".v";
	setAttr ".los" -type "double3" 0.001 0.001 0.001 ;
createNode transform -n "Curves_annotation3" -p "Curves_annotationLocator2";
	rename -uid "E2299A78-4737-038E-0F2B-6B94706681D6";
	setAttr -l on -k off -cb on ".v";
	setAttr -cb on ".t" -type "double3" -0.10820785517605955 -0.4500099950526647 0 ;
	setAttr -cb on ".t";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -cb on ".r";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -cb on ".s";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode annotationShape -n "Curves_annotationShape3" -p "|Curves_Three_Principle|Curves_Lip_Annotations|Curves_annotationLocator2|Curves_annotation3";
	rename -uid "587D8C3A-44C4-AE44-8A3F-43A0A8DAECBA";
	setAttr -k off ".v";
	setAttr ".txt" -type "string" "Lip Center";
createNode transform -n "Curves_annotationLocator3" -p "Curves_Lip_Annotations";
	rename -uid "8D86A905-4CB6-C266-CA0C-CBBDB476B85A";
	setAttr -l on ".v";
	setAttr ".t" -type "double3" 0 0.49977763988448443 0 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode locator -n "Curves_annotationLocator3Shape" -p "Curves_annotationLocator3";
	rename -uid "D2D44F4D-4EE4-D1DA-3154-99B896D1A5B0";
	setAttr -k off ".v";
	setAttr ".los" -type "double3" 0.001 0.001 0.001 ;
createNode transform -n "Curves_annotation3" -p "Curves_annotationLocator3";
	rename -uid "BF434BFE-4A4A-EF2B-0D16-10B57CAC7879";
	setAttr -l on -k off -cb on ".v";
	setAttr -cb on ".t" -type "double3" 0.16852784740842502 0.11847267572686759 0 ;
	setAttr -cb on ".t";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -cb on ".r";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -cb on ".s";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode annotationShape -n "Curves_annotationShape3" -p "|Curves_Three_Principle|Curves_Lip_Annotations|Curves_annotationLocator3|Curves_annotation3";
	rename -uid "ED21DF9D-4EFA-C1D5-DC39-689A7D6AA0F1";
	setAttr -k off ".v";
	setAttr ".txt" -type "string" "Nose Bottom";
createNode transform -n "Curves_annotationLocator8" -p "Curves_Lip_Annotations";
	rename -uid "48E16140-4A75-CDD3-7C00-0E88FF5BEA63";
	setAttr -l on ".v";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode locator -n "Curves_annotationLocator8Shape" -p "Curves_annotationLocator8";
	rename -uid "F332A4F6-4A9B-A351-2C57-5AA2AB0E9310";
	setAttr -k off ".v";
	setAttr ".los" -type "double3" 0.001 0.001 0.001 ;
createNode transform -n "Curves_annotation3" -p "Curves_annotationLocator8";
	rename -uid "06330CED-486B-58F1-05BB-ABAFD745E8C0";
	setAttr -l on -k off -cb on ".v";
	setAttr -cb on ".t" -type "double3" 0.1863361647413676 -0.12766088178576715 0 ;
	setAttr -cb on ".t";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -cb on ".r";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -cb on ".s";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode annotationShape -n "Curves_annotationShape3" -p "|Curves_Three_Principle|Curves_Lip_Annotations|Curves_annotationLocator8|Curves_annotation3";
	rename -uid "173724BD-43E7-4792-E319-1487F072CDB4";
	setAttr -k off ".v";
	setAttr ".txt" -type "string" "L Brow Outer Corner";
createNode pointConstraint -n "Curves_annotationLocator8_pointConstraint1" -p "Curves_annotationLocator8";
	rename -uid "D97EE6D0-4B9E-515A-6763-C8B13A72E459";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "Curves_L_FlcW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 0.60001641511917103 4.0961188574328844e-07 0 ;
	setAttr -k on ".w0";
createNode transform -n "Curves_Brow_Annotations" -p "Curves_Three_Principle";
	rename -uid "24A03798-4F48-BB3D-167D-698712217BF1";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode transform -n "Curves_annotationLocator5" -p "Curves_Brow_Annotations";
	rename -uid "94152AED-4F9C-2AA6-B2D6-DF9CC50B8F10";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode locator -n "Curves_annotationLocator5Shape" -p "Curves_annotationLocator5";
	rename -uid "57984DBF-4045-374F-3DC4-AD9EC98F7383";
	setAttr -k off ".v";
	setAttr ".los" -type "double3" 0.001 0.001 0.001 ;
createNode transform -n "Curves_annotation3" -p "Curves_annotationLocator5";
	rename -uid "D04A3B1A-444D-8146-897E-1CA68F58ECE5";
	setAttr -l on -k off -cb on ".v";
	setAttr -cb on ".t" -type "double3" 0.055733916031058789 -0.39192627741318703 0 ;
	setAttr -cb on ".t";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -cb on ".r";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -cb on ".s";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode annotationShape -n "Curves_annotationShape3" -p "|Curves_Three_Principle|Curves_Brow_Annotations|Curves_annotationLocator5|Curves_annotation3";
	rename -uid "F47B672A-4C28-CC25-492B-50886140B48F";
	setAttr -k off ".v";
	setAttr ".txt" -type "string" "Left Brow Center";
createNode transform -n "Curves_annotationLocator6" -p "Curves_Brow_Annotations";
	rename -uid "38DD7DCF-47D6-E057-CE83-1F8B70ED85E2";
	setAttr -l on -k off -cb on ".v";
	setAttr -cb on ".t" -type "double3" -0.21297546334765671 0.49977763988448443 0 ;
	setAttr -cb on ".t";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -cb on ".r";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -cb on ".s";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode locator -n "Curves_annotationLocator6Shape" -p "Curves_annotationLocator6";
	rename -uid "D7BEF2AD-4D55-B1D6-E2E7-4084DC3CA04B";
	setAttr -k off ".v";
	setAttr ".los" -type "double3" 0.001 0.001 0.001 ;
createNode transform -n "Curves_annotation3" -p "Curves_annotationLocator6";
	rename -uid "D9B571BA-4351-A92A-92E3-8CB3258C0967";
	setAttr -l on -k off -cb on ".v";
	setAttr -cb on ".t" -type "double3" -0.21747517220955104 0.17055813338562764 0 ;
	setAttr -cb on ".t";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -cb on ".r";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -cb on ".s";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode annotationShape -n "Curves_annotationShape3" -p "|Curves_Three_Principle|Curves_Brow_Annotations|Curves_annotationLocator6|Curves_annotation3";
	rename -uid "F19C7552-4FD7-56A3-4E7B-A1BCC1C8479F";
	setAttr -k off ".v";
	setAttr ".txt" -type "string" "Brow High Position";
createNode transform -n "Curves_annotationLocator7" -p "Curves_Brow_Annotations";
	rename -uid "36B8EF95-48B6-3493-069F-C986C98F6AD1";
	setAttr -l on -k off -cb on ".v";
	setAttr -cb on ".t" -type "double3" -0.21475430668765494 -0.5 0 ;
	setAttr -cb on ".t";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -cb on ".r";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -cb on ".s";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode locator -n "Curves_annotationLocator7Shape" -p "Curves_annotationLocator7";
	rename -uid "4F26E9F2-4D8F-07D6-5303-7191C81919D1";
	setAttr -k off ".v";
	setAttr ".los" -type "double3" 0.001 0.001 0.001 ;
createNode transform -n "Curves_annotation3" -p "Curves_annotationLocator7";
	rename -uid "E60CEC44-4661-763F-D9DB-98ADF1C9906C";
	setAttr -l on -k off -cb on ".v";
	setAttr -cb on ".t" -type "double3" -0.10621871796686339 -0.25031904862076837 0 ;
	setAttr -cb on ".t";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -cb on ".r";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -cb on ".s";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode annotationShape -n "Curves_annotationShape3" -p "|Curves_Three_Principle|Curves_Brow_Annotations|Curves_annotationLocator7|Curves_annotation3";
	rename -uid "98D3144C-4C66-EF34-2499-0B9C36CBC31D";
	setAttr -k off ".v";
	setAttr ".txt" -type "string" "Brow Low Position (Almost at blink position)";
createNode transform -s -n "persp";
	rename -uid "ECDE042F-4D19-4949-C04B-B289B49BFD57";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 2.8650205615734405 1.2782846373781089 7.1936875480388309 ;
	setAttr ".r" -type "double3" -9.9383527296031779 23.400000000000205 0 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "2B76DACE-4ED0-ED58-6EDC-42B018742ED0";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 7.8695566816279854;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".tp" -type "double3" 0.17795097215166544 -0.039991637675328207 0 ;
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "AB4ADBAA-472D-3871-8807-778EB0553C2C";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -90 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "9D256540-4D25-1AAE-7418-EFB860A23968";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
createNode transform -s -n "front";
	rename -uid "CAB7F185-4887-5DF3-E939-FDB35E2087AD";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "83207C9D-4D49-452C-06C7-3EBE6BD2DD15";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
createNode transform -s -n "side";
	rename -uid "0B460462-4BCC-D6CC-03DD-88A1DB8D7D89";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 90 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "C729F337-4DA4-8BB0-42AE-9C98C2447DB1";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode distanceBetween -n "Curves_Top_Bot_distance";
	rename -uid "BD644C6A-4355-9637-B196-108E2E90A44D";
createNode nonLinear -n "bend1";
	rename -uid "0C8FB3C4-439F-514B-CFCC-85964BE774B8";
	addAttr -is true -ci true -k true -sn "cur" -ln "curvature" -smn -3.14159 -smx 
		3.14159 -at "doubleAngle";
	addAttr -is true -ci true -k true -sn "lb" -ln "lowBound" -dv -1 -max 0 -smn -10 
		-smx 0 -at "double";
	addAttr -is true -ci true -k true -sn "hb" -ln "highBound" -dv 1 -min 0 -smn 0 -smx 
		10 -at "double";
	setAttr -s 21 ".ip";
	setAttr -s 21 ".og";
	setAttr -k on ".cur" 91.673247220931728;
	setAttr -k on ".lb";
	setAttr -k on ".hb";
createNode objectSet -n "bend1Set";
	rename -uid "34722E3C-4890-8E96-3F10-D383D17B3E18";
	setAttr ".ihi" 0;
	setAttr -s 21 ".dsm";
	setAttr ".vo" yes;
	setAttr -s 21 ".gn";
createNode groupId -n "Three_Curve_Principle_groupId48";
	rename -uid "0E316AC9-4299-7D7D-BB50-CA8AEE3618C4";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId49";
	rename -uid "8FFF0446-4F55-5A62-3D15-99B290C1F63F";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId50";
	rename -uid "BCEB75BF-4E69-9A99-5980-1B9FF4BEC75A";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId53";
	rename -uid "884126D4-4C61-E243-0CF0-40994DB7A3D4";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId54";
	rename -uid "B60E6EB6-448A-FF3D-4C6F-4B881BFF921C";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId55";
	rename -uid "EE1CD931-4E55-A8BA-9673-B2BDBE38A815";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId57";
	rename -uid "9280CB3D-4667-F28E-E28C-949C0390C8FA";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId58";
	rename -uid "8FD7441B-480D-C3F8-2115-ADB58AAA619D";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId59";
	rename -uid "FE473EED-43EF-0AB0-DB5A-409AD96BD231";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId60";
	rename -uid "4A2BE4ED-4DB0-F53C-AF12-36A70E2B30F0";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId61";
	rename -uid "14FDE0C0-4952-87DB-A02F-BDB1298C45DE";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId62";
	rename -uid "C23AABCC-4328-1E00-35F0-0AADFF839FD5";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId63";
	rename -uid "1A147138-47EE-5F7D-247B-A388F4D6BFF4";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId81";
	rename -uid "6589377B-4622-ACD6-EA1F-37B3C36309B7";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId82";
	rename -uid "FD2EC242-4E87-A327-994D-398B5C8B6FC6";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId83";
	rename -uid "3A4B635F-412B-848A-7C85-7D9CB69D698E";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId84";
	rename -uid "1EABBBB8-404D-BCAC-9373-368ED14FD3EA";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId92";
	rename -uid "1235FF82-4100-C4E5-AC0C-A99BF8113E79";
	setAttr ".ihi" 0;
createNode groupId -n "groupId93";
	rename -uid "1AF16E61-4224-A53C-1312-80B296355A01";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId96";
	rename -uid "D6CA2BED-401E-93FB-8705-D5A3FFFDD368";
	setAttr ".ihi" 0;
createNode groupId -n "Three_Curve_Principle_groupId98";
	rename -uid "30B49069-4EB2-E6C9-723B-C5823E076696";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts48";
	rename -uid "84F09694-4378-83A6-211E-F2BB474AD2AA";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak25";
	rename -uid "7E53B0F2-47D9-4988-61CF-4E8F7649EF21";
createNode objectSet -n "Three_Curve_Principle_tweakSet25";
	rename -uid "8AFE83C5-4676-293B-1E65-78A32E055205";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Three_Curve_Principle_groupId65";
	rename -uid "B06EE3E4-46B7-4082-C750-3DA5F72568C5";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts65";
	rename -uid "FC604B8B-42BD-C94C-BD49-5B8E9AC483A5";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts49";
	rename -uid "9D74B9B7-4511-321B-4405-C4B5EC4004DE";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak26";
	rename -uid "8F0D6026-42F5-A2B8-0760-C1B6DBD82F83";
createNode objectSet -n "Three_Curve_Principle_tweakSet26";
	rename -uid "21597898-4DA1-9288-B3F6-19AD649F3DD5";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Three_Curve_Principle_groupId66";
	rename -uid "E1047128-4299-C391-E12F-9ABF4586DD33";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts66";
	rename -uid "039CB439-40C1-551E-BE12-31956A4ABEF1";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts50";
	rename -uid "E456A6E6-4E8B-3A54-384F-4796DA556213";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak27";
	rename -uid "943D920B-468B-A1D4-FAD6-1FBBC80CFA4B";
createNode objectSet -n "Three_Curve_Principle_tweakSet27";
	rename -uid "0B1F681E-479B-F56D-3C62-D394EDAA6F1A";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Three_Curve_Principle_groupId67";
	rename -uid "DC84785C-4265-46D9-5BCF-76930CC4DF6C";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts67";
	rename -uid "68354A72-4CF3-B88A-D06A-9A9377C51600";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts53";
	rename -uid "9530C229-47AB-1027-DA7E-CF8A1603B9B8";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak30";
	rename -uid "A2F557E1-462B-914B-6D49-6A8FCD989ED5";
createNode objectSet -n "Three_Curve_Principle_tweakSet30";
	rename -uid "2A7F461C-4202-B1ED-FE36-169D4C8F30EC";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Three_Curve_Principle_groupId70";
	rename -uid "E8BDC325-4A78-3056-F147-27A5033E14B9";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts70";
	rename -uid "2A13FF80-4A10-61B9-F18E-A4A0A354ADF8";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts54";
	rename -uid "85CF633E-4F5A-D4F6-F469-E883898E2DF9";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak31";
	rename -uid "6D0E8F9B-44FF-D47E-B695-A19CA5203AC8";
createNode objectSet -n "Three_Curve_Principle_tweakSet31";
	rename -uid "C7036D9B-47B9-72B6-0F65-A09C1DFC29E0";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Three_Curve_Principle_groupId71";
	rename -uid "F48E9617-43EF-DCD7-BCC9-12840F347400";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts71";
	rename -uid "33EA6EAA-45AC-5B25-567F-C2A13807BBE9";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts55";
	rename -uid "15F80B8E-43A7-D095-03AE-66BDE065136C";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak32";
	rename -uid "D942B859-49C9-3226-AFF0-95AA0CE39C8A";
createNode objectSet -n "Three_Curve_Principle_tweakSet32";
	rename -uid "084949D4-45A6-BACA-1DC8-FEA65DB85CA8";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Three_Curve_Principle_groupId72";
	rename -uid "D6769E94-43CF-3453-55CF-18B22414C0A9";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts72";
	rename -uid "77754587-4724-65F8-772D-B99A9704D2F2";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts57";
	rename -uid "AADB55F7-449D-79EE-00BD-3C86BEC2DCBA";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak34";
	rename -uid "D9DE060B-4E5E-CC4A-166A-C892C30DF78B";
createNode objectSet -n "Three_Curve_Principle_tweakSet34";
	rename -uid "32643659-4AF6-C8C0-9160-D09FAC90CB1C";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Three_Curve_Principle_groupId74";
	rename -uid "4F06E96B-44B7-981D-0C3E-F9BB3F388BFE";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts74";
	rename -uid "4376AE45-4C11-FD5C-EFB5-2E95C371543F";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts58";
	rename -uid "3DD669BC-4667-4DBB-E61E-03845451C6BC";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak35";
	rename -uid "758A0490-4BE2-C53E-63F9-0FACFD011A2A";
createNode objectSet -n "Three_Curve_Principle_tweakSet35";
	rename -uid "A97694E6-4ABB-3BD9-7407-B9A6F535C175";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Three_Curve_Principle_groupId75";
	rename -uid "561C36D3-4C64-1DFD-4202-3C916013593B";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts75";
	rename -uid "E68C590D-4139-EF0F-EEB3-919E67C150BD";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts59";
	rename -uid "E3E74040-43AA-5F42-0DF4-59A270682330";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak36";
	rename -uid "D105C356-4ED7-43B1-A42F-79AA6B800A6C";
createNode objectSet -n "Three_Curve_Principle_tweakSet36";
	rename -uid "9C09D3A3-4F83-4867-6E8E-419789B631A3";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Three_Curve_Principle_groupId76";
	rename -uid "9E0CF58F-4155-F561-C83B-7993EACDA85D";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts76";
	rename -uid "E9933AA0-4093-635C-2CD1-D495703E4D6C";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts60";
	rename -uid "8F4CE391-44E3-B98C-354C-8183C8FC4049";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak37";
	rename -uid "B34EF477-4D76-B192-7843-13850422A706";
createNode objectSet -n "Three_Curve_Principle_tweakSet37";
	rename -uid "38214392-4095-D618-29C1-6CBCF3631F67";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Three_Curve_Principle_groupId77";
	rename -uid "DF9D192F-4DF2-A474-82A0-C18E0A7E1AA4";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts77";
	rename -uid "AB92BCA5-45CF-615B-E30F-2C8EF0AB2228";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts61";
	rename -uid "058C8D99-42AA-17A8-352B-40B499890622";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak38";
	rename -uid "9AD4DCF0-4CD7-4006-232E-60AE5367EE51";
createNode objectSet -n "Three_Curve_Principle_tweakSet38";
	rename -uid "2A10B1E2-4283-53E3-105C-86AEAFBE6372";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Three_Curve_Principle_groupId78";
	rename -uid "B55F116A-4815-C931-92C8-379864A89F63";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts78";
	rename -uid "7250BE1F-4E8C-8451-B023-46B916FD99BD";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts62";
	rename -uid "42295000-43F3-B9B2-E6A7-15B932DD66CD";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak39";
	rename -uid "9F410CF3-4C17-5785-5E7E-73BE610E4B10";
createNode objectSet -n "Three_Curve_Principle_tweakSet39";
	rename -uid "1F142653-4F23-B08F-A062-5FAC1AA62E56";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Three_Curve_Principle_groupId79";
	rename -uid "EDA291FB-49AD-7798-04E1-D7B52D9E6E6C";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts79";
	rename -uid "1CA1EE87-4F5F-3621-A59C-018C5D063DCA";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts63";
	rename -uid "A6C479DE-475F-1F19-1575-118D81D526FB";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak40";
	rename -uid "A8258B13-46B4-8FBB-05DE-4487587A173B";
createNode objectSet -n "Three_Curve_Principle_tweakSet40";
	rename -uid "6EE29C03-47D9-FD83-F531-F8ACA36BFB8F";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Three_Curve_Principle_groupId80";
	rename -uid "82F62B64-404A-2BD3-F55B-75B8F3B47373";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts80";
	rename -uid "740AD706-4304-5D82-197E-5B9D9995243E";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts81";
	rename -uid "7232C0E2-440D-5594-09E0-8A94FA5C7488";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak41";
	rename -uid "95DEF6A4-4344-653F-3433-56A298066F1F";
createNode objectSet -n "Three_Curve_Principle_tweakSet41";
	rename -uid "C98EE0EA-4AAC-A70C-5778-FA89DE9F80A0";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Three_Curve_Principle_groupId85";
	rename -uid "376754C6-45D8-0726-7BDC-20BE93A1AD4B";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts85";
	rename -uid "2E6CDA0D-4FE8-0F54-E180-2295EE1E6738";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts82";
	rename -uid "19B54325-4893-9CA7-4B30-7C81BEB79343";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak42";
	rename -uid "AA3E7D55-4F5A-7F02-848F-668629308AA3";
createNode objectSet -n "Three_Curve_Principle_tweakSet42";
	rename -uid "36DFDD2D-4AB8-7960-9874-54A552A8A32A";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Three_Curve_Principle_groupId86";
	rename -uid "CCA830C0-4423-C5C5-1B71-FB80B21B3E0A";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts86";
	rename -uid "B71D04B4-4899-3859-1657-A490AE66A953";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts83";
	rename -uid "5C35EB14-42D3-9C7B-C98D-21BFEA1A2D37";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak43";
	rename -uid "D0DE7482-4C3C-F5ED-F919-558BC048D186";
createNode objectSet -n "Three_Curve_Principle_tweakSet43";
	rename -uid "A7CFDED5-494B-2CE8-95E0-2894A82752CA";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Three_Curve_Principle_groupId87";
	rename -uid "8203CB4E-4C09-9AB8-8DDF-3CAF262E8A89";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts87";
	rename -uid "2B177F5F-4271-4582-4ABA-F5AF3AE45578";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts84";
	rename -uid "2C564859-482E-77D5-7DC7-FC9942833D10";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak44";
	rename -uid "6812B913-41DC-BB5A-35EC-5F8275B9E68E";
createNode objectSet -n "Three_Curve_Principle_tweakSet44";
	rename -uid "BE398863-4559-37E1-E5AC-F5A94087A845";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Three_Curve_Principle_groupId88";
	rename -uid "703DF066-4ED2-693C-C1EF-13AB230360F5";
	setAttr ".ihi" 0;
createNode groupParts -n "groupParts88";
	rename -uid "58499504-4BB1-137B-E1F7-629D8CEC9B1E";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts91";
	rename -uid "04B78E41-4397-109A-E9E0-02BCB3660CAC";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[*]";
createNode tweak -n "Three_Curve_Principle_tweak45";
	rename -uid "A37DF2FD-4189-D409-3507-319F2912348F";
createNode objectSet -n "Three_Curve_Principle_tweakSet45";
	rename -uid "7A1B1D54-4D70-5AAD-ADF0-8E8616E7ED8B";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Three_Curve_Principle_groupId94";
	rename -uid "F94A287B-4A77-6AEC-48A3-C3B40EAF0144";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts93";
	rename -uid "B5A1AC53-4236-19BD-8D16-CB9FCBCF062D";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts89";
	rename -uid "3D4B9CE5-49D0-E7AD-7278-1A9329D236B3";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "f[0]";
createNode groupId -n "Three_Curve_Principle_groupId90";
	rename -uid "395FB304-42EF-516D-9040-F7888A3687CB";
	setAttr ".ihi" 0;
createNode groupParts -n "groupParts92";
	rename -uid "50D5C1AA-405D-CA5D-A6DE-708B16CE9FAA";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[*]";
createNode tweak -n "Three_Curve_Principle_tweak46";
	rename -uid "49604F21-4E8E-E257-BD67-E3A3FF9CBA22";
createNode objectSet -n "Three_Curve_Principle_tweakSet46";
	rename -uid "2998028C-4C41-E666-473B-9CBAD2AB9AED";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "groupId95";
	rename -uid "834F0AA1-473A-2A8F-AC97-4DA36787C88B";
	setAttr ".ihi" 0;
createNode groupParts -n "groupParts94";
	rename -uid "A8DE63CE-4840-800B-929A-989C4D4098A6";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[*]";
createNode groupParts -n "groupParts90";
	rename -uid "403F7CEC-46C4-71FA-1A21-498D52708878";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "f[0]";
createNode groupId -n "groupId91";
	rename -uid "1745ACD9-4795-83D0-317C-53A54D48E1AD";
	setAttr ".ihi" 0;
createNode groupParts -n "Three_Curve_Principle_groupParts95";
	rename -uid "7CAFC24B-4309-518D-167D-4B980294C3A3";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak47";
	rename -uid "CD1AF8B6-42A1-5983-563D-68AFC24961A0";
createNode objectSet -n "Three_Curve_Principle_tweakSet47";
	rename -uid "7057ABDD-4DCA-CEF1-7310-90B3537A9FA0";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "groupId97";
	rename -uid "D4385ECF-42C8-83F3-EB3F-8EB421A655BE";
	setAttr ".ihi" 0;
createNode groupParts -n "groupParts96";
	rename -uid "7B0A74BA-4B05-4CFF-0796-0BB7397F8615";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode groupParts -n "Three_Curve_Principle_groupParts97";
	rename -uid "6FDA4DB0-4E70-44AC-89C8-DEA36BB12CF8";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode tweak -n "Three_Curve_Principle_tweak48";
	rename -uid "34E9242E-4B82-B46C-B9CE-B092E3F876D4";
createNode objectSet -n "Three_Curve_Principle_tweakSet48";
	rename -uid "C8995B1E-424A-B615-BAE1-0CA180CA3774";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "groupId99";
	rename -uid "1C99BB89-45C4-D4C6-BC97-27B8DAD06DE9";
	setAttr ".ihi" 0;
createNode groupParts -n "groupParts98";
	rename -uid "4DF16AD1-4374-4161-0186-A68AFEB0F686";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*]";
createNode unitConversion -n "Three_Curve_Principle_unitConversion1";
	rename -uid "D9853A50-4E40-DE01-39F4-82BBA4A44FF5";
	setAttr ".cf" 0.017453292519943295;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "DB9FEA9A-493D-3EC1-2DF2-99B5AC6361C2";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "EE0232F5-4B53-E654-2847-1A88C59A588A";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "A852BD20-4B15-1283-F453-77BFBFBF997A";
createNode displayLayerManager -n "layerManager";
	rename -uid "614EB583-44EE-4362-CB02-899D1F3C63E9";
createNode displayLayer -n "defaultLayer";
	rename -uid "91303897-4495-FE53-C14B-5E82DC7403C8";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "CBCDC4E8-4155-B3DE-21A0-B995ECBE67D3";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "7546DA5B-47E4-FD1E-E0D7-2A8598DD83C1";
	setAttr ".g" yes;
createNode script -n "uiConfigurationScriptNode";
	rename -uid "77BD35E1-4D61-8CFF-7EE0-F1B1383A5210";
	setAttr ".b" -type "string" (
		"// Maya Mel UI Configuration File.\n//\n//  This script is machine generated.  Edit at your own risk.\n//\n//\n\nglobal string $gMainPane;\nif (`paneLayout -exists $gMainPane`) {\n\n\tglobal int $gUseScenePanelConfig;\n\tint    $useSceneConfig = $gUseScenePanelConfig;\n\tint    $nodeEditorPanelVisible = stringArrayContains(\"nodeEditorPanel1\", `getPanel -vis`);\n\tint    $nodeEditorWorkspaceControlOpen = (`workspaceControl -exists nodeEditorPanel1Window` && `workspaceControl -q -visible nodeEditorPanel1Window`);\n\tint    $menusOkayInPanels = `optionVar -q allowMenusInPanels`;\n\tint    $nVisPanes = `paneLayout -q -nvp $gMainPane`;\n\tint    $nPanes = 0;\n\tstring $editorName;\n\tstring $panelName;\n\tstring $itemFilterName;\n\tstring $panelConfig;\n\n\t//\n\t//  get current state of the UI\n\t//\n\tsceneUIReplacement -update $gMainPane;\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Top View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Top View\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"top\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n"
		+ "            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n"
		+ "            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Side View\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Side View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"side\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n"
		+ "            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n"
		+ "            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Front View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Front View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"front\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n"
		+ "            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n"
		+ "            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n"
		+ "            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Persp View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"persp\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n"
		+ "            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n"
		+ "            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n"
		+ "            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1581\n            -height 623\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"ToggledOutliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"ToggledOutliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -docTag \"isolOutln_fromSeln\" \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 1\n            -showReferenceMembers 1\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n"
		+ "            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -isSet 0\n            -isSetMember 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n"
		+ "            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -selectCommand \"print(\\\"\\\")\" \n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            -renderFilterIndex 0\n            -selectionOrder \"chronological\" \n            -expandAttribute 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"Outliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 0\n            -showReferenceMembers 0\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n"
		+ "            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"graphEditor\" (localizedPanelLabel(\"Graph Editor\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -organizeByClip 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showParentContainers 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n"
		+ "                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n"
		+ "                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 1\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 1\n                -autoFitTime 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -showResults \"off\" \n                -showBufferCurves \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -showCurveNames 0\n                -showActiveCurveNames 0\n"
		+ "                -stackedCurves 0\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -displayNormalized 0\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -classicMode 1\n                -valueLinesToggle 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dopeSheetPanel\" (localizedPanelLabel(\"Dope Sheet\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dope Sheet\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n"
		+ "                -showMuteInfo 0\n                -organizeByLayer 1\n                -organizeByClip 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 0\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showParentContainers 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 0\n                -showCompounds 1\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 1\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n"
		+ "                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"DopeSheetEd\");\n            dopeSheetEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n"
		+ "                -displayValues 0\n                -autoFit 0\n                -autoFitTime 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -outliner \"dopeSheetPanel1OutlineEd\" \n                -showSummary 1\n                -showScene 0\n                -hierarchyBelow 0\n                -showTicks 1\n                -selectionWindow 0 0 0 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"timeEditorPanel\" (localizedPanelLabel(\"Time Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Time Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"clipEditorPanel\" (localizedPanelLabel(\"Trax Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Trax Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\n\t\t\t$editorName = clipEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -autoFitTime 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"sequenceEditorPanel\" (localizedPanelLabel(\"Camera Sequencer\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Camera Sequencer\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = sequenceEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n"
		+ "                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -autoFitTime 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 1 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperGraphPanel\" (localizedPanelLabel(\"Hypergraph Hierarchy\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypergraph Hierarchy\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"HyperGraphEd\");\n            hyperGraph -e \n                -graphLayoutStyle \"hierarchicalLayout\" \n                -orientation \"horiz\" \n                -mergeConnections 0\n                -zoom 1\n                -animateTransition 0\n                -showRelationships 1\n"
		+ "                -showShapes 0\n                -showDeformers 0\n                -showExpressions 0\n                -showConstraints 0\n                -showConnectionFromSelected 0\n                -showConnectionToSelected 0\n                -showConstraintLabels 0\n                -showUnderworld 0\n                -showInvisible 0\n                -transitionFrames 1\n                -opaqueContainers 0\n                -freeform 0\n                -imagePosition 0 0 \n                -imageScale 1\n                -imageEnabled 0\n                -graphType \"DAG\" \n                -heatMapDisplay 0\n                -updateSelection 1\n                -updateNodeAdded 1\n                -useDrawOverrideColor 0\n                -limitGraphTraversal -1\n                -range 0 0 \n                -iconSize \"smallIcons\" \n                -showCachedConnections 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperShadePanel\" (localizedPanelLabel(\"Hypershade\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypershade\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"visorPanel\" (localizedPanelLabel(\"Visor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Visor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"nodeEditorPanel\" (localizedPanelLabel(\"Node Editor\")) `;\n\tif ($nodeEditorPanelVisible || $nodeEditorWorkspaceControlOpen) {\n\t\tif (\"\" == $panelName) {\n\t\t\tif ($useSceneConfig) {\n\t\t\t\t$panelName = `scriptedPanel -unParent  -type \"nodeEditorPanel\" -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n"
		+ "                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -connectNodeOnCreation 0\n                -connectOnDrop 0\n                -copyConnectionsOnPaste 0\n                -connectionStyle \"bezier\" \n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -crosshairOnEdgeDragging 0\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -editorMode \"default\" \n"
		+ "                -hasWatchpoint 0\n                $editorName;\n\t\t\t}\n\t\t} else {\n\t\t\t$label = `panel -q -label $panelName`;\n\t\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -connectNodeOnCreation 0\n                -connectOnDrop 0\n                -copyConnectionsOnPaste 0\n                -connectionStyle \"bezier\" \n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -crosshairOnEdgeDragging 0\n"
		+ "                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -editorMode \"default\" \n                -hasWatchpoint 0\n                $editorName;\n\t\t\tif (!$useSceneConfig) {\n\t\t\t\tpanel -e -l $label $panelName;\n\t\t\t}\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"createNodePanel\" (localizedPanelLabel(\"Create Node\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Create Node\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"polyTexturePlacementPanel\" (localizedPanelLabel(\"UV Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"UV Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"renderWindowPanel\" (localizedPanelLabel(\"Render View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Render View\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"shapePanel\" (localizedPanelLabel(\"Shape Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tshapePanel -edit -l (localizedPanelLabel(\"Shape Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"posePanel\" (localizedPanelLabel(\"Pose Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tposePanel -edit -l (localizedPanelLabel(\"Pose Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n"
		+ "\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynRelEdPanel\" (localizedPanelLabel(\"Dynamic Relationships\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dynamic Relationships\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"relationshipPanel\" (localizedPanelLabel(\"Relationship Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Relationship Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"referenceEditorPanel\" (localizedPanelLabel(\"Reference Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Reference Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"componentEditorPanel\" (localizedPanelLabel(\"Component Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Component Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynPaintScriptedPanelType\" (localizedPanelLabel(\"Paint Effects\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Paint Effects\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"scriptEditorPanel\" (localizedPanelLabel(\"Script Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Script Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"profilerPanel\" (localizedPanelLabel(\"Profiler Tool\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Profiler Tool\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"contentBrowserPanel\" (localizedPanelLabel(\"Content Browser\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Content Browser\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"Stereo\" (localizedPanelLabel(\"Stereo\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Stereo\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "{ string $editorName = ($panelName+\"Editor\");\n            stereoCameraView -e \n                -camera \"persp\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"smoothShaded\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -holdOuts 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 0\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 32768\n                -fogging 0\n                -fogSource \"fragment\" \n"
		+ "                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -depthOfFieldPreview 1\n                -maxConstantTransparency 1\n                -objectFilterShowInHUD 1\n                -isFiltered 0\n                -colorResolution 4 4 \n                -bumpResolution 4 4 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 0\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -controllers 1\n                -nurbsCurves 1\n"
		+ "                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -clipGhosts 1\n                -greasePencils 1\n                -shadows 0\n                -captureSequenceNumber -1\n"
		+ "                -width 0\n                -height 0\n                -sceneRenderFilter 0\n                -displayMode \"centerEye\" \n                -viewColor 0 0 0 1 \n                -useCustomBackground 1\n                $editorName;\n            stereoCameraView -e -viewSelected 0 $editorName; };\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\tif ($useSceneConfig) {\n        string $configName = `getPanel -cwl (localizedPanelLabel(\"Current Layout\"))`;\n        if (\"\" != $configName) {\n\t\t\tpanelConfiguration -edit -label (localizedPanelLabel(\"Current Layout\")) \n\t\t\t\t-userCreated false\n\t\t\t\t-defaultImage \"vacantCell.xP:/\"\n\t\t\t\t-image \"\"\n\t\t\t\t-sc false\n\t\t\t\t-configString \"global string $gMainPane; paneLayout -e -cn \\\"single\\\" -ps 1 100 100 $gMainPane;\"\n\t\t\t\t-removeAllPanels\n\t\t\t\t-ap false\n\t\t\t\t\t(localizedPanelLabel(\"Persp View\")) \n\t\t\t\t\t\"modelPanel\"\n"
		+ "\t\t\t\t\t\"$panelName = `modelPanel -unParent -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels `;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 32768\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1581\\n    -height 623\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName\"\n"
		+ "\t\t\t\t\t\"modelPanel -edit -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels  $panelName;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 32768\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1581\\n    -height 623\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName\"\n"
		+ "\t\t\t\t$configName;\n\n            setNamedPanelLayout (localizedPanelLabel(\"Current Layout\"));\n        }\n\n        panelHistory -e -clear mainPanelHistory;\n        sceneUIReplacement -clear;\n\t}\n\n\ngrid -spacing 5 -size 12 -divisions 5 -displayAxes yes -displayGridLines yes -displayDivisionLines yes -displayPerspectiveLabels no -displayOrthographicLabels no -displayAxesBold yes -perspectiveLabelPosition axis -orthographicLabelPosition edge;\nviewManip -drawCompass 0 -compassAngle 0 -frontParameters \"\" -homeParameters \"\" -selectionLockParameters \"\";\n}\n");
	setAttr ".st" 3;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "3BCB7998-46AF-8FF5-1296-5199161D1F66";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 120 -ast 1 -aet 200 ";
	setAttr ".st" 6;
select -ne :time1;
	setAttr ".o" 1;
	setAttr ".unw" 1;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".msaa" yes;
	setAttr ".laa" yes;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 4 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderUtilityList1;
select -ne :defaultRenderingList1;
select -ne :initialShadingGroup;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
	setAttr -s 2 ".gn";
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :defaultColorMgtGlobals;
	setAttr ".cfe" yes;
	setAttr ".cfp" -type "string" "G:/Pipeline/ocio/aces_1.2/config.ocio";
	setAttr ".vtn" -type "string" "sRGB (ACES)";
	setAttr ".wsn" -type "string" "ACES - ACEScg";
	setAttr ".otn" -type "string" "sRGB (ACES)";
	setAttr ".potn" -type "string" "sRGB (ACES)";
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "Curves_Three_Principle.sx" "Curves_Three_Principle.sz" -l on;
connectAttr "Curves_Three_Principle.circle_vis" "Curves_Circles_Grp.v" -l on;
connectAttr "Curves_Top_Bot_distance.d" "Curves_R_circle_Grp.sx" -l on;
connectAttr "Curves_Top_Bot_distance.d" "Curves_R_circle_Grp.sy" -l on;
connectAttr "Curves_Top_Bot_distance.d" "Curves_R_circle_Grp.sz" -l on;
connectAttr "Curves_nurbsCircle1_parentConstraint1.ctx" "Curves_R_circle_Grp.tx"
		 -l on;
connectAttr "Curves_nurbsCircle1_parentConstraint1.cty" "Curves_R_circle_Grp.ty"
		 -l on;
connectAttr "Curves_nurbsCircle1_parentConstraint1.ctz" "Curves_R_circle_Grp.tz"
		 -l on;
connectAttr "Curves_nurbsCircle1_parentConstraint1.crx" "Curves_R_circle_Grp.rx"
		 -l on;
connectAttr "Curves_nurbsCircle1_parentConstraint1.cry" "Curves_R_circle_Grp.ry"
		 -l on;
connectAttr "Curves_nurbsCircle1_parentConstraint1.crz" "Curves_R_circle_Grp.rz"
		 -l on;
connectAttr "Curves_R_circle_Grp.ro" "Curves_nurbsCircle1_parentConstraint1.cro"
		;
connectAttr "Curves_R_circle_Grp.pim" "Curves_nurbsCircle1_parentConstraint1.cpim"
		;
connectAttr "Curves_R_circle_Grp.rp" "Curves_nurbsCircle1_parentConstraint1.crp"
		;
connectAttr "Curves_R_circle_Grp.rpt" "Curves_nurbsCircle1_parentConstraint1.crt"
		;
connectAttr "Curves_R_Flc.t" "Curves_nurbsCircle1_parentConstraint1.tg[0].tt";
connectAttr "Curves_R_Flc.rp" "Curves_nurbsCircle1_parentConstraint1.tg[0].trp";
connectAttr "Curves_R_Flc.rpt" "Curves_nurbsCircle1_parentConstraint1.tg[0].trt"
		;
connectAttr "Curves_R_Flc.r" "Curves_nurbsCircle1_parentConstraint1.tg[0].tr";
connectAttr "Curves_R_Flc.ro" "Curves_nurbsCircle1_parentConstraint1.tg[0].tro";
connectAttr "Curves_R_Flc.s" "Curves_nurbsCircle1_parentConstraint1.tg[0].ts";
connectAttr "Curves_R_Flc.pm" "Curves_nurbsCircle1_parentConstraint1.tg[0].tpm";
connectAttr "Curves_nurbsCircle1_parentConstraint1.w0" "Curves_nurbsCircle1_parentConstraint1.tg[0].tw"
		;
connectAttr "Curves_Top_Bot_distance.d" "Curves_C_circle_Grp.sx" -l on;
connectAttr "Curves_Top_Bot_distance.d" "Curves_C_circle_Grp.sy" -l on;
connectAttr "Curves_Top_Bot_distance.d" "Curves_C_circle_Grp.sz" -l on;
connectAttr "Curves_nurbsCircle3_parentConstraint1.ctx" "Curves_C_circle_Grp.tx"
		 -l on;
connectAttr "Curves_nurbsCircle3_parentConstraint1.cty" "Curves_C_circle_Grp.ty"
		 -l on;
connectAttr "Curves_nurbsCircle3_parentConstraint1.ctz" "Curves_C_circle_Grp.tz"
		 -l on;
connectAttr "Curves_nurbsCircle3_parentConstraint1.crx" "Curves_C_circle_Grp.rx"
		 -l on;
connectAttr "Curves_nurbsCircle3_parentConstraint1.cry" "Curves_C_circle_Grp.ry"
		 -l on;
connectAttr "Curves_nurbsCircle3_parentConstraint1.crz" "Curves_C_circle_Grp.rz"
		 -l on;
connectAttr "Curves_C_circle_Grp.ro" "Curves_nurbsCircle3_parentConstraint1.cro"
		;
connectAttr "Curves_C_circle_Grp.pim" "Curves_nurbsCircle3_parentConstraint1.cpim"
		;
connectAttr "Curves_C_circle_Grp.rp" "Curves_nurbsCircle3_parentConstraint1.crp"
		;
connectAttr "Curves_C_circle_Grp.rpt" "Curves_nurbsCircle3_parentConstraint1.crt"
		;
connectAttr "Curves_Three_Principle.t" "Curves_nurbsCircle3_parentConstraint1.tg[0].tt"
		;
connectAttr "Curves_Three_Principle.rp" "Curves_nurbsCircle3_parentConstraint1.tg[0].trp"
		;
connectAttr "Curves_Three_Principle.rpt" "Curves_nurbsCircle3_parentConstraint1.tg[0].trt"
		;
connectAttr "Curves_Three_Principle.r" "Curves_nurbsCircle3_parentConstraint1.tg[0].tr"
		;
connectAttr "Curves_Three_Principle.ro" "Curves_nurbsCircle3_parentConstraint1.tg[0].tro"
		;
connectAttr "Curves_Three_Principle.s" "Curves_nurbsCircle3_parentConstraint1.tg[0].ts"
		;
connectAttr "Curves_Three_Principle.pm" "Curves_nurbsCircle3_parentConstraint1.tg[0].tpm"
		;
connectAttr "Curves_nurbsCircle3_parentConstraint1.w0" "Curves_nurbsCircle3_parentConstraint1.tg[0].tw"
		;
connectAttr "Curves_Top_Bot_distance.d" "Curves_L_circle_Grp.sx" -l on;
connectAttr "Curves_Top_Bot_distance.d" "Curves_L_circle_Grp.sy" -l on;
connectAttr "Curves_Top_Bot_distance.d" "Curves_L_circle_Grp.sz" -l on;
connectAttr "Curves_nurbsCircle2_parentConstraint1.ctx" "Curves_L_circle_Grp.tx"
		 -l on;
connectAttr "Curves_nurbsCircle2_parentConstraint1.cty" "Curves_L_circle_Grp.ty"
		 -l on;
connectAttr "Curves_nurbsCircle2_parentConstraint1.ctz" "Curves_L_circle_Grp.tz"
		 -l on;
connectAttr "Curves_nurbsCircle2_parentConstraint1.crx" "Curves_L_circle_Grp.rx"
		 -l on;
connectAttr "Curves_nurbsCircle2_parentConstraint1.cry" "Curves_L_circle_Grp.ry"
		 -l on;
connectAttr "Curves_nurbsCircle2_parentConstraint1.crz" "Curves_L_circle_Grp.rz"
		 -l on;
connectAttr "Curves_L_circle_Grp.ro" "Curves_nurbsCircle2_parentConstraint1.cro"
		;
connectAttr "Curves_L_circle_Grp.pim" "Curves_nurbsCircle2_parentConstraint1.cpim"
		;
connectAttr "Curves_L_circle_Grp.rp" "Curves_nurbsCircle2_parentConstraint1.crp"
		;
connectAttr "Curves_L_circle_Grp.rpt" "Curves_nurbsCircle2_parentConstraint1.crt"
		;
connectAttr "Curves_L_Flc.t" "Curves_nurbsCircle2_parentConstraint1.tg[0].tt";
connectAttr "Curves_L_Flc.rp" "Curves_nurbsCircle2_parentConstraint1.tg[0].trp";
connectAttr "Curves_L_Flc.rpt" "Curves_nurbsCircle2_parentConstraint1.tg[0].trt"
		;
connectAttr "Curves_L_Flc.r" "Curves_nurbsCircle2_parentConstraint1.tg[0].tr";
connectAttr "Curves_L_Flc.ro" "Curves_nurbsCircle2_parentConstraint1.tg[0].tro";
connectAttr "Curves_L_Flc.s" "Curves_nurbsCircle2_parentConstraint1.tg[0].ts";
connectAttr "Curves_L_Flc.pm" "Curves_nurbsCircle2_parentConstraint1.tg[0].tpm";
connectAttr "Curves_nurbsCircle2_parentConstraint1.w0" "Curves_nurbsCircle2_parentConstraint1.tg[0].tw"
		;
connectAttr "Curves_L_circle_Grp.sx" "Curves_L_In_circle_Grp.sx" -l on;
connectAttr "Curves_L_circle_Grp.sy" "Curves_L_In_circle_Grp.sy" -l on;
connectAttr "Curves_L_circle_Grp.sz" "Curves_L_In_circle_Grp.sz" -l on;
connectAttr "Curves_L_In_circle_Grp_parentConstraint1.ctx" "Curves_L_In_circle_Grp.tx"
		 -l on;
connectAttr "Curves_L_In_circle_Grp_parentConstraint1.cty" "Curves_L_In_circle_Grp.ty"
		 -l on;
connectAttr "Curves_L_In_circle_Grp_parentConstraint1.ctz" "Curves_L_In_circle_Grp.tz"
		 -l on;
connectAttr "Curves_L_In_circle_Grp_parentConstraint1.crx" "Curves_L_In_circle_Grp.rx"
		 -l on;
connectAttr "Curves_L_In_circle_Grp_parentConstraint1.cry" "Curves_L_In_circle_Grp.ry"
		 -l on;
connectAttr "Curves_L_In_circle_Grp_parentConstraint1.crz" "Curves_L_In_circle_Grp.rz"
		 -l on;
connectAttr "bend1.og[47]" "Curves_L_In_circleShape.cr";
connectAttr "Three_Curve_Principle_tweak47.pl[0].cp[0]" "Curves_L_In_circleShape.twl"
		;
connectAttr "Three_Curve_Principle_groupId96.id" "Curves_L_In_circleShape.iog.og[2].gid"
		;
connectAttr "bend1Set.mwc" "Curves_L_In_circleShape.iog.og[2].gco";
connectAttr "groupId97.id" "Curves_L_In_circleShape.iog.og[3].gid";
connectAttr "Three_Curve_Principle_tweakSet47.mwc" "Curves_L_In_circleShape.iog.og[3].gco"
		;
connectAttr "Curves_L_In_circle_Grp.ro" "Curves_L_In_circle_Grp_parentConstraint1.cro"
		;
connectAttr "Curves_L_In_circle_Grp.pim" "Curves_L_In_circle_Grp_parentConstraint1.cpim"
		;
connectAttr "Curves_L_In_circle_Grp.rp" "Curves_L_In_circle_Grp_parentConstraint1.crp"
		;
connectAttr "Curves_L_In_circle_Grp.rpt" "Curves_L_In_circle_Grp_parentConstraint1.crt"
		;
connectAttr "Curves_Three_Principle.t" "Curves_L_In_circle_Grp_parentConstraint1.tg[0].tt"
		;
connectAttr "Curves_Three_Principle.rp" "Curves_L_In_circle_Grp_parentConstraint1.tg[0].trp"
		;
connectAttr "Curves_Three_Principle.rpt" "Curves_L_In_circle_Grp_parentConstraint1.tg[0].trt"
		;
connectAttr "Curves_Three_Principle.r" "Curves_L_In_circle_Grp_parentConstraint1.tg[0].tr"
		;
connectAttr "Curves_Three_Principle.ro" "Curves_L_In_circle_Grp_parentConstraint1.tg[0].tro"
		;
connectAttr "Curves_Three_Principle.s" "Curves_L_In_circle_Grp_parentConstraint1.tg[0].ts"
		;
connectAttr "Curves_Three_Principle.pm" "Curves_L_In_circle_Grp_parentConstraint1.tg[0].tpm"
		;
connectAttr "Curves_L_In_circle_Grp_parentConstraint1.w0" "Curves_L_In_circle_Grp_parentConstraint1.tg[0].tw"
		;
connectAttr "Curves_R_circle_Grp.sx" "Curves_R_In_circle_Grp.sx" -l on;
connectAttr "Curves_R_circle_Grp.sy" "Curves_R_In_circle_Grp.sy" -l on;
connectAttr "Curves_R_circle_Grp.sz" "Curves_R_In_circle_Grp.sz" -l on;
connectAttr "Curves_R_In_circle_Grp_parentConstraint1.ctx" "Curves_R_In_circle_Grp.tx"
		 -l on;
connectAttr "Curves_R_In_circle_Grp_parentConstraint1.cty" "Curves_R_In_circle_Grp.ty"
		 -l on;
connectAttr "Curves_R_In_circle_Grp_parentConstraint1.ctz" "Curves_R_In_circle_Grp.tz"
		 -l on;
connectAttr "Curves_R_In_circle_Grp_parentConstraint1.crx" "Curves_R_In_circle_Grp.rx"
		 -l on;
connectAttr "Curves_R_In_circle_Grp_parentConstraint1.cry" "Curves_R_In_circle_Grp.ry"
		 -l on;
connectAttr "Curves_R_In_circle_Grp_parentConstraint1.crz" "Curves_R_In_circle_Grp.rz"
		 -l on;
connectAttr "bend1.og[48]" "Curves_R_In_circleShape.cr";
connectAttr "Three_Curve_Principle_tweak48.pl[0].cp[0]" "Curves_R_In_circleShape.twl"
		;
connectAttr "Three_Curve_Principle_groupId98.id" "Curves_R_In_circleShape.iog.og[4].gid"
		;
connectAttr "bend1Set.mwc" "Curves_R_In_circleShape.iog.og[4].gco";
connectAttr "groupId99.id" "Curves_R_In_circleShape.iog.og[5].gid";
connectAttr "Three_Curve_Principle_tweakSet48.mwc" "Curves_R_In_circleShape.iog.og[5].gco"
		;
connectAttr "Curves_R_In_circle_Grp.ro" "Curves_R_In_circle_Grp_parentConstraint1.cro"
		;
connectAttr "Curves_R_In_circle_Grp.pim" "Curves_R_In_circle_Grp_parentConstraint1.cpim"
		;
connectAttr "Curves_R_In_circle_Grp.rp" "Curves_R_In_circle_Grp_parentConstraint1.crp"
		;
connectAttr "Curves_R_In_circle_Grp.rpt" "Curves_R_In_circle_Grp_parentConstraint1.crt"
		;
connectAttr "Curves_Three_Principle.t" "Curves_R_In_circle_Grp_parentConstraint1.tg[0].tt"
		;
connectAttr "Curves_Three_Principle.rp" "Curves_R_In_circle_Grp_parentConstraint1.tg[0].trp"
		;
connectAttr "Curves_Three_Principle.rpt" "Curves_R_In_circle_Grp_parentConstraint1.tg[0].trt"
		;
connectAttr "Curves_Three_Principle.r" "Curves_R_In_circle_Grp_parentConstraint1.tg[0].tr"
		;
connectAttr "Curves_Three_Principle.ro" "Curves_R_In_circle_Grp_parentConstraint1.tg[0].tro"
		;
connectAttr "Curves_Three_Principle.s" "Curves_R_In_circle_Grp_parentConstraint1.tg[0].ts"
		;
connectAttr "Curves_Three_Principle.pm" "Curves_R_In_circle_Grp_parentConstraint1.tg[0].tpm"
		;
connectAttr "Curves_R_In_circle_Grp_parentConstraint1.w0" "Curves_R_In_circle_Grp_parentConstraint1.tg[0].tw"
		;
connectAttr "Curves_Three_Principle.straight_vis" "Curves_Straight_Grp.v" -l on;
connectAttr "bend1.og[39]" "Curves_NeutralShape.cr";
connectAttr "Three_Curve_Principle_tweak40.pl[0].cp[0]" "Curves_NeutralShape.twl"
		;
connectAttr "Three_Curve_Principle_groupId63.id" "Curves_NeutralShape.iog.og[2].gid"
		;
connectAttr "bend1Set.mwc" "Curves_NeutralShape.iog.og[2].gco";
connectAttr "Three_Curve_Principle_groupId80.id" "Curves_NeutralShape.iog.og[3].gid"
		;
connectAttr "Three_Curve_Principle_tweakSet40.mwc" "Curves_NeutralShape.iog.og[3].gco"
		;
connectAttr "bend1.og[38]" "Curves_UpShape.cr";
connectAttr "Three_Curve_Principle_tweak39.pl[0].cp[0]" "Curves_UpShape.twl";
connectAttr "Three_Curve_Principle_groupId62.id" "Curves_UpShape.iog.og[2].gid";
connectAttr "bend1Set.mwc" "Curves_UpShape.iog.og[2].gco";
connectAttr "Three_Curve_Principle_groupId79.id" "Curves_UpShape.iog.og[3].gid";
connectAttr "Three_Curve_Principle_tweakSet39.mwc" "Curves_UpShape.iog.og[3].gco"
		;
connectAttr "bend1.og[37]" "Curves_DownShape.cr";
connectAttr "Three_Curve_Principle_tweak38.pl[0].cp[0]" "Curves_DownShape.twl";
connectAttr "Three_Curve_Principle_groupId61.id" "Curves_DownShape.iog.og[2].gid"
		;
connectAttr "bend1Set.mwc" "Curves_DownShape.iog.og[2].gco";
connectAttr "Three_Curve_Principle_groupId78.id" "Curves_DownShape.iog.og[3].gid"
		;
connectAttr "Three_Curve_Principle_tweakSet38.mwc" "Curves_DownShape.iog.og[3].gco"
		;
connectAttr "Curves_Three_Principle.x_vis" "Curves_X_Grp.v" -l on;
connectAttr "bend1.og[33]" "Curves_Out_Up_LinearShape.cr";
connectAttr "Three_Curve_Principle_tweak34.pl[0].cp[0]" "Curves_Out_Up_LinearShape.twl"
		;
connectAttr "Three_Curve_Principle_groupId57.id" "Curves_Out_Up_LinearShape.iog.og[2].gid"
		;
connectAttr "bend1Set.mwc" "Curves_Out_Up_LinearShape.iog.og[2].gco";
connectAttr "Three_Curve_Principle_groupId74.id" "Curves_Out_Up_LinearShape.iog.og[3].gid"
		;
connectAttr "Three_Curve_Principle_tweakSet34.mwc" "Curves_Out_Up_LinearShape.iog.og[3].gco"
		;
connectAttr "bend1.og[36]" "Curves_Inn_Up_LinearShape.cr";
connectAttr "Three_Curve_Principle_tweak37.pl[0].cp[0]" "Curves_Inn_Up_LinearShape.twl"
		;
connectAttr "Three_Curve_Principle_groupId60.id" "Curves_Inn_Up_LinearShape.iog.og[2].gid"
		;
connectAttr "bend1Set.mwc" "Curves_Inn_Up_LinearShape.iog.og[2].gco";
connectAttr "Three_Curve_Principle_groupId77.id" "Curves_Inn_Up_LinearShape.iog.og[3].gid"
		;
connectAttr "Three_Curve_Principle_tweakSet37.mwc" "Curves_Inn_Up_LinearShape.iog.og[3].gco"
		;
connectAttr "bend1.og[35]" "Curves_Inn_Down_LinearShape.cr";
connectAttr "Three_Curve_Principle_tweak36.pl[0].cp[0]" "Curves_Inn_Down_LinearShape.twl"
		;
connectAttr "Three_Curve_Principle_groupId59.id" "Curves_Inn_Down_LinearShape.iog.og[2].gid"
		;
connectAttr "bend1Set.mwc" "Curves_Inn_Down_LinearShape.iog.og[2].gco";
connectAttr "Three_Curve_Principle_groupId76.id" "Curves_Inn_Down_LinearShape.iog.og[3].gid"
		;
connectAttr "Three_Curve_Principle_tweakSet36.mwc" "Curves_Inn_Down_LinearShape.iog.og[3].gco"
		;
connectAttr "bend1.og[34]" "Curves_Out_Down_LinearShape.cr";
connectAttr "Three_Curve_Principle_tweak35.pl[0].cp[0]" "Curves_Out_Down_LinearShape.twl"
		;
connectAttr "Three_Curve_Principle_groupId58.id" "Curves_Out_Down_LinearShape.iog.og[2].gid"
		;
connectAttr "bend1Set.mwc" "Curves_Out_Down_LinearShape.iog.og[2].gco";
connectAttr "Three_Curve_Principle_groupId75.id" "Curves_Out_Down_LinearShape.iog.og[3].gid"
		;
connectAttr "Three_Curve_Principle_tweakSet35.mwc" "Curves_Out_Down_LinearShape.iog.og[3].gco"
		;
connectAttr "Curves_Three_Principle.up_crv_vis" "Curves_Up_Grp.v" -l on;
connectAttr "bend1.og[40]" "Curves_Neutral1Shape.cr";
connectAttr "Three_Curve_Principle_tweak41.pl[0].cp[0]" "Curves_Neutral1Shape.twl"
		;
connectAttr "Three_Curve_Principle_groupId81.id" "Curves_Neutral1Shape.iog.og[6].gid"
		;
connectAttr "bend1Set.mwc" "Curves_Neutral1Shape.iog.og[6].gco";
connectAttr "Three_Curve_Principle_groupId85.id" "Curves_Neutral1Shape.iog.og[7].gid"
		;
connectAttr "Three_Curve_Principle_tweakSet41.mwc" "Curves_Neutral1Shape.iog.og[7].gco"
		;
connectAttr "bend1.og[41]" "Curves_Neutral3Shape.cr";
connectAttr "Three_Curve_Principle_tweak42.pl[0].cp[0]" "Curves_Neutral3Shape.twl"
		;
connectAttr "Three_Curve_Principle_groupId82.id" "Curves_Neutral3Shape.iog.og[6].gid"
		;
connectAttr "bend1Set.mwc" "Curves_Neutral3Shape.iog.og[6].gco";
connectAttr "Three_Curve_Principle_groupId86.id" "Curves_Neutral3Shape.iog.og[7].gid"
		;
connectAttr "Three_Curve_Principle_tweakSet42.mwc" "Curves_Neutral3Shape.iog.og[7].gco"
		;
connectAttr "Curves_Three_Principle.low_crv_vis" "Curves_Down_Grp.v" -l on;
connectAttr "bend1.og[43]" "Curves_Neutral2Shape.cr";
connectAttr "Three_Curve_Principle_tweak44.pl[0].cp[0]" "Curves_Neutral2Shape.twl"
		;
connectAttr "Three_Curve_Principle_groupId84.id" "Curves_Neutral2Shape.iog.og[6].gid"
		;
connectAttr "bend1Set.mwc" "Curves_Neutral2Shape.iog.og[6].gco";
connectAttr "Three_Curve_Principle_groupId88.id" "Curves_Neutral2Shape.iog.og[7].gid"
		;
connectAttr "Three_Curve_Principle_tweakSet44.mwc" "Curves_Neutral2Shape.iog.og[7].gco"
		;
connectAttr "bend1.og[42]" "Curves_Neutral4Shape.cr";
connectAttr "Three_Curve_Principle_tweak43.pl[0].cp[0]" "Curves_Neutral4Shape.twl"
		;
connectAttr "Three_Curve_Principle_groupId83.id" "Curves_Neutral4Shape.iog.og[6].gid"
		;
connectAttr "bend1Set.mwc" "Curves_Neutral4Shape.iog.og[6].gco";
connectAttr "Three_Curve_Principle_groupId87.id" "Curves_Neutral4Shape.iog.og[7].gid"
		;
connectAttr "Three_Curve_Principle_tweakSet43.mwc" "Curves_Neutral4Shape.iog.og[7].gco"
		;
connectAttr "Curves_Three_Principle.Up_Sub_Crv_Vis" "Curves_Up_Sub_Grp.v";
connectAttr "bend1.og[26]" "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Inn_Up1|Curves_Inn_Up1Shape.cr"
		;
connectAttr "Three_Curve_Principle_tweak27.pl[0].cp[0]" "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Inn_Up1|Curves_Inn_Up1Shape.twl"
		;
connectAttr "Three_Curve_Principle_groupId50.id" "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Inn_Up1|Curves_Inn_Up1Shape.iog.og[2].gid"
		;
connectAttr "bend1Set.mwc" "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Inn_Up1|Curves_Inn_Up1Shape.iog.og[2].gco"
		;
connectAttr "Three_Curve_Principle_groupId67.id" "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Inn_Up1|Curves_Inn_Up1Shape.iog.og[3].gid"
		;
connectAttr "Three_Curve_Principle_tweakSet27.mwc" "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Inn_Up1|Curves_Inn_Up1Shape.iog.og[3].gco"
		;
connectAttr "bend1.og[25]" "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Mid_Up|Curves_Mid_UpShape.cr"
		;
connectAttr "Three_Curve_Principle_tweak26.pl[0].cp[0]" "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Mid_Up|Curves_Mid_UpShape.twl"
		;
connectAttr "Three_Curve_Principle_groupId49.id" "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Mid_Up|Curves_Mid_UpShape.iog.og[2].gid"
		;
connectAttr "bend1Set.mwc" "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Mid_Up|Curves_Mid_UpShape.iog.og[2].gco"
		;
connectAttr "Three_Curve_Principle_groupId66.id" "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Mid_Up|Curves_Mid_UpShape.iog.og[3].gid"
		;
connectAttr "Three_Curve_Principle_tweakSet26.mwc" "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Mid_Up|Curves_Mid_UpShape.iog.og[3].gco"
		;
connectAttr "bend1.og[24]" "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Out_Up2|Curves_Out_Up2Shape.cr"
		;
connectAttr "Three_Curve_Principle_tweak25.pl[0].cp[0]" "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Out_Up2|Curves_Out_Up2Shape.twl"
		;
connectAttr "Three_Curve_Principle_groupId48.id" "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Out_Up2|Curves_Out_Up2Shape.iog.og[2].gid"
		;
connectAttr "bend1Set.mwc" "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Out_Up2|Curves_Out_Up2Shape.iog.og[2].gco"
		;
connectAttr "Three_Curve_Principle_groupId65.id" "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Out_Up2|Curves_Out_Up2Shape.iog.og[3].gid"
		;
connectAttr "Three_Curve_Principle_tweakSet25.mwc" "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Out_Up2|Curves_Out_Up2Shape.iog.og[3].gco"
		;
connectAttr "Curves_Three_Principle.Low_Sub_Crv_Vis" "Curves_Down_Sub_Grp.v";
connectAttr "bend1.og[29]" "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Out_Up2|Curves_Out_Up2Shape.cr"
		;
connectAttr "Three_Curve_Principle_tweak30.pl[0].cp[0]" "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Out_Up2|Curves_Out_Up2Shape.twl"
		;
connectAttr "Three_Curve_Principle_groupId53.id" "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Out_Up2|Curves_Out_Up2Shape.iog.og[2].gid"
		;
connectAttr "bend1Set.mwc" "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Out_Up2|Curves_Out_Up2Shape.iog.og[2].gco"
		;
connectAttr "Three_Curve_Principle_groupId70.id" "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Out_Up2|Curves_Out_Up2Shape.iog.og[3].gid"
		;
connectAttr "Three_Curve_Principle_tweakSet30.mwc" "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Out_Up2|Curves_Out_Up2Shape.iog.og[3].gco"
		;
connectAttr "bend1.og[31]" "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Inn_Up1|Curves_Inn_Up1Shape.cr"
		;
connectAttr "Three_Curve_Principle_tweak32.pl[0].cp[0]" "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Inn_Up1|Curves_Inn_Up1Shape.twl"
		;
connectAttr "Three_Curve_Principle_groupId55.id" "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Inn_Up1|Curves_Inn_Up1Shape.iog.og[2].gid"
		;
connectAttr "bend1Set.mwc" "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Inn_Up1|Curves_Inn_Up1Shape.iog.og[2].gco"
		;
connectAttr "Three_Curve_Principle_groupId72.id" "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Inn_Up1|Curves_Inn_Up1Shape.iog.og[3].gid"
		;
connectAttr "Three_Curve_Principle_tweakSet32.mwc" "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Inn_Up1|Curves_Inn_Up1Shape.iog.og[3].gco"
		;
connectAttr "bend1.og[30]" "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Mid_Up|Curves_Mid_UpShape.cr"
		;
connectAttr "Three_Curve_Principle_tweak31.pl[0].cp[0]" "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Mid_Up|Curves_Mid_UpShape.twl"
		;
connectAttr "Three_Curve_Principle_groupId54.id" "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Mid_Up|Curves_Mid_UpShape.iog.og[2].gid"
		;
connectAttr "bend1Set.mwc" "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Mid_Up|Curves_Mid_UpShape.iog.og[2].gco"
		;
connectAttr "Three_Curve_Principle_groupId71.id" "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Mid_Up|Curves_Mid_UpShape.iog.og[3].gid"
		;
connectAttr "Three_Curve_Principle_tweakSet31.mwc" "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Mid_Up|Curves_Mid_UpShape.iog.og[3].gco"
		;
connectAttr "bend1.msg" "Curves_BendHandle.sml";
connectAttr "Three_Curve_Principle_unitConversion1.o" "Curves_BendHandleShape.cur"
		;
connectAttr "bend1.lb" "Curves_BendHandleShape.lb";
connectAttr "bend1.hb" "Curves_BendHandleShape.hb";
connectAttr "bend1.og[45]" "Curves_L_Flc_SurfShape.i";
connectAttr "groupId91.id" "Curves_L_Flc_SurfShape.iog.og[0].gid";
connectAttr ":initialShadingGroup.mwc" "Curves_L_Flc_SurfShape.iog.og[0].gco";
connectAttr "groupId93.id" "Curves_L_Flc_SurfShape.iog.og[1].gid";
connectAttr "bend1Set.mwc" "Curves_L_Flc_SurfShape.iog.og[1].gco";
connectAttr "groupId95.id" "Curves_L_Flc_SurfShape.iog.og[2].gid";
connectAttr "Three_Curve_Principle_tweakSet46.mwc" "Curves_L_Flc_SurfShape.iog.og[2].gco"
		;
connectAttr "Three_Curve_Principle_tweak46.vl[0].vt[0]" "Curves_L_Flc_SurfShape.twl"
		;
connectAttr "bend1.og[44]" "Curves_R_Flc_SurfShape.i";
connectAttr "Three_Curve_Principle_groupId90.id" "Curves_R_Flc_SurfShape.iog.og[0].gid"
		;
connectAttr ":initialShadingGroup.mwc" "Curves_R_Flc_SurfShape.iog.og[0].gco";
connectAttr "Three_Curve_Principle_groupId92.id" "Curves_R_Flc_SurfShape.iog.og[1].gid"
		;
connectAttr "bend1Set.mwc" "Curves_R_Flc_SurfShape.iog.og[1].gco";
connectAttr "Three_Curve_Principle_groupId94.id" "Curves_R_Flc_SurfShape.iog.og[2].gid"
		;
connectAttr "Three_Curve_Principle_tweakSet45.mwc" "Curves_R_Flc_SurfShape.iog.og[2].gco"
		;
connectAttr "Three_Curve_Principle_tweak45.vl[0].vt[0]" "Curves_R_Flc_SurfShape.twl"
		;
connectAttr "Curves_L_FlcShape.ot" "Curves_L_Flc.t" -l on;
connectAttr "Curves_L_FlcShape.or" "Curves_L_Flc.r" -l on;
connectAttr "Curves_L_Flc_SurfShape.wm" "Curves_L_FlcShape.iwm";
connectAttr "Curves_L_Flc_SurfShape.o" "Curves_L_FlcShape.inm";
connectAttr "Curves_R_FlcShape.ot" "Curves_R_Flc.t" -l on;
connectAttr "Curves_R_FlcShape.or" "Curves_R_Flc.r" -l on;
connectAttr "Curves_R_Flc_SurfShape.wm" "Curves_R_FlcShape.iwm";
connectAttr "Curves_R_Flc_SurfShape.o" "Curves_R_FlcShape.inm";
connectAttr "Curves_Three_Principle.lips_annotations" "Curves_Lip_Annotations.v"
		;
connectAttr "Curves_annotationLocator1_pointConstraint1.ctx" "Curves_annotationLocator1.tx"
		 -l on;
connectAttr "Curves_annotationLocator1_pointConstraint1.cty" "Curves_annotationLocator1.ty"
		 -l on;
connectAttr "Curves_annotationLocator1_pointConstraint1.ctz" "Curves_annotationLocator1.tz"
		 -l on;
connectAttr "Curves_annotationLocator1Shape.wm" "|Curves_Three_Principle|Curves_Lip_Annotations|Curves_annotationLocator1|Curves_annotation3|Curves_annotationShape3.dom"
		 -na;
connectAttr "Curves_annotationLocator1.pim" "Curves_annotationLocator1_pointConstraint1.cpim"
		;
connectAttr "Curves_annotationLocator1.rp" "Curves_annotationLocator1_pointConstraint1.crp"
		;
connectAttr "Curves_annotationLocator1.rpt" "Curves_annotationLocator1_pointConstraint1.crt"
		;
connectAttr "Curves_L_Flc.t" "Curves_annotationLocator1_pointConstraint1.tg[0].tt"
		;
connectAttr "Curves_L_Flc.rp" "Curves_annotationLocator1_pointConstraint1.tg[0].trp"
		;
connectAttr "Curves_L_Flc.rpt" "Curves_annotationLocator1_pointConstraint1.tg[0].trt"
		;
connectAttr "Curves_L_Flc.pm" "Curves_annotationLocator1_pointConstraint1.tg[0].tpm"
		;
connectAttr "Curves_annotationLocator1_pointConstraint1.w0" "Curves_annotationLocator1_pointConstraint1.tg[0].tw"
		;
connectAttr "Curves_annotationLocator2Shape.wm" "|Curves_Three_Principle|Curves_Lip_Annotations|Curves_annotationLocator2|Curves_annotation3|Curves_annotationShape3.dom"
		 -na;
connectAttr "Curves_annotationLocator3Shape.wm" "|Curves_Three_Principle|Curves_Lip_Annotations|Curves_annotationLocator3|Curves_annotation3|Curves_annotationShape3.dom"
		 -na;
connectAttr "Curves_annotationLocator8_pointConstraint1.ctx" "Curves_annotationLocator8.tx"
		 -l on;
connectAttr "Curves_annotationLocator8_pointConstraint1.cty" "Curves_annotationLocator8.ty"
		 -l on;
connectAttr "Curves_annotationLocator8_pointConstraint1.ctz" "Curves_annotationLocator8.tz"
		 -l on;
connectAttr "Curves_annotationLocator8Shape.wm" "|Curves_Three_Principle|Curves_Lip_Annotations|Curves_annotationLocator8|Curves_annotation3|Curves_annotationShape3.dom"
		 -na;
connectAttr "Curves_annotationLocator8.pim" "Curves_annotationLocator8_pointConstraint1.cpim"
		;
connectAttr "Curves_annotationLocator8.rp" "Curves_annotationLocator8_pointConstraint1.crp"
		;
connectAttr "Curves_annotationLocator8.rpt" "Curves_annotationLocator8_pointConstraint1.crt"
		;
connectAttr "Curves_L_Flc.t" "Curves_annotationLocator8_pointConstraint1.tg[0].tt"
		;
connectAttr "Curves_L_Flc.rp" "Curves_annotationLocator8_pointConstraint1.tg[0].trp"
		;
connectAttr "Curves_L_Flc.rpt" "Curves_annotationLocator8_pointConstraint1.tg[0].trt"
		;
connectAttr "Curves_L_Flc.pm" "Curves_annotationLocator8_pointConstraint1.tg[0].tpm"
		;
connectAttr "Curves_annotationLocator8_pointConstraint1.w0" "Curves_annotationLocator8_pointConstraint1.tg[0].tw"
		;
connectAttr "Curves_Three_Principle.Brow_Annotations" "Curves_Brow_Annotations.v"
		;
connectAttr "Curves_annotationLocator5Shape.wm" "|Curves_Three_Principle|Curves_Brow_Annotations|Curves_annotationLocator5|Curves_annotation3|Curves_annotationShape3.dom"
		 -na;
connectAttr "Curves_annotationLocator6Shape.wm" "|Curves_Three_Principle|Curves_Brow_Annotations|Curves_annotationLocator6|Curves_annotation3|Curves_annotationShape3.dom"
		 -na;
connectAttr "Curves_annotationLocator7Shape.wm" "|Curves_Three_Principle|Curves_Brow_Annotations|Curves_annotationLocator7|Curves_annotation3|Curves_annotationShape3.dom"
		 -na;
connectAttr "Curves_Bot_LocShape.wp.wpx" "Curves_Top_Bot_distance.p1x";
connectAttr "Curves_Bot_LocShape.wp.wpy" "Curves_Top_Bot_distance.p1y";
connectAttr "Curves_Bot_LocShape.wp.wpz" "Curves_Top_Bot_distance.p1z";
connectAttr "Curves_Top_LocShape.wp.wpx" "Curves_Top_Bot_distance.p2x";
connectAttr "Curves_Top_LocShape.wp.wpy" "Curves_Top_Bot_distance.p2y";
connectAttr "Curves_Top_LocShape.wp.wpz" "Curves_Top_Bot_distance.p2z";
connectAttr "Three_Curve_Principle_groupParts48.og" "bend1.ip[24].ig";
connectAttr "Three_Curve_Principle_groupId48.id" "bend1.ip[24].gi";
connectAttr "Three_Curve_Principle_groupParts49.og" "bend1.ip[25].ig";
connectAttr "Three_Curve_Principle_groupId49.id" "bend1.ip[25].gi";
connectAttr "Three_Curve_Principle_groupParts50.og" "bend1.ip[26].ig";
connectAttr "Three_Curve_Principle_groupId50.id" "bend1.ip[26].gi";
connectAttr "Three_Curve_Principle_groupParts53.og" "bend1.ip[29].ig";
connectAttr "Three_Curve_Principle_groupId53.id" "bend1.ip[29].gi";
connectAttr "Three_Curve_Principle_groupParts54.og" "bend1.ip[30].ig";
connectAttr "Three_Curve_Principle_groupId54.id" "bend1.ip[30].gi";
connectAttr "Three_Curve_Principle_groupParts55.og" "bend1.ip[31].ig";
connectAttr "Three_Curve_Principle_groupId55.id" "bend1.ip[31].gi";
connectAttr "Three_Curve_Principle_groupParts57.og" "bend1.ip[33].ig";
connectAttr "Three_Curve_Principle_groupId57.id" "bend1.ip[33].gi";
connectAttr "Three_Curve_Principle_groupParts58.og" "bend1.ip[34].ig";
connectAttr "Three_Curve_Principle_groupId58.id" "bend1.ip[34].gi";
connectAttr "Three_Curve_Principle_groupParts59.og" "bend1.ip[35].ig";
connectAttr "Three_Curve_Principle_groupId59.id" "bend1.ip[35].gi";
connectAttr "Three_Curve_Principle_groupParts60.og" "bend1.ip[36].ig";
connectAttr "Three_Curve_Principle_groupId60.id" "bend1.ip[36].gi";
connectAttr "Three_Curve_Principle_groupParts61.og" "bend1.ip[37].ig";
connectAttr "Three_Curve_Principle_groupId61.id" "bend1.ip[37].gi";
connectAttr "Three_Curve_Principle_groupParts62.og" "bend1.ip[38].ig";
connectAttr "Three_Curve_Principle_groupId62.id" "bend1.ip[38].gi";
connectAttr "Three_Curve_Principle_groupParts63.og" "bend1.ip[39].ig";
connectAttr "Three_Curve_Principle_groupId63.id" "bend1.ip[39].gi";
connectAttr "Three_Curve_Principle_groupParts81.og" "bend1.ip[40].ig";
connectAttr "Three_Curve_Principle_groupId81.id" "bend1.ip[40].gi";
connectAttr "Three_Curve_Principle_groupParts82.og" "bend1.ip[41].ig";
connectAttr "Three_Curve_Principle_groupId82.id" "bend1.ip[41].gi";
connectAttr "Three_Curve_Principle_groupParts83.og" "bend1.ip[42].ig";
connectAttr "Three_Curve_Principle_groupId83.id" "bend1.ip[42].gi";
connectAttr "Three_Curve_Principle_groupParts84.og" "bend1.ip[43].ig";
connectAttr "Three_Curve_Principle_groupId84.id" "bend1.ip[43].gi";
connectAttr "Three_Curve_Principle_groupParts91.og" "bend1.ip[44].ig";
connectAttr "Three_Curve_Principle_groupId92.id" "bend1.ip[44].gi";
connectAttr "groupParts92.og" "bend1.ip[45].ig";
connectAttr "groupId93.id" "bend1.ip[45].gi";
connectAttr "Three_Curve_Principle_groupParts95.og" "bend1.ip[47].ig";
connectAttr "Three_Curve_Principle_groupId96.id" "bend1.ip[47].gi";
connectAttr "Three_Curve_Principle_groupParts97.og" "bend1.ip[48].ig";
connectAttr "Three_Curve_Principle_groupId98.id" "bend1.ip[48].gi";
connectAttr "Curves_BendHandleShape.dd" "bend1.dd";
connectAttr "Curves_BendHandle.wm" "bend1.ma";
connectAttr "Three_Curve_Principle_groupId48.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId49.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId50.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId53.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId54.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId55.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId57.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId58.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId59.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId60.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId61.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId62.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId63.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId81.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId82.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId83.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId84.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId92.msg" "bend1Set.gn" -na;
connectAttr "groupId93.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId96.msg" "bend1Set.gn" -na;
connectAttr "Three_Curve_Principle_groupId98.msg" "bend1Set.gn" -na;
connectAttr "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Out_Up2|Curves_Out_Up2Shape.iog.og[2]" "bend1Set.dsm"
		 -na;
connectAttr "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Mid_Up|Curves_Mid_UpShape.iog.og[2]" "bend1Set.dsm"
		 -na;
connectAttr "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Inn_Up1|Curves_Inn_Up1Shape.iog.og[2]" "bend1Set.dsm"
		 -na;
connectAttr "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Out_Up2|Curves_Out_Up2Shape.iog.og[2]" "bend1Set.dsm"
		 -na;
connectAttr "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Mid_Up|Curves_Mid_UpShape.iog.og[2]" "bend1Set.dsm"
		 -na;
connectAttr "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Inn_Up1|Curves_Inn_Up1Shape.iog.og[2]" "bend1Set.dsm"
		 -na;
connectAttr "Curves_Out_Up_LinearShape.iog.og[2]" "bend1Set.dsm" -na;
connectAttr "Curves_Out_Down_LinearShape.iog.og[2]" "bend1Set.dsm" -na;
connectAttr "Curves_Inn_Down_LinearShape.iog.og[2]" "bend1Set.dsm" -na;
connectAttr "Curves_Inn_Up_LinearShape.iog.og[2]" "bend1Set.dsm" -na;
connectAttr "Curves_DownShape.iog.og[2]" "bend1Set.dsm" -na;
connectAttr "Curves_UpShape.iog.og[2]" "bend1Set.dsm" -na;
connectAttr "Curves_NeutralShape.iog.og[2]" "bend1Set.dsm" -na;
connectAttr "Curves_Neutral1Shape.iog.og[6]" "bend1Set.dsm" -na;
connectAttr "Curves_Neutral3Shape.iog.og[6]" "bend1Set.dsm" -na;
connectAttr "Curves_Neutral4Shape.iog.og[6]" "bend1Set.dsm" -na;
connectAttr "Curves_Neutral2Shape.iog.og[6]" "bend1Set.dsm" -na;
connectAttr "Curves_R_Flc_SurfShape.iog.og[1]" "bend1Set.dsm" -na;
connectAttr "Curves_L_Flc_SurfShape.iog.og[1]" "bend1Set.dsm" -na;
connectAttr "Curves_L_In_circleShape.iog.og[2]" "bend1Set.dsm" -na;
connectAttr "Curves_R_In_circleShape.iog.og[4]" "bend1Set.dsm" -na;
connectAttr "bend1.msg" "bend1Set.ub[0]";
connectAttr "Three_Curve_Principle_tweak25.og[0]" "Three_Curve_Principle_groupParts48.ig"
		;
connectAttr "Three_Curve_Principle_groupId48.id" "Three_Curve_Principle_groupParts48.gi"
		;
connectAttr "Three_Curve_Principle_groupParts65.og" "Three_Curve_Principle_tweak25.ip[0].ig"
		;
connectAttr "Three_Curve_Principle_groupId65.id" "Three_Curve_Principle_tweak25.ip[0].gi"
		;
connectAttr "Three_Curve_Principle_groupId65.msg" "Three_Curve_Principle_tweakSet25.gn"
		 -na;
connectAttr "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Out_Up2|Curves_Out_Up2Shape.iog.og[3]" "Three_Curve_Principle_tweakSet25.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak25.msg" "Three_Curve_Principle_tweakSet25.ub[0]"
		;
connectAttr "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Out_Up2|Curves_Out_Up2ShapeOrig.ws" "Three_Curve_Principle_groupParts65.ig"
		;
connectAttr "Three_Curve_Principle_groupId65.id" "Three_Curve_Principle_groupParts65.gi"
		;
connectAttr "Three_Curve_Principle_tweak26.og[0]" "Three_Curve_Principle_groupParts49.ig"
		;
connectAttr "Three_Curve_Principle_groupId49.id" "Three_Curve_Principle_groupParts49.gi"
		;
connectAttr "Three_Curve_Principle_groupParts66.og" "Three_Curve_Principle_tweak26.ip[0].ig"
		;
connectAttr "Three_Curve_Principle_groupId66.id" "Three_Curve_Principle_tweak26.ip[0].gi"
		;
connectAttr "Three_Curve_Principle_groupId66.msg" "Three_Curve_Principle_tweakSet26.gn"
		 -na;
connectAttr "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Mid_Up|Curves_Mid_UpShape.iog.og[3]" "Three_Curve_Principle_tweakSet26.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak26.msg" "Three_Curve_Principle_tweakSet26.ub[0]"
		;
connectAttr "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Mid_Up|Curves_Mid_UpShapeOrig.ws" "Three_Curve_Principle_groupParts66.ig"
		;
connectAttr "Three_Curve_Principle_groupId66.id" "Three_Curve_Principle_groupParts66.gi"
		;
connectAttr "Three_Curve_Principle_tweak27.og[0]" "Three_Curve_Principle_groupParts50.ig"
		;
connectAttr "Three_Curve_Principle_groupId50.id" "Three_Curve_Principle_groupParts50.gi"
		;
connectAttr "Three_Curve_Principle_groupParts67.og" "Three_Curve_Principle_tweak27.ip[0].ig"
		;
connectAttr "Three_Curve_Principle_groupId67.id" "Three_Curve_Principle_tweak27.ip[0].gi"
		;
connectAttr "Three_Curve_Principle_groupId67.msg" "Three_Curve_Principle_tweakSet27.gn"
		 -na;
connectAttr "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Inn_Up1|Curves_Inn_Up1Shape.iog.og[3]" "Three_Curve_Principle_tweakSet27.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak27.msg" "Three_Curve_Principle_tweakSet27.ub[0]"
		;
connectAttr "|Curves_Three_Principle|Curves_Grp|Curves_Up_Sub_Grp|Curves_Inn_Up1|Curves_Inn_Up1ShapeOrig.ws" "Three_Curve_Principle_groupParts67.ig"
		;
connectAttr "Three_Curve_Principle_groupId67.id" "Three_Curve_Principle_groupParts67.gi"
		;
connectAttr "Three_Curve_Principle_tweak30.og[0]" "Three_Curve_Principle_groupParts53.ig"
		;
connectAttr "Three_Curve_Principle_groupId53.id" "Three_Curve_Principle_groupParts53.gi"
		;
connectAttr "Three_Curve_Principle_groupParts70.og" "Three_Curve_Principle_tweak30.ip[0].ig"
		;
connectAttr "Three_Curve_Principle_groupId70.id" "Three_Curve_Principle_tweak30.ip[0].gi"
		;
connectAttr "Three_Curve_Principle_groupId70.msg" "Three_Curve_Principle_tweakSet30.gn"
		 -na;
connectAttr "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Out_Up2|Curves_Out_Up2Shape.iog.og[3]" "Three_Curve_Principle_tweakSet30.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak30.msg" "Three_Curve_Principle_tweakSet30.ub[0]"
		;
connectAttr "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Out_Up2|Curves_Out_Up2ShapeOrig.ws" "Three_Curve_Principle_groupParts70.ig"
		;
connectAttr "Three_Curve_Principle_groupId70.id" "Three_Curve_Principle_groupParts70.gi"
		;
connectAttr "Three_Curve_Principle_tweak31.og[0]" "Three_Curve_Principle_groupParts54.ig"
		;
connectAttr "Three_Curve_Principle_groupId54.id" "Three_Curve_Principle_groupParts54.gi"
		;
connectAttr "Three_Curve_Principle_groupParts71.og" "Three_Curve_Principle_tweak31.ip[0].ig"
		;
connectAttr "Three_Curve_Principle_groupId71.id" "Three_Curve_Principle_tweak31.ip[0].gi"
		;
connectAttr "Three_Curve_Principle_groupId71.msg" "Three_Curve_Principle_tweakSet31.gn"
		 -na;
connectAttr "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Mid_Up|Curves_Mid_UpShape.iog.og[3]" "Three_Curve_Principle_tweakSet31.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak31.msg" "Three_Curve_Principle_tweakSet31.ub[0]"
		;
connectAttr "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Mid_Up|Curves_Mid_UpShapeOrig.ws" "Three_Curve_Principle_groupParts71.ig"
		;
connectAttr "Three_Curve_Principle_groupId71.id" "Three_Curve_Principle_groupParts71.gi"
		;
connectAttr "Three_Curve_Principle_tweak32.og[0]" "Three_Curve_Principle_groupParts55.ig"
		;
connectAttr "Three_Curve_Principle_groupId55.id" "Three_Curve_Principle_groupParts55.gi"
		;
connectAttr "Three_Curve_Principle_groupParts72.og" "Three_Curve_Principle_tweak32.ip[0].ig"
		;
connectAttr "Three_Curve_Principle_groupId72.id" "Three_Curve_Principle_tweak32.ip[0].gi"
		;
connectAttr "Three_Curve_Principle_groupId72.msg" "Three_Curve_Principle_tweakSet32.gn"
		 -na;
connectAttr "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Inn_Up1|Curves_Inn_Up1Shape.iog.og[3]" "Three_Curve_Principle_tweakSet32.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak32.msg" "Three_Curve_Principle_tweakSet32.ub[0]"
		;
connectAttr "|Curves_Three_Principle|Curves_Grp|Curves_Down_Sub_Grp|Curves_Inn_Up1|Curves_Inn_Up1ShapeOrig.ws" "Three_Curve_Principle_groupParts72.ig"
		;
connectAttr "Three_Curve_Principle_groupId72.id" "Three_Curve_Principle_groupParts72.gi"
		;
connectAttr "Three_Curve_Principle_tweak34.og[0]" "Three_Curve_Principle_groupParts57.ig"
		;
connectAttr "Three_Curve_Principle_groupId57.id" "Three_Curve_Principle_groupParts57.gi"
		;
connectAttr "Three_Curve_Principle_groupParts74.og" "Three_Curve_Principle_tweak34.ip[0].ig"
		;
connectAttr "Three_Curve_Principle_groupId74.id" "Three_Curve_Principle_tweak34.ip[0].gi"
		;
connectAttr "Three_Curve_Principle_groupId74.msg" "Three_Curve_Principle_tweakSet34.gn"
		 -na;
connectAttr "Curves_Out_Up_LinearShape.iog.og[3]" "Three_Curve_Principle_tweakSet34.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak34.msg" "Three_Curve_Principle_tweakSet34.ub[0]"
		;
connectAttr "Curves_Out_Up_LinearShapeOrig.ws" "Three_Curve_Principle_groupParts74.ig"
		;
connectAttr "Three_Curve_Principle_groupId74.id" "Three_Curve_Principle_groupParts74.gi"
		;
connectAttr "Three_Curve_Principle_tweak35.og[0]" "Three_Curve_Principle_groupParts58.ig"
		;
connectAttr "Three_Curve_Principle_groupId58.id" "Three_Curve_Principle_groupParts58.gi"
		;
connectAttr "Three_Curve_Principle_groupParts75.og" "Three_Curve_Principle_tweak35.ip[0].ig"
		;
connectAttr "Three_Curve_Principle_groupId75.id" "Three_Curve_Principle_tweak35.ip[0].gi"
		;
connectAttr "Three_Curve_Principle_groupId75.msg" "Three_Curve_Principle_tweakSet35.gn"
		 -na;
connectAttr "Curves_Out_Down_LinearShape.iog.og[3]" "Three_Curve_Principle_tweakSet35.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak35.msg" "Three_Curve_Principle_tweakSet35.ub[0]"
		;
connectAttr "Curves_Out_Down_LinearShapeOrig.ws" "Three_Curve_Principle_groupParts75.ig"
		;
connectAttr "Three_Curve_Principle_groupId75.id" "Three_Curve_Principle_groupParts75.gi"
		;
connectAttr "Three_Curve_Principle_tweak36.og[0]" "Three_Curve_Principle_groupParts59.ig"
		;
connectAttr "Three_Curve_Principle_groupId59.id" "Three_Curve_Principle_groupParts59.gi"
		;
connectAttr "Three_Curve_Principle_groupParts76.og" "Three_Curve_Principle_tweak36.ip[0].ig"
		;
connectAttr "Three_Curve_Principle_groupId76.id" "Three_Curve_Principle_tweak36.ip[0].gi"
		;
connectAttr "Three_Curve_Principle_groupId76.msg" "Three_Curve_Principle_tweakSet36.gn"
		 -na;
connectAttr "Curves_Inn_Down_LinearShape.iog.og[3]" "Three_Curve_Principle_tweakSet36.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak36.msg" "Three_Curve_Principle_tweakSet36.ub[0]"
		;
connectAttr "Curves_Inn_Down_LinearShapeOrig.ws" "Three_Curve_Principle_groupParts76.ig"
		;
connectAttr "Three_Curve_Principle_groupId76.id" "Three_Curve_Principle_groupParts76.gi"
		;
connectAttr "Three_Curve_Principle_tweak37.og[0]" "Three_Curve_Principle_groupParts60.ig"
		;
connectAttr "Three_Curve_Principle_groupId60.id" "Three_Curve_Principle_groupParts60.gi"
		;
connectAttr "Three_Curve_Principle_groupParts77.og" "Three_Curve_Principle_tweak37.ip[0].ig"
		;
connectAttr "Three_Curve_Principle_groupId77.id" "Three_Curve_Principle_tweak37.ip[0].gi"
		;
connectAttr "Three_Curve_Principle_groupId77.msg" "Three_Curve_Principle_tweakSet37.gn"
		 -na;
connectAttr "Curves_Inn_Up_LinearShape.iog.og[3]" "Three_Curve_Principle_tweakSet37.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak37.msg" "Three_Curve_Principle_tweakSet37.ub[0]"
		;
connectAttr "Curves_Inn_Up_LinearShapeOrig.ws" "Three_Curve_Principle_groupParts77.ig"
		;
connectAttr "Three_Curve_Principle_groupId77.id" "Three_Curve_Principle_groupParts77.gi"
		;
connectAttr "Three_Curve_Principle_tweak38.og[0]" "Three_Curve_Principle_groupParts61.ig"
		;
connectAttr "Three_Curve_Principle_groupId61.id" "Three_Curve_Principle_groupParts61.gi"
		;
connectAttr "Three_Curve_Principle_groupParts78.og" "Three_Curve_Principle_tweak38.ip[0].ig"
		;
connectAttr "Three_Curve_Principle_groupId78.id" "Three_Curve_Principle_tweak38.ip[0].gi"
		;
connectAttr "Three_Curve_Principle_groupId78.msg" "Three_Curve_Principle_tweakSet38.gn"
		 -na;
connectAttr "Curves_DownShape.iog.og[3]" "Three_Curve_Principle_tweakSet38.dsm" 
		-na;
connectAttr "Three_Curve_Principle_tweak38.msg" "Three_Curve_Principle_tweakSet38.ub[0]"
		;
connectAttr "Curves_DownShapeOrig.ws" "Three_Curve_Principle_groupParts78.ig";
connectAttr "Three_Curve_Principle_groupId78.id" "Three_Curve_Principle_groupParts78.gi"
		;
connectAttr "Three_Curve_Principle_tweak39.og[0]" "Three_Curve_Principle_groupParts62.ig"
		;
connectAttr "Three_Curve_Principle_groupId62.id" "Three_Curve_Principle_groupParts62.gi"
		;
connectAttr "Three_Curve_Principle_groupParts79.og" "Three_Curve_Principle_tweak39.ip[0].ig"
		;
connectAttr "Three_Curve_Principle_groupId79.id" "Three_Curve_Principle_tweak39.ip[0].gi"
		;
connectAttr "Three_Curve_Principle_groupId79.msg" "Three_Curve_Principle_tweakSet39.gn"
		 -na;
connectAttr "Curves_UpShape.iog.og[3]" "Three_Curve_Principle_tweakSet39.dsm" -na
		;
connectAttr "Three_Curve_Principle_tweak39.msg" "Three_Curve_Principle_tweakSet39.ub[0]"
		;
connectAttr "Curves_UpShapeOrig.ws" "Three_Curve_Principle_groupParts79.ig";
connectAttr "Three_Curve_Principle_groupId79.id" "Three_Curve_Principle_groupParts79.gi"
		;
connectAttr "Three_Curve_Principle_tweak40.og[0]" "Three_Curve_Principle_groupParts63.ig"
		;
connectAttr "Three_Curve_Principle_groupId63.id" "Three_Curve_Principle_groupParts63.gi"
		;
connectAttr "Three_Curve_Principle_groupParts80.og" "Three_Curve_Principle_tweak40.ip[0].ig"
		;
connectAttr "Three_Curve_Principle_groupId80.id" "Three_Curve_Principle_tweak40.ip[0].gi"
		;
connectAttr "Three_Curve_Principle_groupId80.msg" "Three_Curve_Principle_tweakSet40.gn"
		 -na;
connectAttr "Curves_NeutralShape.iog.og[3]" "Three_Curve_Principle_tweakSet40.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak40.msg" "Three_Curve_Principle_tweakSet40.ub[0]"
		;
connectAttr "Curves_NeutralShapeOrig.ws" "Three_Curve_Principle_groupParts80.ig"
		;
connectAttr "Three_Curve_Principle_groupId80.id" "Three_Curve_Principle_groupParts80.gi"
		;
connectAttr "Three_Curve_Principle_tweak41.og[0]" "Three_Curve_Principle_groupParts81.ig"
		;
connectAttr "Three_Curve_Principle_groupId81.id" "Three_Curve_Principle_groupParts81.gi"
		;
connectAttr "Three_Curve_Principle_groupParts85.og" "Three_Curve_Principle_tweak41.ip[0].ig"
		;
connectAttr "Three_Curve_Principle_groupId85.id" "Three_Curve_Principle_tweak41.ip[0].gi"
		;
connectAttr "Three_Curve_Principle_groupId85.msg" "Three_Curve_Principle_tweakSet41.gn"
		 -na;
connectAttr "Curves_Neutral1Shape.iog.og[7]" "Three_Curve_Principle_tweakSet41.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak41.msg" "Three_Curve_Principle_tweakSet41.ub[0]"
		;
connectAttr "Curves_Neutral1ShapeOrig.ws" "Three_Curve_Principle_groupParts85.ig"
		;
connectAttr "Three_Curve_Principle_groupId85.id" "Three_Curve_Principle_groupParts85.gi"
		;
connectAttr "Three_Curve_Principle_tweak42.og[0]" "Three_Curve_Principle_groupParts82.ig"
		;
connectAttr "Three_Curve_Principle_groupId82.id" "Three_Curve_Principle_groupParts82.gi"
		;
connectAttr "Three_Curve_Principle_groupParts86.og" "Three_Curve_Principle_tweak42.ip[0].ig"
		;
connectAttr "Three_Curve_Principle_groupId86.id" "Three_Curve_Principle_tweak42.ip[0].gi"
		;
connectAttr "Three_Curve_Principle_groupId86.msg" "Three_Curve_Principle_tweakSet42.gn"
		 -na;
connectAttr "Curves_Neutral3Shape.iog.og[7]" "Three_Curve_Principle_tweakSet42.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak42.msg" "Three_Curve_Principle_tweakSet42.ub[0]"
		;
connectAttr "Curves_Neutral3ShapeOrig.ws" "Three_Curve_Principle_groupParts86.ig"
		;
connectAttr "Three_Curve_Principle_groupId86.id" "Three_Curve_Principle_groupParts86.gi"
		;
connectAttr "Three_Curve_Principle_tweak43.og[0]" "Three_Curve_Principle_groupParts83.ig"
		;
connectAttr "Three_Curve_Principle_groupId83.id" "Three_Curve_Principle_groupParts83.gi"
		;
connectAttr "Three_Curve_Principle_groupParts87.og" "Three_Curve_Principle_tweak43.ip[0].ig"
		;
connectAttr "Three_Curve_Principle_groupId87.id" "Three_Curve_Principle_tweak43.ip[0].gi"
		;
connectAttr "Three_Curve_Principle_groupId87.msg" "Three_Curve_Principle_tweakSet43.gn"
		 -na;
connectAttr "Curves_Neutral4Shape.iog.og[7]" "Three_Curve_Principle_tweakSet43.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak43.msg" "Three_Curve_Principle_tweakSet43.ub[0]"
		;
connectAttr "Curves_Neutral4ShapeOrig.ws" "Three_Curve_Principle_groupParts87.ig"
		;
connectAttr "Three_Curve_Principle_groupId87.id" "Three_Curve_Principle_groupParts87.gi"
		;
connectAttr "Three_Curve_Principle_tweak44.og[0]" "Three_Curve_Principle_groupParts84.ig"
		;
connectAttr "Three_Curve_Principle_groupId84.id" "Three_Curve_Principle_groupParts84.gi"
		;
connectAttr "groupParts88.og" "Three_Curve_Principle_tweak44.ip[0].ig";
connectAttr "Three_Curve_Principle_groupId88.id" "Three_Curve_Principle_tweak44.ip[0].gi"
		;
connectAttr "Three_Curve_Principle_groupId88.msg" "Three_Curve_Principle_tweakSet44.gn"
		 -na;
connectAttr "Curves_Neutral2Shape.iog.og[7]" "Three_Curve_Principle_tweakSet44.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak44.msg" "Three_Curve_Principle_tweakSet44.ub[0]"
		;
connectAttr "Curves_Neutral2ShapeOrig.ws" "groupParts88.ig";
connectAttr "Three_Curve_Principle_groupId88.id" "groupParts88.gi";
connectAttr "Three_Curve_Principle_tweak45.og[0]" "Three_Curve_Principle_groupParts91.ig"
		;
connectAttr "Three_Curve_Principle_groupId92.id" "Three_Curve_Principle_groupParts91.gi"
		;
connectAttr "Three_Curve_Principle_groupParts93.og" "Three_Curve_Principle_tweak45.ip[0].ig"
		;
connectAttr "Three_Curve_Principle_groupId94.id" "Three_Curve_Principle_tweak45.ip[0].gi"
		;
connectAttr "Three_Curve_Principle_groupId94.msg" "Three_Curve_Principle_tweakSet45.gn"
		 -na;
connectAttr "Curves_R_Flc_SurfShape.iog.og[2]" "Three_Curve_Principle_tweakSet45.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak45.msg" "Three_Curve_Principle_tweakSet45.ub[0]"
		;
connectAttr "Three_Curve_Principle_groupParts89.og" "Three_Curve_Principle_groupParts93.ig"
		;
connectAttr "Three_Curve_Principle_groupId94.id" "Three_Curve_Principle_groupParts93.gi"
		;
connectAttr "Curves_R_Flc_SurfShapeOrig.w" "Three_Curve_Principle_groupParts89.ig"
		;
connectAttr "Three_Curve_Principle_groupId90.id" "Three_Curve_Principle_groupParts89.gi"
		;
connectAttr "Three_Curve_Principle_tweak46.og[0]" "groupParts92.ig";
connectAttr "groupId93.id" "groupParts92.gi";
connectAttr "groupParts94.og" "Three_Curve_Principle_tweak46.ip[0].ig";
connectAttr "groupId95.id" "Three_Curve_Principle_tweak46.ip[0].gi";
connectAttr "groupId95.msg" "Three_Curve_Principle_tweakSet46.gn" -na;
connectAttr "Curves_L_Flc_SurfShape.iog.og[2]" "Three_Curve_Principle_tweakSet46.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak46.msg" "Three_Curve_Principle_tweakSet46.ub[0]"
		;
connectAttr "groupParts90.og" "groupParts94.ig";
connectAttr "groupId95.id" "groupParts94.gi";
connectAttr "Curves_L_Flc_SurfShapeOrig.w" "groupParts90.ig";
connectAttr "groupId91.id" "groupParts90.gi";
connectAttr "Three_Curve_Principle_tweak47.og[0]" "Three_Curve_Principle_groupParts95.ig"
		;
connectAttr "Three_Curve_Principle_groupId96.id" "Three_Curve_Principle_groupParts95.gi"
		;
connectAttr "groupParts96.og" "Three_Curve_Principle_tweak47.ip[0].ig";
connectAttr "groupId97.id" "Three_Curve_Principle_tweak47.ip[0].gi";
connectAttr "groupId97.msg" "Three_Curve_Principle_tweakSet47.gn" -na;
connectAttr "Curves_L_In_circleShape.iog.og[3]" "Three_Curve_Principle_tweakSet47.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak47.msg" "Three_Curve_Principle_tweakSet47.ub[0]"
		;
connectAttr "Curves_L_In_circleShapeOrig.ws" "groupParts96.ig";
connectAttr "groupId97.id" "groupParts96.gi";
connectAttr "Three_Curve_Principle_tweak48.og[0]" "Three_Curve_Principle_groupParts97.ig"
		;
connectAttr "Three_Curve_Principle_groupId98.id" "Three_Curve_Principle_groupParts97.gi"
		;
connectAttr "groupParts98.og" "Three_Curve_Principle_tweak48.ip[0].ig";
connectAttr "groupId99.id" "Three_Curve_Principle_tweak48.ip[0].gi";
connectAttr "groupId99.msg" "Three_Curve_Principle_tweakSet48.gn" -na;
connectAttr "Curves_R_In_circleShape.iog.og[5]" "Three_Curve_Principle_tweakSet48.dsm"
		 -na;
connectAttr "Three_Curve_Principle_tweak48.msg" "Three_Curve_Principle_tweakSet48.ub[0]"
		;
connectAttr "Curves_R_In_circleShapeOrig1.ws" "groupParts98.ig";
connectAttr "groupId99.id" "groupParts98.gi";
connectAttr "Curves_Three_Principle.curvature" "Three_Curve_Principle_unitConversion1.i"
		;
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "Curves_Top_Bot_distance.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "Curves_R_Flc_SurfShape.iog.og[0]" ":initialShadingGroup.dsm" -na;
connectAttr "Curves_L_Flc_SurfShape.iog.og[0]" ":initialShadingGroup.dsm" -na;
connectAttr "Three_Curve_Principle_groupId90.msg" ":initialShadingGroup.gn" -na;
connectAttr "groupId91.msg" ":initialShadingGroup.gn" -na;
// End of Three_Curve_Principle.ma
