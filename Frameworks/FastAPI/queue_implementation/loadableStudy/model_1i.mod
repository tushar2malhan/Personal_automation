# ACA AMPL model # full model
# changelog upon aca_model_v2 (Aug 05, 2019)
# Added by CC
##-------------------------------------------------------------------------
# Changelog: 31 Jan 2021
# 1. Added ballast  parameters
# ballast requirement
# set ballastSet1;
# set ballastSet2;
# set ballastSet3;
# param minBallastAmt default 100;
# 2. Added ballast constraints
# Condition113a, Condition113b, Condition113c, Condition113d
# Condition114a, Condition114b
##-------------------------------------------------------------------------
# Changelog: 27 Jan 2021
# 1. Added Commingle parameters
# set Cm_1 within C; # cargo 1 commingle 
# set Cm_2 within C; # cargo 2 commingle 
# set Tm within T; # Suitable tank for commingle
# param density_Cm{c in C} default 1; # SG when commingle
# 2. Added Commingle Constraints
# Condition01a, Condition01b, Condition01c
# Constr5b, Constr5c
# Disable Constr7a will add back later
##-------------------------------------------------------------------------
# Changelog: 15 Jan 2021
#1. Added Draft parameters
# param Mean_draft{p in P} default 0;
# param Base_draft{p in P} default 0;
#  param mDraft1,..., mDraft10 ;
#  param bDraft1, ...,bDraft10;
#2. Added New SF and BM parameters
# param Fr >= 0 integer, default 1; #frame
# set Frames := 0..Fr;
# # weight ratio
# param weightRatio_ct {f in Frames, t in T} default 0;
# param weightRatio_bt {f in Frames, t in TB} default 0;
# param weightRatio_ot {f in Frames, t in OtherTanks} default 0;
# # LCG
# param LCG_ct {f in Frames, t in T} default 0;
# param LCG_bt {f in Frames, t in TB} default 0;
# param LCG_ot {f in Frames, t in OtherTanks} default 0;
# param LCG_fr {f in Frames} default 0;
# # Sn
# param lowerSFlimit{f in Frames} default -100000;
# param upperSFlimit{f in Frames} default 100000;
# param BV_SF {f in 1..Fr, p in P} default 0;
# param CD_SF {f in 1..Fr, p in P} default 0;
# # Bn
# param lowerBMlimit{f in Frames} default -100000;
# param upperBMlimit{f in Frames} default 100000;
# param BV_BM {f in 1..Fr, p in P} default 0;
# param CD_BM {f in 1..Fr, p in P} default 0;

#3. Added New SF and BM Constraints
# Constr17a 
# Constr18a to Constr18c Constr18d 
# Constr19a  to Constr19c 
# Condition20a to Condition20b 
# Condition21a to Condition21b

#4. Modified Objective Function to maximize the amout of loaded cargoes in terms of total loaded amount & minimize the ballast amount & minimize the number of cargo tanks to be used.
# Revised version:minus the weighted (10000 to 15000)*sum{t in T, c in C} x[c,t]; (that minimize total number of cargo tanks) in the Objective Function
# Removed the previous Minus sum of zTank, not required now.
# Removed the previous Constr22c, not required now.
 
##-------------------------------------------------------------------------
# Changelog: 10 Jan 2021
# Incorporated to PengHui's program model  model_1c.mod (also renamed as model_1c_CC20210110.mod);

##-------------------------------------------------------------------------
# Changelog: 24 Dec 2020
#1. Added new variables/parameters:
# param MBallast default 10000; #MBallast is an arbitrary number much larger (10 times) than the largest value of wB
# var zBallast{P} binary default 0; # to be optimised to either 0 or 1 for each port P by the program as follows:
# zBallast=0, Ballast tanks can be both filled and discharged at each loading and discharging port.
# zBallast=1, Ballast tanks can only be filled at each discharging port. Ballast tanks can only be discharged) loading port.

#2. Modify new ballast constraints at loading ports and discharging ports
#Constr22a
#Constr22b

#3. Renamed # param gamma (Constr15c7 to Constr15c10) and replaced with ListMOM as in original version.
#4. Updated new trim constraints, now in terms of 10-piece-wise linear approximation for each of the LCB.

##-------------------------------------------------------------------------
# Changelog: 8 Dec 2020
#1. Added new variables/parameters:
# param gamma default 0.01;
#For Constr22c:
#var zTank{T} binary; # 1 if cargo tank t is used/filled by any cargo type;
#For Constr15:
#var Vertical_moment{p in P} default 0; 
#var Final_list_moment{p in P} default 0;  
#param dterms{p in P} default 1; 

#2. Modified Objective Function to maximize the amout of loaded cargoes in terms of total loaded amount & minimize the ballast amount & minimize the number of cargo tanks to be used.
# Added the Minus sum of zTank (that minimize total number of cargo tanks) in the Objective Function

#3. i) Derived and added new List constraints: Constr15c1 to Constr15c10 associated with gamma
#   ii) Remarked previous List constraints: Constr15a3,  Constr15a4 associated with ListMOM

##-------------------------------------------------------------------------
# Changelog: 30 Nov 2020
#1. Removed irrelevant sets/parameters/functions
#2. Added new list constraints using 10-piece linear functions
#3. Removed McCormick envelope method
#Constr15b1
#Constr15b2 
#Constr15
#Constr151 
#4. Added new ballast constraints at loading ports and discharging ports
#Constr22a
#Constr22b
#5.  Renamed  sets/parameters
#6.  Modified objective function: Removed sum of zBt (that minimize number of ballast tanks) from the objective function



## basic: set and params -----------------------------------------------------------
set T; # set of all cargo tanks
set T1; # set of cargos tanks without pw tcg details
#set T2; # set of cargos tanks without pw lcg details

set T_loaded within T; # set of loaded tanks (preloaded condition)

set C; # set of all cargoes
set C_loaded within C; # set of all loaded cargoes preloaded condition)
set C_loaded1 within C default {}; # set of all loaded cargoes with auto discharge)
set C_max;
set C_equal default C;
set C_slop default C;

param I_loaded{c in C_loaded, t in T_loaded} binary default 0; # 1 if cargo c has been loaded in tank t ((preloaded condition)

## compatibility: set and params
set Tc{c in C} within T default T; # set of tanks compatible with cargo c (consider tank coating, cargo history, tank heating);
#check {c in C_loaded}: sum{t in T_loaded diff Tc[c]}I[c,t] = 0; # check cargo-tank compatibility in existing allocation.
set Ct{t in T} default C; # set of cargoes compatible with tank t (consider tank coating, cargo history, tank heating);

set Cbarc{c in C}; # set of cargoes in conflict with cargo c (consider USCG list);

## ballast-cargo tank compatibility: set and params

## capacity: set and params
param NP >= 0 integer; # total number of ports in the booking list
param LP >=0, <= NP integer; # the last loading port


set P := 1 .. NP; # set of ports
set P1 default 1 .. NP-1; # set of ports for P_stable
set P_org := {0}; # a virtual port before the first port
set Pbar := P_org union P;
set P_load := 1 .. LP ; # set of loading ports
set P_dis := LP+1 .. NP ; # set of discharging ports
set P_last_loading := {LP} ; # the last loading port
set P0 default {};
set P_ban_ballast default {}; # set of port with ban_ballast

param firstloadingPort default 1;

param densityCargo_Low{c in C} >=0 default 1; # cargo density @ high temperature (in t/m3)
param densityCargo_High{c in C} >=0 default 1; # cargo density @ low temperature (in t/m3)
#param highDensityOn default 1; # change highDensityOn to a large number to deactivate high density check

param density_up{c in C} default densityCargo_Low[c]; # density used for the upper loading bound
param density_low{c in C} default densityCargo_High[c]; # density used for the lower loading bound
param upperHighDensity{c in C, t in T} default 1; # upper filling limit for high density cargo, (0,1)

param aveCargoDensity default 1;

# cargo priority
param priority{c in C} >0 default 100; # cargo with higher priority will be loaded as close to the intended quantity as possible
# priority 1 and 2 cargo
set cargoPriority within {C,C};

# tank priority
param priorityTank{c in C, t in T}  default 1; 

param Wcp{c in C, p in P} default 0; # weight (in metric tone) of cargo to be moved at port p. positive -> to be loaded; negative -> to be discharged; zero -> no action is required.
param Vcp{c in C, p in P} = Wcp[c,p]/densityCargo_Low[c]; # volume (in t/m3) to be moved at port p based on low density.

param W0{c in C, t in T} >=0 default 0; # weight of cargo c remained in tank t at initial state (before ship entering the first port)
param Q0{c in C, t in T} = W0[c,t]/densityCargo_Low[c]; # volume of cargo c remained in tank t at initial state
check {c in C_loaded, t in T_loaded diff Tc[c]}: Q0[c,t]=I_loaded[c,t]; # check cargo-tank compatibility in existing allocation.

set fixCargoPort default {}; # for fixing preloaded cargo
param W1{c in C, t in T, p in fixCargoPort} >=0 default 0; # fix weight of cargo c  in port p at tank remained 
param Q1{c in C, t in T, p in fixCargoPort} = W1[c,t,p]/densityCargo_Low[c]; # volume of cargo c remained in tank t at initial state

param W_loaded{C_loaded,T_loaded,P} default 0; # the weight of preloaded cargo to be moved from tank t at port p
param V_loaded{c in C_loaded, t in T_loaded, p in P} = W_loaded[c,t,p]/densityCargo_Low[c]; # the volume of preloaded cargo to be moved from tank t at port p

# for fixed qw
param QW{c in C, t in T} >=0 default 0;
set QWT{c in C} default {};

# discharge
param QW1{c in C, t in T, p in P} >=0 default 0;
set QWT1{c in C} default {};

# loading ports
set loadPort;
param loadingPortAmt{p in loadPort} default 0;
param deballastPercent default 0.4;

# discharge ports
set dischargePort default {};
param dischargePortAmt{p in dischargePort} default 0;
param ballastPercent default 0.4;

## ballast tanks
set TB; #set of ballast tanks
set TB1; # set of ballast tanks with no pw tcg details
set TB2; # set of ballast tanks with no pw lcg details
set TB3 default {}; # set of ballast tanks no restriction in ballast/deballast
set TB4 default TB; # for rotation port 2
set TB5 default {}; # for small bunker
set minTB default {}; # set of ballast tanks >= 30cm ullage
set toBallastTank default {};
set toDeballastTank default {};
param ballastLimit{p in Pbar} default 1e6;
set TB0 default TB; # deballasting tanking
set TBinit default TB; # empty ballast tanks at arrival

param densitySeaWater{p in Pbar} default 1.025; # density of water @ high temperature
param densityBallast{p in Pbar} default 1.025; # density of water @ high temperature


# locked ballast
param B_locked{TB,Pbar} default 0;
set fixBallastPort default {}; 
set sameBallastPort default {}; 

set P_stable0 default P1;  # loading P1 = 1..NP-1 # discharge P = 1..NP
set P_stable = P_stable0 diff fixBallastPort diff sameBallastPort; # stable port

# for departure of last discharging port min draft constraint
set NP1 default {NP}; # NP1 = {} for cargo left in last discharge port
set P_stable1 =  P_stable diff NP1; # port with min draft requirement
set P_stable2{C} default P_stable; 
set P_opt within C cross 1..NP default {}; 
set P_bm default {};

set zeroListPort default {};

param capacityCargoTank{t in T} >= 0; # cargo tank capacity (in m3)
param densityCargoTank{t in T} >= 0 default 1.0; # cargo tank density (in t/m3)
param onboard{t in T} >=0 default 0; # onboard qty

## parameters for capacity rules
param upperBound{t in T} default 0.980; #upper loading bound for each tank: 0.98 for tank capacity more than 0.5 km^3, and 1 for the other cargo tanks.
param lowerBound{t in T} default 0.0; #lower loading bound for each tank, e.g. 0.6
param upperBoundC{ c in C, t in T} default upperBound[t]; 
#check {c in C_loaded, t in Tc[c] inter T_loaded}: Q0[c,t] <= upperBound[t]*gt[t]*I[c,t]; # amount of cargo preloaded <= capacity of the tank.

## locked tank, locked allocation plan.
set T_locked within T;
set C_locked within C;
param A_locked{C_locked,T_locked} binary default 0; # 1 if tank t is locked for cargo c
#check {c in C_locked}: sum{t in T_locked diff Tc[c]}A_locked[c,t] = 0; # check cargo-tank compatibility in locked allocation.
#check {c in C_locked, t in T_locked inter Tc[c]}: sum{k in C_locked inter Cbarc[c], u in T_locked inter Tadj[t]}(A_locked[k,u])-M[t]*(1-A_locked[c,t]) <= 0; # check cargo-cargo compatibility in locked allocation.

param W_locked{C_locked,T_locked,P} default 0; # the amount of cargo locked to put/unload into/from tank t at port p
param V_locked{c in C_locked, t in T_locked, p in P} = W_locked[c,t,p]/densityCargo_Low[c];
#check {c in C_locked, t in T_locked diff Tc[c],p in P_load}: W_locked[c,t,p]=A_locked[c,t]; # check cargo-tank compatibility in locked allocation.
#check {c in C_locked, p in P_load}:  0 <= sum{t in Tc[c] inter T_locked} V_locked[c,t,p] <= Vcp[c,p]; # amount of cargo to be loaded <= amount available at the port.
#check {c in C_locked, t in Tc[c] inter T_locked, p in P_load}: V_locked[c,t,p] <= upperBound[t]*gt[t]*A_locked[c,t]; # amount of cargo pre-allocated <= capacity of the tank.

## other tanks
set OtherTanks; # set of other tanks, e.g. fuel tanks, water tanks,
param  weightOtherTank{t in OtherTanks, p in Pbar} default 0; # weight of each tank

param maxTankUsed default 100;
param intended default 1e6; 


#set CargoSolid; # solidifying cargo

param capacityBallastTank{t in TB}; # capacity of each ballast tank
param upperBoundB1{t in TB} default 0.98; #upper loading bound for each ballast tank
param lowerBoundB1{t in TB} default 0; #lower loading bound for each ballast tank
param initBallast {t in TB} default 0; # initial ballast
param finalBallast {t in TB} default 0; # final ballast
set incTB default {};  # TB to inc
set decTB default {};  # TB to dec 
#set finalBallastPort;
set lastLoadingPortBallastBan;

set ballastBan default {};

param minCargoLoad{c in C} default 0;
param toLoad{c in C} default 0;
param diffSlop default 1;

## commingled cargo
set Cm_1 within C;
set Cm_2 within C;
set Tm within T;
param density_Cm{c in C} default 1; # density at commingle temperature
param Qm_1 default 0; # manual fix cargo1 wt
param Qm_2 default 0; # manual fix cargo2 wt
param Mm default 1e5;

## ballast requirement
set loadingPort within 0..NP cross 0..NP; # loading port
set loadingPortNotLast within 0..NP cross 0..NP; # loading port except last

set depArrPort1 within 0..NP cross 0..NP default {}; # with ROB
set depArrPort2 within 0..NP cross 0..NP default {}; # no ROB
set depArrPort3 within 0..NP cross 0..NP default {}; # no ROB
set rotatingPort1 within 0..NP cross 0..NP default {};  
set rotatingPort2 within 0..NP cross 0..NP default {};  
set specialBallastPort default {LP-1, LP}; # default LP-1
set zeroBallastPort default {}; # default LP

param minBallastAmt{t in TB} default 10;
param diffBallastAmt{p in P} default 2000;
param minCargoAmt default 1000;

## cargo tank
set slopS default {'SLS'};
set slopP default {'SLP'};

set cargoTankNonSym within T cross T; # non-sym cargo tanks
set symmetricVolTank within T cross T default  {('3P','3S')} union (slopS cross slopP);
set equalWeightTank within T cross T default  {('1P','1S'), ('2P','2S'), ('4P','4S'), ('5P','5S')};

## stability: set and params
set AllTanks = T union OtherTanks union TB; # set of all tanks
param lightWeight; # lightweight of the ship
param deadweightConst default 0; # deadweight constant

param deadweight > 0 default 1e6; # deadweight
param cargoweight > 0 default 1e6;
set firstDisCargo;

param diffVol default 0.05;

param maxEmptyTankWeight default 0;
# stability - draft
param displacementLimit{p in Pbar}; # displacement limit derived from maximum permissible draft and hydrostatic table.
param displacementLowLimit{p in Pbar} default 0; # displacement limit lower bound

# stability - list
#param upListMOM; # upperbound on the tranversal moment
#param lowListMOM; # lowerbound on the tranversal moment
param TCGt{t in AllTanks} default 0; #tank TCG
param TCGtp{t in OtherTanks, p in Pbar} default 0;
param ListMOM default 500; # upper and lower limits of tcg mom
param TCGdw default 0; # TCG deadweight constant

param pwTCG default 0;
param mTankTCG{p in 1..pwTCG,   t in T union TB} default 0; # need update input based on tcg details
param bTankTCG{p in 1..pwTCG-1, t in T union TB} default 0; # need update input based on tcg details

# stability - trim
param LCGt{t in AllTanks}; #tank LCG
param LCGtport{t in T, p in Pbar} default 0; # more accurate LCG
param LCGship;
param LCGdw default 0;
param LCGtp{t in OtherTanks, p in Pbar} default 0;
#param TrimMOM default 1;
param trim_upper{p in Pbar} default 0.0001;
param trim_lower{p in Pbar} default -0.0001;
param ave_trim {p in Pbar} default 0.5*(trim_lower[p]+trim_upper[p]);

param pwLCG default 0;
param mTankLCG{p in 1..pwLCG,   t in T union TB} default 0; # need update input based on tcg details
param bTankLCG{p in 1..pwLCG-1, t in T union TB} default 0; # need update input based on tcg details


param pwLCB default 0;
param mLCB{p in 1..pwLCB} default 0;
param bLCB{p in 1..pwLCB-1}  default 0;

param pwMTC default 0;
param mMTC{p in 1..pwMTC} default 0;
param bMTC{p in 1..pwMTC-1}  default 0;


# stability - Draft 
param base_draft{p in Pbar} default 0;
param draft_corr{p in Pbar} default 0;

param pwDraft default 0;
param mDraft{p in 1..pwDraft} default 0;
param bDraft{p in 1..pwDraft-1}  default 0;

param disp0 default 123177.0;
# stability - SF and BM
param adjMeanDraft default 0.166895; # KAZUSA 0.166895 AP 0.131300
param adjLCB default -13665.8; # KAZUSA -13665.8 AP -68197.25
param adjMTC default 2239.64; # KAZUSA 2239.64 AP 2393.987

param Fr >= 0 integer, default 1; #frame
set Frames := 0..Fr;
# weight ratio
param weightRatio_ct {f in Frames, t in T} default 0;
param weightRatio_bt {f in Frames, t in TB} default 0;
param weightRatio_ot {f in Frames, t in OtherTanks} default 0;
# LCG
param LCG_ct {f in Frames, t in T} default 0;
param LCG_bt {f in Frames, t in TB} default 0;
param LCG_ot {f in Frames, t in OtherTanks} default 0;
param LCG_fr {f in Frames} default 0;
# Sn
param lowerSFlimit{f in Frames} default -100000;
param upperSFlimit{f in Frames} default 100000;

param BV_SF {f in 1..Fr, p in Pbar} default 0;
param CD_SF {f in 1..Fr, p in Pbar} default 0;
param CT_SF {f in 1..Fr, p in Pbar} default 0;

# Bn
param lowerBMlimit{f in Frames} default -100000;
param upperBMlimit{f in Frames} default 100000;

param BV_BM {f in 1..Fr, p in Pbar} default 0;
param CD_BM {f in 1..Fr, p in Pbar} default 0;
param CT_BM {f in 1..Fr, p in Pbar} default 0;

param numSolutions integer default 3;
param runtimeLimit integer default 60;
param seed integer default 0;

param tolerance := 0; # tolerance for rounding
param IIS integer default 1;

### Decision Variables ###
# for compatibility
# Added in orTools - 20220301
var x{C,T} binary; # 1 if cargo c is allocated into tank t
var xt{T} binary;
# for capacity
# Added in orTools - 20220301
var w{C,T,P}; # weight of cargo (w.r.t. low density) planned to be serviced from/to tank t at port p. positive -> load; zero -> no action; negative -> unload.
# Added in orTools, refer to constraint 020 - 20220301
var y{c in C,t in T,p in P} = w[c,t,p]/densityCargo_Low[c]; # volume of cargo (w.r.t. low density) planned to be serviced from/to tank t at port p. positive -> load; zero -> no action; negative -> unload.
# Added in orTools - 20220301
var qw2f{C,T,Pbar} >=0 integer; # weight of cargo remained in tank t after visiting port p.
# Added in orTools - 20220301
var qw{c in C,t in T,p in Pbar} = qw2f[c,t,p]/10;
# Added in orTools - 20220301
var qty{c in C,t in T,p in Pbar} = qw[c,t,p]/densityCargo_Low[c]; # volume of cargo remained in tank t after visiting port p.
# Added in orTools - 20220301
var qwz{c in C,t in T,p in Pbar} binary;

# Added in orTools - 20220301
var xwB{TB,Pbar} binary; # 1 if ballast tank t is filled with water at port p

# Added in orTools - 20220301
var xB{TB,Pbar} binary; # 1 if ballast tank t is filled with water at port p

# Added in orTools - 20220301
var wB{TB,Pbar}  >= 0; # weight of water in ballast tank t at port p

# Added in orTools - 20220301
var zBa1{TB} binary;
# Added in orTools - 20220301
var zBb1{TB} binary;
# Added in orTools - 20220301
var zBa2{TB} binary;
# Added in orTools - 20220301
var zBb2{TB} binary;

# Added in orTools - 20220301, refer to Constr11, Constr12
var yB{t in TB,p in Pbar} = wB[t,p]/densityBallast[p]; # volume of water (w.r.t. low density) planned to be added into ballast tank t at port p

# Added in orTools - 20220301
var TB_tmom{t in TB, p in Pbar} default 0; # TMom TB
# Added in orTools - 20220301
var TB_lmom{t in TB, p in Pbar} default 0; # TMom TB


# Added in orTools - 20220301
var T_tmom{t in T, p in Pbar} default 0; # TMom T
# Added in orTools - 20220301
var T_mom{p in Pbar} default 0; # TCG Mom
# Added in orTools - 20220301
var L_mom{p in Pbar} default 0; # LCG Mom
# Added in orTools - 20220301
var LCBp {p in Pbar} default 0;
# Added in orTools - 20220301
var MTCp {p in Pbar} default 0; 
# extra amout (w.r.t. metric tone) of cargo c that the tank can take in
#var extraWeight{c in C, t in T} = x[c,t]*min((upperBound[t]*capacityCargoTank[t]-sum{p in P_last_loading}q[c,t,p]*densityCargo_Low[c]/density_up[c])*density_up[c],(min(1,highDensityOn*densityCargoTank[t]/densityCargo_High[c])*capacityCargoTank[t]-sum{p in P_last_loading}q[c,t,p]*densityCargo_Low[c]/densityCargo_High[c])*densityCargo_High[c]); 

# Added in orTools - 20220301
var delta{c in C diff C_locked, p in P_dis} binary;

# BM and SF
# Added in orTools - 20220301
var displacement{p in Pbar} >=0; # displacement
# Added in orTools - 20220301
var displacement1{p in Pbar} >=0; # displacement corrected for seawater density
# Added in orTools - 20220301
var mean_draft{p in Pbar} default 0;
# Added in orTools - 20220301
var wn{f in Frames, p in Pbar} >= 0;
# Added in orTools - 20220301
var mn{f in Frames, p in Pbar};

# Added in orTools - 20220301
var wC{t in T, p in Pbar} >= 0;
# Added in orTools - 20220301
var SS{f in Frames, p in Pbar} default 0;
# Added in orTools - 20220301
var SB{f in Frames, p in Pbar} default 0;
# Added in orTools - 20220301
var est_trim{p in Pbar}default 0;



## objective function
#####################
# to maximize the amout of loaded cargoes in terms of total loaded amount + minimize the ballast amount.
maximize Action_Amount:
sum{c in C, t in Tc[c]} priority[c]*(sum{p in P_last_loading} qw[c,t,p]- sum{p in P_dis} w[c,t,p])
-1*sum{t in TB, p in P}wB[t,p]
- maxEmptyTankWeight*sum{ (c, p) in P_opt, t in T} qwz[c,t,p] +
sum{c in C, t in {'1C', '1P', '1S', '5C', '5P', '5S'} union slopS union slopP} priority[c]*(sum{p in P_last_loading} qw[c,t,p]- sum{p in P_dis} w[c,t,p])
;


#####################
#original
# to maximize the amout of loaded cargoes in terms of total loaded amount + minimize the ballast usage.
# maximize Action_Amount:
#sum{c in C, t in Tc[c]} priority[c]*(sum{p in P_last_loading} qw[c,t,p]- sum{p in P_dis} w[c,t,p])-1*sum{t in TB, p in P}wB[t,p]-100*sum{t in TB}zB[t];
##sum{c in C, t in Tc[c]} priority[c]*(sum{p in P_last_loading} qw[c,t,p]- sum{p in P_dis} w[c,t,p])+sum{c in C, t in Tc[c], p in P} priorityTank[c,t]*q[c,t,p]/gt[t]-1*sum{t in TB, p in P}wB[t,p]-100*sum{t in TB}zB[t];

### Constraints ###
## basic conditions
# Added in orTools - 20220301
subject to Condition0 {c in C diff C_loaded diff C_locked}: sum{t in T diff Tc[c]} x[c,t] = 0; # cargo c is not allocated to tank t if t is not compatible with cargo c
# Added in orTools - 20220301
subject to Condition01 {t in T diff Tm}: sum{k in C}x[k,t] <= 1; # one tank can only take in one cargo
# commingled cargo
# Added in orTools - 20220301
subject to Condition01a {t in Tm}: sum{k in C diff Cm_1} x[k,t] <= 1; # one tank can only take in one cargo
# Added in orTools - 20220301
subject to Condition01b {t in Tm}: sum{k in C diff Cm_2} x[k,t] <= 1; # one tank can only take in one cargo
# Added in orTools - 20220301
subject to Condition01c {t in Tm, k1 in Cm_1, k2 in Cm_2}:  x[k1,t] + x[k2,t] <= 2; # one tank can only take in two cargo

# Added in orTools - 20220301

subject to Condition01z {c in C diff C_locked, p in P_last_loading}: sum{t in Tc[c]} qw[c,t,p] >= minCargoLoad[c]; # a cargo is loaded to at min amt at last loading port

# Added in orTools - 20220302
subject to Condition020 {c in C, t in T diff Tc[c], p in P}: y[c,t,p] = x[c,t]; # cargo c is not allocated to tank t if t is not compatible with cargo c
# Added in orTools - 20220302
subject to Condition021 {c in C, t in T diff Tc[c], p in P}: qty[c,t,p] = x[c,t]; # cargo c is not allocated to tank t if t is not compatible with cargo c
# Added in orTools - 20220302
subject to Condition03 {c in C diff C_locked}: sum{t in Tc[c]} Q0[c,t] + sum{p in P_load, t in Tc[c]} y[c,t,p] >= sum{p in P_dis, t in Tc[c]} -y[c,t,p]; # total loaded >= total discharged
# Added in orTools - 20220302
subject to Condition04 {c in C diff C_locked, p in P_load : Vcp[c,p]>0}:  0 <= sum{t in Tc[c]} y[c,t,p] <= Vcp[c,p]; # amount of cargo to be loaded <= amount available at the port.
# Added in orTools - 20220302
subject to Condition041 {c in C, t in Tc[c], p in P_load}: y[c,t,p]>=0;
# Added in orTools - 20220302
subject to Condition05 {c in C diff C_locked, p in P_dis : Vcp[c,p]<0}:  0 >= sum{t in Tc[c]} y[c,t,p] >= Vcp[c,p]; # amount of cargo to be discharged is not more than the amount needed at the port.
# Added in orTools - 20220302
subject to Condition050 {c in C diff C_locked, p in P_dis : Vcp[c,p]<0}:  sum{t in Tc[c]}qty[c,t,p-1]>=-Vcp[c,p]-1e6*(1-delta[c,p]);
# Added in orTools - 20220302
subject to Condition050a {c in C diff C_locked, p in P_dis : Vcp[c,p]<0}:  sum{t in Tc[c]}qty[c,t,p-1]<=-Vcp[c,p]+1e6*delta[c,p];
# Added in orTools - 20220302
subject to Condition050b {c in C diff C_locked, p in P_dis : Vcp[c,p]<0}:  -Vcp[c,p]-1e6*(1-delta[c,p])<=-sum{t in Tc[c]} y[c,t,p];
# Added in orTools - 20220302
subject to Condition050b1 {c in C diff C_locked, p in P_dis : Vcp[c,p]<0}:  -sum{t in Tc[c]} y[c,t,p]<=-Vcp[c,p]+1e6*(1-delta[c,p]);
# Added in orTools - 20220302
subject to Condition050c {c in C diff C_locked, p in P_dis : Vcp[c,p]<0}:  -1e6*(delta[c,p])<=-sum{t in Tc[c]} qty[c,t,p];
# Added in orTools - 20220302
subject to Condition050c1 {c in C diff C_locked, p in P_dis : Vcp[c,p]<0}:  -sum{t in Tc[c]} qty[c,t,p]<=1e6*(delta[c,p]);
# Added in orTools - 20220302
subject to Condition051 {c in C, t in Tc[c], p in P_dis}: y[c,t,p]<=0;
# Added in orTools - 20220302
subject to Condition052 {c in C diff C_locked, t in Tc[c], p in P : Vcp[c,p]==0}: y[c,t,p]=0;
# Added in orTools - 20220302
subject to Condition06 {c in C, t in Tc[c], p in Pbar diff {NP} }: qty[c,t,p] + y[c,t,p+1] = qty[c,t,p+1]; # amount of cargo c left in tank when leaving port p for port p+1 is equal to the amount of cargo c moved from/to tank t at port p.

## preloaded condition
# Added in orTools - 20220302
subject to condition22 {c in C_loaded, t in T_loaded}: x[c,t] = I_loaded[c,t]; # follow the existing stowage of preloaded cargoes
# Added in orTools - 20220302
subject to condition23 {c in C_loaded, t in T diff T_loaded}: x[c,t] = 0; # preloaded cargo can only be loaded to its corresponding preloaded tanks.

# Added in orTools - 20220302
subject to condition23a {c in C_loaded, t in T diff T_loaded, p in P}: y[c,t,p]=x[c,t]; # preloaded cargo can only be loaded to its corresponding preloaded tanks.
# Added in orTools - 20220302
subject to condition23b {c in C_loaded, t in T diff T_loaded, p in P}: qty[c,t,p]=x[c,t]; # preloaded cargo can only be loaded to its corresponding preloaded tanks.

# Added in orTools - 20220302
subject to condition24 {c in C, t in T}: qty[c,t,0] = Q0[c,t]; # follow the existing stowage of preloaded cargoes
# Added in orTools - 20220302
subject to condition24a {c in C_loaded diff C_loaded1, t in T_loaded, p in P diff fixCargoPort}: y[c,t,p] = V_loaded[c,t,p]; # follow the existing stowage of preloaded cargoes
# Added in orTools - 20220302
subject to condition24b {c in C_loaded1, t in T, p in fixCargoPort}: qty[c,t,p] = Q1[c,t,p]; # follow the existing stowage of preloaded cargoes


## locked tank / pre-allocated condition
# Added in orTools - 20220302
subject to condition25 {c in C_locked, t in T_locked}: x[c,t] = A_locked[c,t]; # follow the existing stowage of locked cargoes
# Added in orTools - 20220302
subject to condition26 {c in C_locked, t in T diff T_locked}: x[c,t] = 0; # locked cargo can only be loaded to its corresponding locked tanks.
# Added in orTools - 20220302
subject to condition26a {c in C_locked, t in T diff T_locked, p in P}: y[c,t,p]=x[c,t]; # locked cargo can only be loaded to its corresponding locked tanks.
# Added in orTools - 20220302
subject to condition26b {c in C_locked, t in T diff T_locked, p in P}: qty[c,t,p]=x[c,t]; # locked cargo can only be loaded to its corresponding locked tanks.
# Added in orTools - 20220302
subject to condition27 {c in C_locked, t in T_locked, p in P}: y[c,t,p] = V_locked[c,t,p]; # follow the existing stowage of locked cargoes


## capacity constraint 98% rule

# Added in orTools - 20220302
subject to Constr5a {c in C diff C_loaded diff C_locked, t in Tc[c], p in P_last_loading}: qty[c,t,p] <= upperBoundC[c,t]*capacityCargoTank[t]*x[c,t];
# commingled
# Added in orTools - 20220302
subject to Constr5b {k1 in Cm_1, k2 in Cm_2, t in T, p in P_last_loading}: qw[k1,t,p]/density_Cm[k1] + qw[k2,t,p]/density_Cm[k2] <= upperBound[t]*capacityCargoTank[t];
#subject to Constr5a {c in C diff C_loaded diff C_locked, t in Tc[c], p in P_last_loading}: q[c,t,p]*dcLow[c]/density_up[c] + tolerance*x[c,t]/density_up[c] <= upperBound[t]*gt[t]*x[c,t];
# Added in orTools - 20220302
subject to Constr5c {k1 in Cm_1, k2 in Cm_2}:sum{t in Tm} x[k1,t]*x[k2,t] <= 1; # limit commingle tank to 1

#subject to Constr5b1 {k1 in Cm_1, t in T, p in P_last_loading}: qw[k1,t,p]/density_Cm[k1]  <= 0.6*upperBound[t]*capacityCargoTank[t];
#subject to Constr5b2 {k2 in Cm_2, t in T, p in P_last_loading}: qw[k2,t,p]/density_Cm[k2]  <= 0.4*upperBound[t]*capacityCargoTank[t];

# manual commingle
# Added in orTools - 20220302
subject to Constr5d1 {k1 in Cm_1, k2 in Cm_2, t in Tm, p in P_last_loading}: x[k2,t]*Qm_2 - qw[k2,t,p] <= Mm*(1-x[k1,t]);
# Added in orTools - 20220302
subject to Constr5d2 {k1 in Cm_1, k2 in Cm_2, t in Tm, p in P_last_loading}:  qw[k2,t,p] - x[k2,t]*(Qm_2+Mm) <= Mm*(1-x[k1,t]);
# Added in orTools - 20220302
subject to Constr5d3 {k1 in Cm_1, k2 in Cm_2, t in Tm, p in P_last_loading}: x[k1,t]*Qm_1 - qw[k1,t,p] <= Mm*(1-x[k2,t]);
# Added in orTools - 20220302
subject to Constr5d4 {k1 in Cm_1, k2 in Cm_2, t in Tm, p in P_last_loading}:  qw[k1,t,p] - x[k1,t]*(Qm_1+Mm) <= Mm*(1-x[k2,t]);

## capacity constraint 60% rule
subject to Constr7a {c in C diff C_loaded diff C_locked, t in Tc[c], p in P_last_loading}: lowerBound[t]*x[c,t] <= qty[c,t,p];
# Added in orTools - 20220302
subject to Constr8 {c in C, t in Tc[c], p in P_last_loading}: qw2f[c,t,p]/1000 - 1e4*(x[c,t])<=0; ## newly added on 20190603

## capacity constraint high density cargo
#subject to Constr6a {c in C diff C_loaded diff C_locked, t in Tc[c], p in P_last_loading:highDensityOn*densityCargoTank[t]/densityCargo_High[c]<=1}: (q[c,t,p] + tolerance*x[c,t])*densityCargo_Low[c]/densityCargo_High[c] <= upperHighDensity[c,t]*capacityCargoTank[t]*x[c,t];

## ballast capacity constraint
# Added in orTools - 20220302
subject to Constr11 {t in TB, p in P_stable union P0}: yB[t,p] <= upperBoundB1[t]*capacityBallastTank[t]*xB[t,p];

## ballast capacity constraint
# Added in orTools - 20220302
subject to Constr12 {t in TB, p in P_stable union P0}: lowerBoundB1[t]*capacityBallastTank[t]*xB[t,p] <= yB[t,p];

## max num of tanks available
#subject to Constr12a: sum {t in T, c in C} x[c,t] <= maxTankUsed;
# Added in orTools - 20220302
subject to Constr12a1 {t in T}: sum {c in C} x[c,t] <=100*xt[t];
# Added in orTools - 20220302
subject to Constr12a2: sum{t in T} xt[t] <= maxTankUsed;


## load all  cargo
# Added in orTools - 20220302
subject to Condition111 {p in P_last_loading}: -intended <= sum{c in C, pp in P:Wcp[c,pp]>0}Wcp[c,pp]-sum{t in T, c in C}qw[c,t,p]<=intended;

## priority 1 and 2
# Added in orTools - 20220302
subject to Constr122{(c1,c2) in cargoPriority}: sum{t in Tc[c2], p in P_last_loading} qw[c2,t,p]/toLoad[c2] <= sum{t in Tc[c1], p in P_last_loading} qw[c1,t,p]/toLoad[c1];


## symmetric loading
# Added in orTools - 20220302
subject to Condition112a {c in C}: x[c,'1P'] = x[c,'1S'];
# Added in orTools - 20220302
subject to Condition112b {c in C}: x[c,'2P'] = x[c,'2S'];
# Added in orTools - 20220302
subject to Condition112c1 {c in C}: x[c,'3P'] = x[c,'3S'];
# Added in orTools - 20220302
subject to Condition112c2 {c in C}: x[c,'4P'] = x[c,'4S'];
# Added in orTools - 20220302
subject to Condition112c3 {c in C}: x[c,'5P'] = x[c,'5S'];
# Added in orTools - 20220302
subject to Condition112a1 {(u,v) in symmetricVolTank, p in P_last_loading}: sum{c in C}qw[c,u,p]/densityCargo_Low[c]/capacityCargoTank[u] - sum{c in C}qw[c,v,p]/densityCargo_Low[c]/capacityCargoTank[v] <= diffVol ;
# Added in orTools - 20220302
subject to Condition112a2 {(u,v) in symmetricVolTank, p in P_last_loading}:     -diffVol <= sum{c in C}qw[c,u,p]/densityCargo_Low[c]/capacityCargoTank[u] - sum{c in C}qw[c,v,p]/densityCargo_Low[c]/capacityCargoTank[v];

# equal weight in 1W, 2W, 4W, 5W
#subject to Condition112d1 {c in C_equal, p in P_stable2[c]}: qw[c,'1P',p] = qw[c,'1S',p];
#subject to Condition112d2 {c in C_equal, p in P_stable2[c]}: qw[c,'2P',p] = qw[c,'2S',p];
#subject to Condition112d3 {c in C_equal, p in P_stable2[c]}: qw[c,'4P',p] = qw[c,'4S',p];
#subject to Condition112d4 {c in C_equal, p in P_stable2[c]}: qw[c,'5P',p] = qw[c,'5S',p];
# Added in orTools - 20220302
subject to Condition112d1 {c in C_equal, p in P_stable2[c], (u,v) in equalWeightTank}: qw[c,u,p] = qw[c,v,p];

# only for discharging
# Added in orTools - 20220302
subject to Condition112d5 {c in C_equal, p in P_stable2[c]}: qw[c,'3P',p] = qw[c,'3S',p];
# qw > 0 ==> qwz == 1
# Added in orTools - 20220302
subject to Condition116a {(c, p) in P_opt, t in T} : qw[c,t,p] <= 1e5*qwz[c,t,p];

# diff cargos in slop tanks, except when only one cargo
#subject to Condition112f {c in C}: x[c,'SLS'] + x[c,'SLP'] <= diffSlop;
#subject to Condition112f1 {c in C}: x[c,'1P'] + x[c,'1C'] <= diffSlop;
#subject to Condition112f2 {c in C}: x[c,'2P'] + x[c,'2C'] <= diffSlop;
#subject to Condition112f3 {c in C}: x[c,'3P'] + x[c,'3C'] <= diffSlop;
#subject to Condition112f4 {c in C}: x[c,'4P'] + x[c,'4C'] <= diffSlop;
#subject to Condition112f5 {c in C}: x[c,'5P'] + x[c,'5C'] <= diffSlop;

# Added in orTools - 20220302
subject to Condition112f {c in C, (u,v) in cargoTankNonSym}: x[c,u] + x[c,v] <= diffSlop;

# slop tanks have to be used
# Added in orTools - 20220302
subject to Condition112g1 : sum{c in C_slop, t in slopP} x[c, t] = 1;
# Added in orTools - 20220302
subject to Condition112g2 : sum{c in C_slop, t in slopS} x[c, t] = 1;

# each row must have a the cargo for C_max, empty when only 1 cargo is loaded
# Added in orTools - 20220302
subject to Condition112h1 {c in C_max}: x[c,'1P'] + x[c,'1C'] >= 1;
# Added in orTools - 20220302
subject to Condition112h2 {c in C_max}: x[c,'2P'] + x[c,'2C'] >= 1;
# Added in orTools - 20220302
subject to Condition112h3 {c in C_max}: x[c,'3P'] + x[c,'3C'] >= 1;
# Added in orTools - 20220302
subject to Condition112h4 {c in C_max}: x[c,'4P'] + x[c,'4C'] >= 1;
# Added in orTools - 20220302
subject to Condition112h5 {c in C_max}: x[c,'5P'] + x[c,'5C'] >= 1;
# C_max cannot occupy 2 consecutive rows
# Added in orTools - 20220302
subject to Condition112i1 {c in C_max}: x[c,'1P'] + x[c,'1C'] + x[c,'1S'] + x[c,'2P'] + x[c,'2C'] + x[c,'2S'] <= 5;
# Added in orTools - 20220302
subject to Condition112i2 {c in C_max}: x[c,'2P'] + x[c,'2C'] + x[c,'2S'] + x[c,'3P'] + x[c,'3C'] + x[c,'3S'] <= 5;
# Added in orTools - 20220302
subject to Condition112i3 {c in C_max}: x[c,'3P'] + x[c,'3C'] + x[c,'3S'] + x[c,'4P'] + x[c,'4C'] + x[c,'4S'] <= 5;
# Added in orTools - 20220302
subject to Condition112i4 {c in C_max}: x[c,'4P'] + x[c,'4C'] + x[c,'4S'] + x[c,'5P'] + x[c,'5C'] + x[c,'5S'] <= 5;


# first discharge cargo
# Added in orTools - 20220302
subject to Condition112j {c in firstDisCargo, (u,v) in slopS cross slopP }: x[c,u] + x[c,v] >= 1;

##
subject to Condition117a {c in C, t in QWT[c], p in P_last_loading}:  0.98*QW[c,t] <= qw[c,t,p] <= QW[c,t]*1.02;
subject to Condition117b {c in C, t in QWT1[c], p in dischargePort}:  0.98*QW1[c,t,p] <= qw[c,t,p] <= QW1[c,t,p]*1.02;


##
# Added in orTools - 20220302
subject to Condition112b1 {t in T, c in C diff C_loaded diff C_locked, p in P_last_loading}: qw[c,t,p] >= minCargoAmt*x[c,t]; # link xB and wB
# Added in orTools - 20220302
subject to Condition112b2 {t in T, c in C diff C_loaded diff C_locked, p in P_last_loading}: qw[c,t,p] <= 1e5*x[c,t]; # link xB and wB

## ballast requirement
# Added in orTools - 20220302
subject to Condition113d1 {t in TB, p in P_stable union P0}: wB[t,p] >= minBallastAmt[t]*xB[t,p]; # loaded min ballast
# Added in orTools - 20220302
subject to Condition113d2 {t in TB, p in P_stable union P0}: wB[t,p] <= 1e4*xB[t,p]; # loaded min ballast
# Added in orTools - 20220302
subject to Condition113d3 {t in minTB, p in P_stable union P0}: wB[t,p] >= minBallastAmt[t]; # loaded min ballast


# initial ballast condition
#subject to Condition114a1 {t in incTB diff TB3}: wB[t,0] <= wB[t,firstloadingPort];
#subject to Condition114a2 {t in decTB diff TB3}: wB[t,0] >= wB[t,firstloadingPort];

subject to Condition114a3 {t in TBinit diff TB5}:  initBallast[t] = wB[t,0];
# decreasing ballast except last loading port
# Added in orTools - 20220302
subject to Condition114b {t in TB, (u,v) in loadingPortNotLast}: wB[t,u] >= wB[t,v];
# decreasing ballast tank
subject to Condition114c {(u,v) in depArrPort3}: -diffBallastAmt[u] <= sum{t in TB}wB[t,u] - sum{t in TB}wB[t,v] <= diffBallastAmt[u];
# depart and arrival has to use same tank
# Added in orTools - 20220302
subject to Condition114d2 {t in TB, (u,v) in depArrPort2}: wB[t,u] = wB[t,v]; # fixed ROB
# Added in orTools - 20220302
subject to Condition114d1 {t in TB diff TB3, (u,v) in depArrPort1}: wB[t,u] >= wB[t,v]; # non-zero ROB
# rotation loading ports
# Added in orTools - 20220302
subject to Condition114e1 {t in TB diff TB3, (u,v) in rotatingPort1}:  -wB[t,u] +  wB[t,v] <= 1e6*(1-zBa1[t]);
# Added in orTools - 20220302
subject to Condition114e2 {t in TB diff TB3, (u,v) in rotatingPort1}:    wB[t,u] -  wB[t,v] <= 1e6*(1-zBb1[t]);
# Added in orTools - 20220302
subject to Condition114e3 {t in TB diff TB3}: zBa1[t] + zBb1[t] = 1;
# Added in orTools - 20220302
subject to Condition114e4 {t in TB4, (u,v) in rotatingPort2}:  -wB[t,u] +  wB[t,v] <= 1e6*(1-zBa2[t]);
# Added in orTools - 20220302
subject to Condition114e5 {t in TB4, (u,v) in rotatingPort2}:    wB[t,u] -  wB[t,v] <= 1e6*(1-zBb2[t]);
# Added in orTools - 20220302
subject to Condition114e6 {t in TB4}: zBa2[t] + zBb2[t] = 1;

# fixed ballast
# Added in orTools - 20220302
subject to Condition114f1 {t in TB, p in fixBallastPort}:  B_locked[t,p] = wB[t,p];

# deballast amt
# Added in orTools - 20220302
subject to Condition114g1 {p in loadPort inter P_stable}: sum{t in TB0} wB[t,p] + deballastPercent*loadingPortAmt[p] >= sum{t in TB0} wB[t,p-1];
# ballast amt
# Added in orTools - 20220302
subject to Condition114g2 {p in dischargePort inter P_stable}: sum{t in TB} wB[t,p-1] + ballastPercent*dischargePortAmt[p] >= sum{t in TB} wB[t,p];

# equal weight ballast
# Added in orTools - 20220303
subject to Condition114j1 {p in P0}: wB['WB1P',p] = wB['WB1S',p];
# Added in orTools - 20220303
subject to Condition114j2 {p in P0}: wB['WB2P',p] = wB['WB2S',p];
# Added in orTools - 20220303
subject to Condition114j3 {p in P0}: wB['WB3P',p] = wB['WB3S',p];
# Added in orTools - 20220303
subject to Condition114j4 {p in P0}: wB['WB4P',p] = wB['WB4S',p];

# departure of last loading port
# Added in orTools - 20220303
subject to Condition114h {t in lastLoadingPortBallastBan, p in specialBallastPort}: xB[t, p] = 0;
# arrival of last loading port
# Added in orTools - 20220303
subject to Condition114h1 {t in TB, p in zeroBallastPort}: xB[t, p] = 0;

# banned ballast

subject to Condition114i1 {t in ballastBan, p in P_ban_ballast}: xB[t, p] = 0;


## LOADING
# Added in orTools - 20220303
subject to Condition115 {p in P}: sum{t in toDeballastTank} wB[t,p-1] - sum{t in toDeballastTank} wB[t,p] <= ballastLimit[p];

### ship stabilty ------------------------------------------------------------
# assume the ship satisfies all the stability conditions when entering the first port, and ballast tank allocation will be refreshed before leaving each port.
# Added in orTools - 20220407
subject to Constr17a {t in T, p in P union P0}: wC[t,p] = sum{c in C} qw[c,t,p] + onboard[t];


## draft constraint
# displacement
# Added in orTools - 20220407
subject to Constr13c1 {p in P union P0}: displacement[p] = sum{t in T} wC[t,p] + sum{t in TB} wB[t,p] + sum{t in OtherTanks} weightOtherTank[t,p] + lightWeight + deadweightConst;
# Added in orTools - 20220407
subject to Constr13c2 {p in P union P0}: displacement1[p] = displacement[p]*1.025/densitySeaWater[p];

# loading and unloading port
# Added in orTools - 20220407
subject to Constr13 {p in P_stable1 union P0}: displacementLowLimit[p]+0.001 <= displacement[p] <= displacementLimit[p]-0.001;

# deadweight constraint
# Added in orTools - 20220407
subject to Constr13a {p in P_stable}: sum{t in T} wC[t,p] + sum{t in TB} wB[t,p] + sum{t in OtherTanks} weightOtherTank[t,p] + deadweightConst <= deadweight;
# Added in orTools - 20220407
subject to Constr13b {p in P_last_loading}: sum{t in T} wC[t,p] <= cargoweight;
## New list constraint
#  ballast
# Added in orTools - 20220407
subject to Constr15b1 {t in TB diff TB1, p in P_stable union P0}: TB_tmom[t,p] = <<{s in 1..pwTCG-1} bTankTCG[s,t]; {s in 1..pwTCG} mTankTCG[s,t]>> wB[t,p];
# Added in orTools - 20220407
subject to Constr15b2 {t in TB1, p in P_stable union P0}: TB_tmom[t,p] = wB[t,p]*TCGt[t];
# cargo
# Added in orTools - 20220407
subject to Constr15c1 {t in T diff T1, p in P_stable union P0}: T_tmom[t,p] = <<{s in 1..pwTCG-1} bTankTCG[s,t]; {s in 1..pwTCG} mTankTCG[s,t]>> wC[t,p];
# Added in orTools - 20220407
subject to Constr15c2 {t in T1, p in P_stable union P0}: T_tmom[t,p] = wC[t,p]*TCGt[t];
# Added in orTools - 20220407
subject to Constr153 {p in P_stable union P0}: T_mom[p] = sum{t in T} T_tmom[t,p] + sum{t in TB } TB_tmom[t,p]  + sum{t in OtherTanks} weightOtherTank[t,p]*TCGtp[t,p] + deadweightConst*TCGdw;
# Added in orTools - 20220407
subject to Constr154 {p in P_stable union P0}: -ListMOM <= T_mom[p] <= ListMOM;
## Trim constraint
#  ballast
# Added in orTools - 20220407
subject to Constr16b1 {t in TB diff TB2, p in P_stable union P0}: TB_lmom[t,p] = 1000 * (<<{s in 1..pwLCG-1} bTankLCG[s,t]; {s in 1..pwLCG} mTankLCG[s,t]>> wB[t,p]);
# Added in orTools - 20220407
subject to Constr16b2 {t in TB2, p in P_stable union P0}: TB_lmom[t,p] = wB[t,p]*LCGt[t];
# Added in orTools - 20220407
#subject to Constr161 {p in P_stable}: L_mom[p] = sum{t in T} wC[t,p]*LCGt[t] + sum{t in TB} TB_lmom[t,p] + sum{t in OtherTanks} weightOtherTank[t,p]*LCGtp[t,p] + lightWeight*LCGship + deadweightConst*LCGdw;
# Added in orTools - 20220407
subject to Constr161 {p in P_stable union P0}: L_mom[p] = sum{t in T} wC[t,p]*LCGtport[t,p] + sum{t in TB} TB_lmom[t,p] + sum{t in OtherTanks} weightOtherTank[t,p]*LCGtp[t,p] + lightWeight*LCGship + deadweightConst*LCGdw;
# Added in orTools - 20220407
subject to Constr163 {p in P_stable union P0}: LCBp[p] = (<<{s in 1..pwLCB-1} bLCB[s]; {s in 1..pwLCB} mLCB[s]>> displacement1[p])*densitySeaWater[p]/1.025  + adjLCB;
# Added in orTools - 20220407
subject to Constr164 {p in P_stable union P0}: MTCp[p] = (<<{s in 1..pwMTC-1} bMTC[s]; {s in 1..pwMTC} mMTC[s]>> displacement1[p])*densitySeaWater[p]/1.025 + adjMTC;
# Added in orTools - 20220407
subject to Constr16a {p in P_stable union P0}: MTCp[p]*trim_lower[p]*100 <= L_mom[p] - LCBp[p] ;
# Added in orTools - 20220407
subject to Constr16b {p in P_stable union P0}: L_mom[p] - LCBp[p] <= MTCp[p]*trim_upper[p]*100;

## SF and BM 

# wn
# Added in orTools - 20220407
subject to Constr18a {p in P}: wn[0,p] = 0;
# Added in orTools - 20220407
subject to Constr18b {f in 1..Fr, p in P_stable}: wn[f,p] = wn[f-1,p] + sum {t in T} weightRatio_ct[f,t]*wC[t,p]/1000 + sum {t in TB} weightRatio_bt[f,t]*wB[t,p]/1000 + sum {t in OtherTanks} weightRatio_ot[f,t]*weightOtherTank[t,p]/1000; 
# mn
# Added in orTools - 20220407
subject to Constr19a {p in P}: mn[0,p] = 0;
# Added in orTools - 20220407
subject to Constr19b {f in 1..Fr, p in P_stable}: mn[f,p] = mn[f-1,p] + sum {t in T} LCG_ct[f,t]*weightRatio_ct[f,t]*wC[t,p]/1000 + sum {t in TB} LCG_bt[f,t]*weightRatio_bt[f,t]*wB[t,p]/1000 + sum {t in OtherTanks} LCG_ot[f,t]*weightRatio_ot[f,t]*weightOtherTank[t,p]/1000; 

# mean_draft=pwl(displacement)
# Added in orTools - 20220407
subject to Constr18d {p in P}: mean_draft[p] = <<{s in 1..pwDraft-1} bDraft[s]; {s in 1..pwDraft}mDraft[s]>> displacement[p] + adjMeanDraft;
# Added in orTools - 20220407
#subject to Condition200a {p in P_stable}: est_trim[p] = (trim_upper[p]+trim_lower[p])/2;
# Added in orTools - 20220407
subject to  Condition200a {p in P_stable}: est_trim[p] = ave_trim[p];

# SF -> zero trim
# Added in orTools - 20220407
subject to Condition20a2 {f in 1..Fr, p in P_stable union P0}: SS[f,p] = BV_SF[f,p] + CD_SF[f,p]*(mean_draft[p]+draft_corr[p]-base_draft[p]) + CT_SF[f,p]*est_trim[p];
# Added in orTools - 20220407
subject to Condition20a1 {f in 1..Fr, p in P_stable union P0}: SS[f,p] = BV_SF[f,p] + CD_SF[f,p]*(mean_draft[p]+0.5*est_trim[p]+draft_corr[p]-base_draft[p]) + CT_SF[f,p]*est_trim[p];
# Added in orTools - 20220407
subject to Condition20b {f in 1..Fr, p in P_stable union P0}: lowerSFlimit[f] <= SS[f,p]- wn[f,p];
# Added in orTools - 20220407
subject to Condition20c {f in 1..Fr, p in P_stable union P0}: SS[f,p] - wn[f,p] <= upperSFlimit[f];

# BM -> -> zero trim
# Added in orTools - 20220407
subject to Condition21a2 {f in 1..Fr, p in P_stable union P0}: SB[f,p] = BV_BM[f,p] + CD_BM[f,p]*(mean_draft[p]+draft_corr[p]-base_draft[p]) + CT_BM[f,p]*est_trim[p];
# Added in orTools - 20220407
subject to Condition21a1 {f in 1..Fr, p in P_stable union P0}: SB[f,p] = BV_BM[f,p] + CD_BM[f,p]*(mean_draft[p]+0.5*est_trim[p]+draft_corr[p]-base_draft[p]) + CT_BM[f,p]*est_trim[p];
# Added in orTools - 20220407
subject to Condition21b {f in 1..Fr, p in P_stable union P0}: lowerBMlimit[f] <= wn[f,p]*LCG_fr[f] + mn[f,p] - SB[f,p];
# Added in orTools - 20220407
subject to Condition21c {f in 1..Fr, p in P_stable union P0 diff P_bm}: wn[f,p]*LCG_fr[f] + mn[f,p] -  SB[f,p] <= upperBMlimit[f];












