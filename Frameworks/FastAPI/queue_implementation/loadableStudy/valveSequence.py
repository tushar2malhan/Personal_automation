import json
import pandas as pd
import numpy as np


class Constants:
    def __init__(self):
        self.EVENTS = 'events'
        self.SEQUENCE = 'sequence'
        self.TIMEEND = 'timeEnd'
        self.TIMESTART = 'timeStart'
        self.SLOPDISCHARGE = 'slopDischarge'
        self.COWSTRIPPING = 'COWStripping'
        self.REDUCEDRATE = 'reducedRate'
        self.FINALSTRIPPING = 'finalStripping'
        self.START = 'start'
        self.END = 'end'
        self.MID = 'mid'
        self.RATE = 'rate'
        self.CLEANING = 'Cleaning'
        self.stages = ['stage', self.TIMESTART]
        self.SIMCARGODISCHARGE_KEY = 'simCargoDischargingRatePerTankM3_Hr'
        self.TANKSHORTNAME = 'tankShortName'
        self.TANKOPEN = 'TankOpen'
        self.TANKCLOSE = 'TankClose'
        self.OPEN = 'open'
        self.CLOSE = 'close'
        self.FULLCLEAN = 'FullClean'
        self.TANKSTRIPOPEN = 'Tso'
        self.TANKSTRIPCLOSE = 'Tsc'
        self.TANKCOWOPEN = 'Tco'
        self.TANKCOWCLOSE = 'Tcc'
        self.FILLINGUPTCP = 'FillingUpOfTCP'
        self.WARMTCP = 'WarmTCP'
        self.DRAINTCLINE = 'TCline'
        self.cow_strip_operation_time_map = {}
        self.cow_strip_operation_time_map[self.FILLINGUPTCP] = 30
        self.cow_strip_operation_time_map[self.WARMTCP] = 28
        self.final_strip_operation_time_map = {}
        self.final_strip_operation_time_map[self.DRAINTCLINE] = 40
        self.TANKOPEN_TIMELINE = 17
        self.ops_arr = ['floodSeparator','warmPumps','initialRate','FillingUpOfTCP','WarmTCP','COWStripping','COWStripping_end',
           'dryCheck','slopDischarge_start','slopDischarge_end','slopDischarge_mid','finalStripping','finalStripping_mid','TCline','finalStripping_end']
        self.ops_abbr_dict={}
        self.ops_abbr_dict['floodSeparator'] = 'FS'
        self.ops_abbr_dict['warmPumps'] = 'WP'
        self.ops_abbr_dict['initialRate'] = 'PCOP'
        self.ops_abbr_dict['FillingUpOfTCP'] = 'FTCP'
        self.ops_abbr_dict['WarmTCP'] = 'WTCP'
        self.ops_abbr_dict['COWStripping'] = 'COWS'
        self.ops_abbr_dict['COWStripping_end'] = 'COWE'
        self.ops_abbr_dict['dryCheck'] = 'DC'
        self.ops_abbr_dict['slopDischarge_start'] = 'SDstart'
        self.ops_abbr_dict['slopDischarge_end'] = 'SDend'
        self.ops_abbr_dict['slopDischarge_mid'] = 'SDmid'
        self.ops_abbr_dict['finalStripping'] = 'FStrip'
        self.ops_abbr_dict['TCline'] = 'FStripmid'
        self.ops_abbr_dict['finalStripping_end'] = 'FStripend'
        self.START_OPERATIONS = ['COWS', 'SDstart', 'FStrip', 'FStripmid']
        self.END_OPERATIONS = ['COWE', 'SDend', 'FStripend']

        # valve category name
        self.BALLAST_TANK_NAME = 'BALLLAST VALVES'
        self.BALLAST_PUMP_NAME = 'Ballast Pump'
        self.CARGO_TANK_NAME = 'CARGO PIPE LINE VALVES'
        self.MANIFOLD_NAME = 'MANIFOLD GATE VALVE'
        self.BALLAST_STRIP_TANK_NAME = "STRIPPER SUCTION VALVE"
        self.BALLAST_EDUCTOR_NAME = ["EDUCTOR DRIVE VALVE", "EDUCTOR SUCTION VALVE", "EDUCTOR DISCHARGE VALVE"]
        # Parameters
        self.BALLAST_TANKS = ['LFPT', 'WB1P', 'WB1S', 'WB2P', 'WB2S', 'WB3P', 'WB3S', 'WB4P', 'WB4S', 'WB5P', 'WB5S']
        self.BALLAST_MAP = {'pump': {"4": 'BP1', "5": 'BP2'},
                            'eductor': {"10": 'Ballast Eductor 1', "11": 'Ballast Eductor 2'}}

        # valve variable/operation
        self.VALVE_TYPE_VARIABLE = 'valveTypeName'
        self.PUMP_TYPE_VARIABLE = 'pumpType'
        self.VALVE_OP_VARIABLE = 'operation'
        self.VALVE_NAME_VARIABLE = 'valveNumber'
        self.PUMP_NAME_VARIABLE = 'pumpCode'
        self.MANIFOLD_NAME_VARIABLE = 'manifoldName'
        self.MANIFOLD_SIDE_VARIABLE = 'manifoldSide'
        self.VALVE = 'valve'
        self.PUMP = 'pump'
        self.EDUCTOR = 'eductor'
        self.RATEM3 = 'rateM3_Hr'
        self.TANK = 'tank'
        self.STAGE = 'stage'
        self.SHUT = 'shut'
        self.GRAVITY = 'Gravity'
        self.CARGO = 'Cargo'
        self.LOADINGINFO = "loadingInformation"
        self.MACHINERYINUSES = "machineryInUses"
        self.LOADINGMACHINEINUSES = "loadingMachinesInUses"
        self.MACHINETYPENAME = "machineTypeName"
        self.MACHINENAME = "machineName"
        self.TANKTYPENAME = "tankTypeName"
        self.MANIFOLD = "MANIFOLD"

        # cargo stages/sequences
        self.INITIAL = 'initialCondition'
        self.OPENSINGLETANK = 'openSingleTank'
        self.INITIALRATE = 'initialRate'
        self.OPENALLTANKS = 'openAllTanks'
        self.INCREASETOMAXRATE = 'increaseToMaxRate'
        self.LOADINGATMAXRATE = 'loadingAtMaxRate'
        self.TOPPING = 'topping'
        self.LOADING_STAGES = [self.INITIAL, self.OPENSINGLETANK, self.INITIALRATE, self.OPENALLTANKS,
                               self.INCREASETOMAXRATE,
                               self.LOADINGATMAXRATE, self.TOPPING]

        # valve sequences
        self.BALLAST_GRAVITY = 'ballastingByGravity'
        self.BALLAST_FLOOD = 'floodingOfBallastPumpBeforeBallasting'
        self.BALLAST_PUMP_GRAVITY = 'ballastingByPumpsAfterGravity'
        self.BALLAST_PUMP = 'startingOfBallastingByPumpsWhenNoGravity'
        self.BALLAST_STS = 'seaToSea'
        self.BALLAST_SHUT = 'shuttingSequence'
        self.BALLAST_TANK_OPEN = 'openBallastTank'
        self.BALLAST_TANK_CLOSE = 'closeBallastTank'
        self.BALLAST_PUMP_OPEN = 'openBallastPump'
        self.BALLAST_PUMP_CLOSE = 'closeBallastPump'
        self.BALLAST_OPS = 'ballast'

        self.DEBALLAST_GRAVITY = 'startOfDeballasingByGravity'
        self.DEBALLAST_FLOOD = 'floodingTheBallastPump'
        self.DEBALLAST_PUMP_GRAVITY = 'debalastingByPumpAfterGravity'
        self.DEBALLAST_PUMP = 'startingOfDeballastingByPumpsWhenNoGravity'
        self.DEBALLAST_STSP = 'seaToSea'
        self.DEBALLAST_EDUCTOR = 'strippingByEductor'
        self.DEBALLAST_STSE = 'seaTosea'
        self.DEBALLAST_SHUT = 'shuttingSequence'
        self.DEBALLAST_OPS = 'deballast'

        self.LOADING_SINGLE = 'startOfLoading'
        self.LOADING_ALL = 'fullLoadingRate'
        self.LOADING_TOPPING = 'toppingOff'
        self.LOADING_SHUT = 'shuttingSequence'
        self.CARGO_TANK_OPEN = 'openCargoTank'
        self.CARGO_TANK_CLOSE = 'closeCargoTank'
        self.LOADING_OPS = 'loading'

        # ATTRIBUTE NAME IN FINAL JSON
        self.VALVES_JSON = 'valves'
        self.TIME_JSON = 'time'
        self.OP_JSON = 'operation'

        self.SIMCARGOLOADING_KEY = "simCargoLoadingRatePerTankM3_Hr"
        self.SIMBALLASTING_KEY = "simBallastingRateM3_Hr"
        self.SIMDEBALLASTING_KEY = "simDeballastingRateM3_Hr"
        self.BALLAST_KEY = 'ballast'
        self.EDUCTION_KEY = 'eduction'
        self.PUMP_VARIABLE = 'pumpSelected'
        self.BALLASTPUMP_VARIABLE = 'ballastPumpSelected'
        self.PUMPNAME_VARIABLE = 'pumpName'

        self.ops_abbr_dict['ballast'] = {}
        self.ops_abbr_dict['ballast']['ballastingByGravity'] = 'BG'
        self.ops_abbr_dict['ballast']['floodingOfBallastPumpBeforeBallasting'] = 'FBP'
        self.ops_abbr_dict['ballast']['ballastingByPumpsAfterGravity'] = 'BPG'
        self.ops_abbr_dict['ballast']['startingOfBallastingByPumpsWhenNoGravity'] = 'BPWG'
        self.ops_abbr_dict['ballast']['seaToSea'] = 'STSP'
        self.ops_abbr_dict['ballast']['shuttingSequence'] = 'SB'
        self.ops_abbr_dict['ballast']['openBallastTank'] = 'WBTO'
        self.ops_abbr_dict['ballast']['closeBallastTank'] = 'WBTC'
        self.ops_abbr_dict['ballast']['openBallastPump'] = 'BPO'
        self.ops_abbr_dict['ballast']['closeBallastPump'] = 'BPC'

        self.ops_abbr_dict['deballast'] = {}
        self.ops_abbr_dict['deballast']['startOfDeballasingByGravity'] = 'DG'
        self.ops_abbr_dict['deballast']['floodingTheBallastPump'] = 'DFBP'
        self.ops_abbr_dict['deballast']['debalastingByPumpAfterGravity'] = 'DPG'
        self.ops_abbr_dict['deballast']['startingOfDeballastingByPumpsWhenNoGravity'] = 'DPWG'
        self.ops_abbr_dict['deballast']['seaToSea'] = 'DSTSP'
        self.ops_abbr_dict['deballast']['strippingByEductor'] = 'DSE'
        self.ops_abbr_dict['deballast']['seaTosea'] = 'STSE'
        self.ops_abbr_dict['deballast']['shuttingSequence'] = 'SD'
        self.ops_abbr_dict['deballast']['openBallastTank'] = 'WBTO'
        self.ops_abbr_dict['deballast']['closeBallastTank'] = 'WBTC'
        self.ops_abbr_dict['deballast']['openBallastPump'] = 'BPO'
        self.ops_abbr_dict['deballast']['closeBallastPump'] = 'BPC'

        self.ops_abbr_dict['loading'] = {}
        self.ops_abbr_dict['loading']['startOfLoading'] = 'OST'
        self.ops_abbr_dict['loading']['fullLoadingRate'] = 'OAT'
        self.ops_abbr_dict['loading']['shuttingSequence'] = 'SL'
        self.ops_abbr_dict['loading']['openCargoTank'] = 'CTO'
        self.ops_abbr_dict['loading']['closeCargoTank'] = 'CTC'


# Loading
# Valve filter class to filter valves of a particular type
class ValveFilters:
    def __init__(self, constants):
        self.constants = constants

    # Filter for generic valves with no specific requirements
    def no_filter(self, valve_seq, seqno):
        valves = []
        for valve in valve_seq:
            valveName = valve[self.constants.VALVE_NAME_VARIABLE]
            valveOpen = self.constants.CLOSE if valve[
                self.constants.SHUT] else self.constants.OPEN  # close or open valve
            value = {self.constants.VALVE: valveName, self.constants.VALVE_OP_VARIABLE: valveOpen}
            valves.append(value)
        return valves

    # Filter for ballast pump valves for specifc pumps
    def ballast_pump_filter(self, valve_seq, pumps, seqno):
        pumpValves = []
        for valve in valve_seq:
            valveName = valve[self.constants.PUMP_NAME_VARIABLE]
            valveOpen = self.constants.CLOSE if valve[
                self.constants.SHUT] else self.constants.OPEN  # close or open pump
            if valveName in pumps:  # filter for specific pumps
                value = {self.constants.VALVE: valveName, self.constants.VALVE_OP_VARIABLE: valveOpen}
                pumpValves.append(value)
        return pumpValves

    # Filter for ballast tank valves for specifc tanks
    def ballast_tank_filter(self, valve_seq, tanks, seqno):
        tankValves = []
        for valve in valve_seq:
            valveName = valve[self.constants.VALVE_NAME_VARIABLE]
            valveOpen = self.constants.CLOSE if valve[
                self.constants.SHUT] else self.constants.OPEN  # close or open tank
            tankName = valve[self.constants.TANKSHORTNAME]
            if tankName in tanks:  # filter for specific tanks
                value = {self.constants.VALVE: valveName, self.constants.TANK: tankName,
                         self.constants.VALVE_OP_VARIABLE: valveOpen}
                tankValves.append(value)
        return tankValves

    # Filter for deballast strip tank valves for specifc tanks
    def ballast_strip_tank_filter(self, valve_seq, tanks, seqno):
        stripTankValves = []
        for valve in valve_seq:
            valveName = valve[self.constants.VALVE_NAME_VARIABLE]
            valveOpen = self.constants.CLOSE if valve[
                self.constants.SHUT] else self.constants.OPEN  # close or open tank
            tankName = valve[self.constants.TANKSHORTNAME]
            if tankName in tanks:  # filter for specific tanks
                value = {self.constants.VALVE: valveName, self.constants.TANK: tankName,
                         self.constants.VALVE_OP_VARIABLE: valveOpen}
                stripTankValves.append(value)
        return stripTankValves

    # Filter for deballast eductor related valves for specifc tanks
    def ballast_eductor_filter(self, valve_seq, eductor, seqno):
        eductorValves = []
        for valve in valve_seq:
            valveName = valve[self.constants.VALVE_NAME_VARIABLE]
            valveOpen = self.constants.CLOSE if valve[
                self.constants.SHUT] else self.constants.OPEN  # close or open tank
            eductorCheck = sum(
                [str(i) in valveName for i in eductor])  # If valve corresponds to any of the ballast eductor being used
            if eductorCheck:
                value = {self.constants.VALVE: valveName, self.constants.VALVE_OP_VARIABLE: valveOpen}
                eductorValves.append(value)
        return eductorValves

    # Filter for cargo tank valves for specifc tanks
    def cargo_tank_filter(self, valve_seq, tanks, seqno):
        tankValves = []
        for valve in valve_seq:
            valveName = valve[self.constants.VALVE_NAME_VARIABLE]
            valveOpen = self.constants.CLOSE if valve[
                self.constants.SHUT] else self.constants.OPEN  # close or open tank
            tankName = valve[self.constants.TANKSHORTNAME]
            if tankName in tanks:  # filter for specific tanks
                value = {self.constants.VALVE: valveName, self.constants.TANK: tankName,
                         self.constants.VALVE_OP_VARIABLE: valveOpen}
                tankValves.append(value)
        return tankValves

    # Filter for manifold valves for specifc pipelines and side(port/stbd)
    def manifold_filter(self, valve_seq, pipelines, side, seqno):
        tankValves = []
        for valve in valve_seq:
            valveName = valve[self.constants.VALVE_NAME_VARIABLE]
            valveOpen = self.constants.CLOSE if valve[
                self.constants.SHUT] else self.constants.OPEN  # close or open tank
            lineCheck = sum([str(i) in valve[self.constants.MANIFOLD_NAME_VARIABLE] for i in
                             pipelines]) > 0  # If valve corresponds to any of the manifold pipeline connection
            sideCheck = (
                        side.lower() in valve[self.constants.MANIFOLD_SIDE_VARIABLE].lower())  # port/stbd side manifold
            if sideCheck & lineCheck:
                value = {self.constants.VALVE: valveName, self.constants.VALVE_OP_VARIABLE: valveOpen}
                tankValves.append(value)
        return tankValves


class ValveOperations:
    def __init__(self, filters, vessel_json, constants):
        self.vfilters = filters
        self.constants = constants
        self.vessel_json = vessel_json

        # Operations
        self.key_operation_mapping = {}
        # BALLAST
        ops = self.constants.ops_abbr_dict[self.constants.BALLAST_OPS]
        self.key_operation_mapping[ops[self.constants.BALLAST_GRAVITY]] = self.ballast_gravity_operation
        self.key_operation_mapping[ops[self.constants.BALLAST_FLOOD]] = self.ballast_flood_pump_operation
        self.key_operation_mapping[ops[self.constants.BALLAST_PUMP_GRAVITY]] = self.ballast_pump_after_gravity_operation
        self.key_operation_mapping[ops[self.constants.BALLAST_PUMP]] = self.ballast_pump_wo_gravity_operation
        self.key_operation_mapping[ops[self.constants.BALLAST_STS]] = self.sea_to_sea_pump_operation
        self.key_operation_mapping[ops[self.constants.BALLAST_SHUT]] = self.ballast_shut_operation
        # BALLAST/DEBALLAST
        self.key_operation_mapping[ops[self.constants.BALLAST_TANK_OPEN]] = self.WBT_open_operation
        self.key_operation_mapping[ops[self.constants.BALLAST_TANK_CLOSE]] = self.WBT_close_operation
        self.key_operation_mapping[ops[self.constants.BALLAST_PUMP_OPEN]] = self.BP_open_operation
        self.key_operation_mapping[ops[self.constants.BALLAST_PUMP_CLOSE]] = self.BP_close_operation
        # DEBALLAST
        ops = self.constants.ops_abbr_dict[self.constants.DEBALLAST_OPS]
        self.key_operation_mapping[ops[self.constants.DEBALLAST_GRAVITY]] = self.deballast_gravity_operation
        self.key_operation_mapping[ops[self.constants.DEBALLAST_FLOOD]] = self.deballast_flood_pump_operation
        self.key_operation_mapping[
            ops[self.constants.DEBALLAST_PUMP_GRAVITY]] = self.deballast_pump_after_gravity_operation
        self.key_operation_mapping[ops[self.constants.DEBALLAST_PUMP]] = self.deballast_pump_wo_gravity_operation
        self.key_operation_mapping[ops[self.constants.DEBALLAST_STSP]] = self.deballast_sea_to_sea_pump_operation
        self.key_operation_mapping[ops[self.constants.DEBALLAST_EDUCTOR]] = self.deballast_stripping_eductor_operation
        self.key_operation_mapping[ops[self.constants.DEBALLAST_STSE]] = self.deballast_sea_to_sea_eductor_operation
        self.key_operation_mapping[ops[self.constants.DEBALLAST_SHUT]] = self.deballast_shut_operation
        # LOADING
        ops = self.constants.ops_abbr_dict[self.constants.LOADING_OPS]
        self.key_operation_mapping[ops[self.constants.LOADING_SINGLE]] = self.open_single_tank_operation
        self.key_operation_mapping[ops[self.constants.LOADING_ALL]] = self.open_all_tank_operation
        self.key_operation_mapping[ops[self.constants.CARGO_TANK_OPEN]] = self.CT_open_operation
        self.key_operation_mapping[ops[self.constants.CARGO_TANK_CLOSE]] = self.CT_close_operation
        self.key_operation_mapping[ops[self.constants.LOADING_SHUT]] = self.shutting_loading_operation
        self.valves = self.vessel_json['vessel']['vesselValveSequence']

        # BALLAST
        self.ballast_gravity = self.valves[self.constants.BALLAST_OPS][self.constants.BALLAST_GRAVITY]
        self.ballast_flood_pump = self.valves[self.constants.BALLAST_OPS][self.constants.BALLAST_FLOOD]
        self.ballast_pump_after_gravity = self.valves[self.constants.BALLAST_OPS][self.constants.BALLAST_PUMP_GRAVITY]
        self.ballast_pump_wo_gravity = self.valves[self.constants.BALLAST_OPS][self.constants.BALLAST_PUMP]
        self.sea_to_sea_pump = self.valves[self.constants.BALLAST_OPS][self.constants.BALLAST_STS]
        self.ballast_shut = self.valves[self.constants.BALLAST_OPS][self.constants.BALLAST_SHUT]
        # BALLAST/DEBALLAST
        self.WBT_open = self.extractBallastTankValves(self.ballast_gravity)
        self.WBT_close = self.extractBallastTankValves(self.ballast_gravity)
        self.BP_open = self.extractBallastPumpValves(self.ballast_pump_after_gravity)
        self.BP_close = self.extractBallastPumpValves(self.ballast_pump_after_gravity)
        # DEBALLAST
        self.deballast_gravity = self.valves[self.constants.DEBALLAST_OPS][self.constants.DEBALLAST_GRAVITY]
        self.deballast_flood_pump = self.valves[self.constants.DEBALLAST_OPS][self.constants.DEBALLAST_FLOOD]
        self.deballast_pump_after_gravity = self.valves[self.constants.DEBALLAST_OPS][
            self.constants.DEBALLAST_PUMP_GRAVITY]
        self.deballast_pump_wo_gravity = self.valves[self.constants.DEBALLAST_OPS][self.constants.DEBALLAST_PUMP]
        self.deballast_sea_to_sea_pump = self.valves[self.constants.DEBALLAST_OPS][self.constants.DEBALLAST_STSP]
        self.deballast_stripping_eductor = self.valves[self.constants.DEBALLAST_OPS][self.constants.DEBALLAST_EDUCTOR]
        self.deballast_sea_to_sea_eductor = self.valves[self.constants.DEBALLAST_OPS][self.constants.DEBALLAST_STSE]
        self.deballast_shut = self.valves[self.constants.DEBALLAST_OPS][self.constants.DEBALLAST_SHUT]
        # LOADING
        self.open_single_tank = self.valves[self.constants.LOADING_OPS][self.constants.LOADING_SINGLE]
        self.open_all_tank = self.valves[self.constants.LOADING_OPS][self.constants.LOADING_ALL]
        self.CT_open = self.valves[self.constants.LOADING_OPS][self.constants.LOADING_TOPPING]
        self.CT_close = self.valves[self.constants.LOADING_OPS][self.constants.LOADING_TOPPING]
        self.shutting_loading = self.valves[self.constants.LOADING_OPS][self.constants.LOADING_SHUT]

    # Get ballast tank valve sequence given a dictionary of different sequences
    def extractBallastTankValves(self, sequence):
        tank_valves = {idx: seq for idx, seq in sequence.items() if
                       seq[0][self.constants.VALVE_TYPE_VARIABLE] == self.constants.BALLAST_TANK_NAME}
        return tank_valves

    # Get ballast pump valve sequence given a dictionary of different sequences
    def extractBallastPumpValves(self, sequence):
        pump_valves = {idx: seq for idx, seq in sequence.items() if
                       seq[0][self.constants.PUMP_TYPE_VARIABLE] == self.constants.BALLAST_PUMP_NAME}
        return pump_valves

    # Get cargo tank valve sequence given a dictionary of different sequences
    def extractCargoTankValves(self, sequence):
        tank_valves = {idx: seq for idx, seq in sequence.items() if
                       seq[0][self.constants.VALVE_TYPE_VARIABLE] == self.constants.CARGO_TANK_NAME}
        return tank_valves

    def getManifoldParameters(self, json):
        lines = []
        side = ''
        machines = json[self.constants.LOADINGINFO][self.constants.MACHINERYINUSES][self.constants.LOADINGMACHINEINUSES]
        for i in machines:
            if i[self.constants.MACHINETYPENAME] == self.constants.MANIFOLD:
                lines.append(int(i[self.constants.MACHINENAME][-1]))
                side = i[self.constants.TANKTYPENAME]
        self.MANIFOLD = lines
        self.SIDE = side

    ###### BALLAST ######

    # Ballasting by gravity operation with tank valves filters
    def ballast_gravity_operation(self, time, time_dict):
        tank_filter = self.vfilters.ballast_tank_filter
        no_filter = self.vfilters.no_filter

        operation_valves = []
        for idx, seq in self.ballast_gravity.items():  # loop through sequence and get filtered valves
            count = str(idx.split('_')[1])
            if seq[0][self.constants.VALVE_TYPE_VARIABLE] == self.constants.BALLAST_TANK_NAME:
                tanks = time_dict[time][self.constants.OPEN]
                valves = tank_filter(seq, tanks, count)  # ballast tank filter
            else:
                valves = no_filter(seq, count)  # no filter, take all valves
            operation_valves += valves
        return operation_valves

    # Flooding ballast pump operation for ballasting with no filters
    def ballast_flood_pump_operation(self, time, time_dict):
        no_filter = self.vfilters.no_filter

        operation_valves = []
        for idx, seq in self.ballast_flood_pump.items():  # loop through sequence and get filtered valves
            count = str(idx.split('_')[1])
            valves = no_filter(seq, count)  # no filter, take all valves
            operation_valves += valves
        return operation_valves

    # ballasting by pump after gravity with pump filters
    def ballast_pump_after_gravity_operation(self, time, time_dict):
        pump_filter = self.vfilters.ballast_pump_filter
        no_filter = self.vfilters.no_filter

        operation_valves = []
        for idx, seq in self.ballast_pump_after_gravity.items():  # loop through sequence and get filtered valves
            count = str(idx.split('_')[1])
            if seq[0][self.constants.PUMP_TYPE_VARIABLE] == self.constants.BALLAST_PUMP_NAME:
                pumps = [i for i in time_dict[time][self.constants.OPEN] if
                         i in self.constants.BALLAST_MAP[self.constants.PUMP].values()]
                valves = pump_filter(seq, pumps, count)  # ballast pump fiter
            else:
                valves = no_filter(seq, count)  # no filter, take all valves
            operation_valves += valves
        return operation_valves

    # ballasting by pump without gravity with pump filters
    def ballast_pump_wo_gravity_operation(self, time, time_dict):
        pump_filter = self.vfilters.ballast_pump_filter
        tank_filter = self.vfilters.ballast_tank_filter
        no_filter = self.vfilters.no_filter

        operation_valves = []
        for idx, seq in self.ballast_pump_wo_gravity.items():  # loop through sequence and get filtered valves
            count = str(idx.split('_')[1])
            if seq[0][self.constants.VALVE_TYPE_VARIABLE] == self.constants.BALLAST_TANK_NAME:
                tanks = time_dict[time][self.constants.OPEN]
                valves = tank_filter(seq, tanks, count)  # ballast tank filter
            elif seq[0][self.constants.PUMP_TYPE_VARIABLE] == self.constants.BALLAST_PUMP_NAME:
                pumps = [i for i in time_dict[time][self.constants.OPEN] if
                         i in self.constants.BALLAST_MAP[self.constants.PUMP].values()]
                valves = pump_filter(seq, pumps, count)  # ballast pump filter
            else:
                valves = no_filter(seq, count)  # no filter, take all valves
            operation_valves += valves
        return operation_valves

    # ballasting sea to sea operation for pumps with pump filters
    def sea_to_sea_pump_operation(self, time, time_dict):
        tank_filter = self.vfilters.ballast_tank_filter
        no_filter = self.vfilters.no_filter

        operation_valves = []
        for idx, seq in self.sea_to_sea_pump.items():  # loop through sequence and get filtered valves
            count = str(idx.split('_')[1])
            if seq[0][self.constants.VALVE_TYPE_VARIABLE] == self.constants.BALLAST_TANK_NAME:
                if time in time_dict:
                    tanks = time_dict[time][self.constants.CLOSE]
                    valves = tank_filter(seq, tanks, count)  # ballast tank filter
            else:
                valves = no_filter(seq, count)  # no filter, take all valves
            operation_valves += valves
        return operation_valves

    # ballasting shutting operation with pump filters
    def ballast_shut_operation(self, time, time_dict):
        pump_filter = self.vfilters.ballast_pump_filter
        no_filter = self.vfilters.no_filter

        operation_valves = []
        for idx, seq in self.ballast_shut.items():  # loop through sequence and get filtered valves
            count = str(idx.split('_')[1])
            if seq[0][self.constants.PUMP_TYPE_VARIABLE] == self.constants.BALLAST_PUMP_NAME:
                pumps = [i for i in time_dict[time][self.constants.CLOSE] if
                         i in self.constants.BALLAST_MAP[self.constants.PUMP].values()]
                valves = pump_filter(seq, pumps, count)  # ballast pump filter
            else:
                valves = no_filter(seq, count)  # no filter, take all valves
            operation_valves += valves
        return operation_valves

    ###### DEBALLAST/BALLAST ######

    # water ballast tank opening operation with tank filters
    def WBT_open_operation(self, time, time_dict):
        tank_filter = self.vfilters.ballast_tank_filter

        operation_valves = []
        for idx, seq in self.WBT_open.items():
            count = -1
            if seq[0][self.constants.VALVE_TYPE_VARIABLE] == self.constants.BALLAST_TANK_NAME:
                tanks = time_dict[time][self.constants.OPEN]
                valves = tank_filter(seq, tanks, count)  # ballast tank filter
                for v in valves:
                    v[
                        self.constants.VALVE_OP_VARIABLE] = self.constants.OPEN  # ensure all ballast tank valve operation is open
                operation_valves += valves
        return operation_valves

    # water ballast tank closing operation with tank filters
    def WBT_close_operation(self, time, time_dict):
        tank_filter = self.vfilters.ballast_tank_filter

        operation_valves = []
        for idx, seq in self.WBT_close.items():
            count = -1
            if seq[0][self.constants.VALVE_TYPE_VARIABLE] == self.constants.BALLAST_TANK_NAME:
                tanks = time_dict[time][self.constants.CLOSE]
                valves = tank_filter(seq, tanks, count)  # ballast tank filter
                for v in valves:
                    v[
                        self.constants.VALVE_OP_VARIABLE] = self.constants.CLOSE  # ensure all ballast tank valve operation is close
                operation_valves += valves
        return operation_valves

    # ballast pump opening operation with pump filters
    def BP_open_operation(self, time, time_dict):
        pump_filter = self.vfilters.ballast_pump_filter

        operation_valves = []
        for idx, seq in self.BP_open.items():
            count = -1
            if seq[0][self.constants.PUMP_TYPE_VARIABLE] == self.constants.BALLAST_PUMP_NAME:
                pumps = [i for i in time_dict[time][self.constants.OPEN] if
                         i in self.constants.BALLAST_MAP[self.constants.PUMP].values()]
                valves = pump_filter(seq, pumps, count)  # ballast pump filter
                for v in valves:
                    v[
                        self.constants.VALVE_OP_VARIABLE] = self.constants.OPEN  # ensure all ballast pump valve operation is open
                operation_valves += valves
        return operation_valves

    # ballast pump closing operation with pump filters
    def BP_close_operation(self, time, time_dict):
        pump_filter = self.vfilters.ballast_pump_filter

        operation_valves = []
        for idx, seq in self.BP_close.items():
            count = -1
            if seq[0][self.constants.PUMP_TYPE_VARIABLE] == self.constants.BALLAST_PUMP_NAME:
                pumps = [i for i in time_dict[time][self.constants.CLOSE] if
                         i in self.constants.BALLAST_MAP[self.constants.PUMP].values()]
                valves = pump_filter(seq, pumps, count)  # ballast pump filter
                for v in valves:
                    v[
                        self.constants.VALVE_OP_VARIABLE] = self.constants.CLOSE  # ensure all ballast pump valve operation is close
                operation_valves += valves
        return operation_valves

    ###### DEBALLAST ######

    # Deballasting by gravity operation with tank valves filters
    def deballast_gravity_operation(self, time, time_dict):
        tank_filter = self.vfilters.ballast_tank_filter
        no_filter = self.vfilters.no_filter

        operation_valves = []
        for idx, seq in self.deballast_gravity.items():  # loop through sequence and get filtered valves
            count = str(idx.split('_')[1])
            if seq[0][self.constants.VALVE_TYPE_VARIABLE] == self.constants.BALLAST_TANK_NAME:
                tanks = time_dict[time][self.constants.OPEN]
                valves = tank_filter(seq, tanks, count)  # ballast tank filter
            else:
                valves = no_filter(seq, count)
            operation_valves += valves
        return operation_valves

    # Flooding ballast pump operation for deballasting with no filters
    def deballast_flood_pump_operation(self, time, time_dict):
        no_filter = self.vfilters.no_filter

        operation_valves = []
        for idx, seq in self.deballast_flood_pump.items():  # loop through sequence and get filtered valves
            count = str(idx.split('_')[1])
            valves = no_filter(seq, count)  # no filter, take all valves
            operation_valves += valves
        return operation_valves

    # deballasting by pump after gravity with pump filters
    def deballast_pump_after_gravity_operation(self, time, time_dict):
        pump_filter = self.vfilters.ballast_pump_filter
        no_filter = self.vfilters.no_filter

        operation_valves = []
        for idx, seq in self.deballast_pump_after_gravity.items():  # loop through sequence and get filtered valves
            count = str(idx.split('_')[1])
            if seq[0][self.constants.PUMP_TYPE_VARIABLE] == self.constants.BALLAST_PUMP_NAME:
                pumps = [i for i in time_dict[time][self.constants.OPEN] if
                         i in self.constants.BALLAST_MAP[self.constants.PUMP].values()]
                valves = pump_filter(seq, pumps, count)  # ballast pump filter
            else:
                valves = no_filter(seq, count)  # no filter, take all valves
            operation_valves += valves
        return operation_valves

    # deballasting by pump without gravity with pump filters
    def deballast_pump_wo_gravity_operation(self, time, time_dict):
        pump_filter = self.vfilters.ballast_pump_filter
        tank_filter = self.vfilters.ballast_tank_filter
        no_filter = self.vfilters.no_filter

        operation_valves = []
        for idx, seq in self.deballast_pump_wo_gravity.items():  # loop through sequence and get filtered valves
            count = str(idx.split('_')[1])
            if seq[0][self.constants.VALVE_TYPE_VARIABLE] == self.constants.BALLAST_TANK_NAME:
                tanks = time_dict[time][self.constants.OPEN]
                valves = tank_filter(seq, tanks, count)  # ballast tank filter
            elif seq[0][self.constants.PUMP_TYPE_VARIABLE] == self.constants.BALLAST_PUMP_NAME:
                pumps = [i for i in time_dict[time][self.constants.OPEN] if
                         i in self.constants.BALLAST_MAP[self.constants.PUMP].values()]
                valves = pump_filter(seq, pumps, count)  # ballast pump filter
            else:
                valves = no_filter(seq, count)  # no filter, take all valves
            operation_valves += valves
        return operation_valves

    # deballasting sea to sea operation for pumps with pump filters
    def deballast_sea_to_sea_pump_operation(self, time, time_dict):
        tank_filter = self.vfilters.ballast_tank_filter
        no_filter = self.vfilters.no_filter

        operation_valves = []
        for idx, seq in self.deballast_sea_to_sea_pump.items():  # loop through sequence and get filtered valves
            count = str(idx.split('_')[1])
            if seq[0][self.constants.VALVE_TYPE_VARIABLE] == self.constants.BALLAST_TANK_NAME:
                tanks = time_dict[time][self.constants.CLOSE]
                valves = tank_filter(seq, tanks, count)  # ballast tank filter
            else:
                valves = no_filter(seq, count)  # no filter, take all valves
            operation_valves += valves
        return operation_valves

    # deballasting sea to sea operation for eductor with tank strip and eductor filters
    def deballast_sea_to_sea_eductor_operation(self, time, time_dict):
        ballast_eductor_filter = self.vfilters.ballast_eductor_filter
        strip_tank_filter = self.vfilters.ballast_strip_tank_filter
        no_filter = self.vfilters.no_filter

        operation_valves = []
        for idx, seq in self.deballast_sea_to_sea_eductor.items():  # loop through sequence and get filtered valves
            count = str(idx.split('_')[1])
            if seq[0][self.constants.VALVE_TYPE_VARIABLE] == self.constants.BALLAST_STRIP_TANK_NAME:
                tanks = time_dict[time][self.constants.CLOSE]
                valves = strip_tank_filter(seq, tanks, count)  # ballast strip tank filter
            elif seq[0][self.constants.VALVE_TYPE_VARIABLE] in self.constants.BALLAST_EDUCTOR_NAME:
                eductor = [i[-1] for i in time_dict[time][self.constants.CLOSE] if
                           i in self.constants.BALLAST_MAP[self.constants.EDUCTOR].values()]
                valves = ballast_eductor_filter(seq, eductor, count)  # ballast eductor related filter
            else:
                valves = no_filter(seq, count)  # no filter, take all valves
            operation_valves += valves
        return operation_valves

    # deballasting stripping by eductor with tank strip and eductor filters
    def deballast_stripping_eductor_operation(self, time, time_dict):
        ballast_eductor_filter = self.vfilters.ballast_eductor_filter
        strip_tank_filter = self.vfilters.ballast_strip_tank_filter
        no_filter = self.vfilters.no_filter

        operation_valves = []
        for idx, seq in self.deballast_stripping_eductor.items():  # loop through sequence and get filtered valves
            count = str(idx.split('_')[1])
            if seq[0][self.constants.VALVE_TYPE_VARIABLE] == self.constants.BALLAST_STRIP_TANK_NAME:
                tanks = time_dict[time][self.constants.CLOSE]
                valves = strip_tank_filter(seq, tanks, count)  # ballast strip tank filter
            elif seq[0][self.constants.VALVE_TYPE_VARIABLE] in self.constants.BALLAST_EDUCTOR_NAME:
                eductor = [i[-1] for i in time_dict[time][self.constants.OPEN] if
                           i in self.constants.BALLAST_MAP[self.constants.EDUCTOR].values()]
                valves = ballast_eductor_filter(seq, eductor, count)  # ballast eductor related filter
            else:
                valves = no_filter(seq, count)  # no filter, take all valves
            operation_valves += valves
        return operation_valves

    # deballasting shutting operation with pump filters
    def deballast_shut_operation(self, time, time_dict):
        pump_filter = self.vfilters.ballast_pump_filter
        no_filter = self.vfilters.no_filter

        operation_valves = []
        for idx, seq in self.deballast_shut.items():
            count = str(idx.split('_')[1])
            if seq[0][self.constants.PUMP_TYPE_VARIABLE] == self.constants.BALLAST_PUMP_NAME:
                pumps = [i for i in time_dict[time][self.constants.CLOSE] if
                         i in self.constants.BALLAST_MAP[self.constants.PUMP].values()]
                valves = pump_filter(seq, pumps, count)  # ballast pump filter
            else:
                valves = no_filter(seq, count)  # no filter, take all valves
            operation_valves += valves
        return operation_valves

        ###### LOADING ######

    # Open single tank operation for loading with tank and manifold filter
    def open_single_tank_operation(self, time, time_dict):
        tank_filter = self.vfilters.cargo_tank_filter
        manifold_filter = self.vfilters.manifold_filter
        no_filter = self.vfilters.no_filter

        operation_valves = []
        for idx, seq in list(self.open_single_tank.items())[
                        :-1]:  # last item in sequence is a repeat of 1st item so ignore
            count = str(idx.split('_')[1])
            if seq[0][self.constants.VALVE_TYPE_VARIABLE] == self.constants.CARGO_TANK_NAME:
                tanks = time_dict[time][self.constants.OPEN]
                valves = tank_filter(seq, tanks, count)  # cargo tank filter
            elif self.constants.MANIFOLD_NAME in seq[0][self.constants.VALVE_TYPE_VARIABLE]:
                valves = manifold_filter(seq, self.MANIFOLD, self.SIDE, count)  # cargo manifold filter
            else:
                valves = no_filter(seq, count)  # no filter, take all valves
            operation_valves += valves
        return operation_valves

    # Open all tank operations for loading with tank filter
    def open_all_tank_operation(self, time, time_dict):
        tank_filter = self.vfilters.cargo_tank_filter
        no_filter = self.vfilters.no_filter

        operation_valves = []
        for idx, seq in self.open_all_tank.items():
            count = str(idx.split('_')[1])
            if seq[0][self.constants.VALVE_TYPE_VARIABLE] == self.constants.CARGO_TANK_NAME:
                tanks = time_dict[time][self.constants.OPEN]
                valves = tank_filter(seq, tanks, count)  # cargo tank filter
            else:
                valves = no_filter(seq, count)  # no filter, take all valves
            operation_valves += valves
        return operation_valves

    # Open cargo tank for loading with tank filter
    def CT_open_operation(self, time, time_dict):
        tank_filter = self.vfilters.cargo_tank_filter

        operation_valves = []
        for idx, seq in self.CT_open.items():
            count = -1
            if seq[0][self.constants.VALVE_TYPE_VARIABLE] == self.constants.CARGO_TANK_NAME:
                tanks = time_dict[time][self.constants.OPEN]
                valves = tank_filter(seq, tanks, count)  # cargo tank filter
                for v in valves:
                    v[
                        self.constants.VALVE_OP_VARIABLE] = self.constants.OPEN  # ensure all cargo tank valve operation is open
                operation_valves += valves
        return operation_valves

    # Close cargo tank for loading with tank filter
    def CT_close_operation(self, time, time_dict):
        tank_filter = self.vfilters.cargo_tank_filter

        operation_valves = []
        for idx, seq in self.CT_close.items():
            count = -1
            if seq[0][self.constants.VALVE_TYPE_VARIABLE] == self.constants.CARGO_TANK_NAME:
                tanks = time_dict[time][self.constants.CLOSE]
                valves = tank_filter(seq, tanks, count)  # cargo tank filter
                for v in valves:
                    v[
                        self.constants.VALVE_OP_VARIABLE] = self.constants.CLOSE  # ensure all cargo tank valve operation is close
                operation_valves += valves
        return operation_valves

    # Shutting sequence for loading with tank and manifold filter
    def shutting_loading_operation(self, time, time_dict):
        tank_filter = self.vfilters.cargo_tank_filter
        manifold_filter = self.vfilters.manifold_filter
        no_filter = self.vfilters.no_filter

        operation_valves = []
        for idx, seq in self.shutting_loading.items():
            count = str(idx.split('_')[1])
            if seq[0][self.constants.VALVE_TYPE_VARIABLE] == self.constants.CARGO_TANK_NAME:
                tanks = time_dict[time][self.constants.CLOSE]
                valves = tank_filter(seq, tanks, count)  # cargo tank filter
            elif self.constants.MANIFOLD_NAME in seq[0][self.constants.VALVE_TYPE_VARIABLE]:
                valves = manifold_filter(seq, self.MANIFOLD, self.SIDE, count)  # cargo manifold filter
            else:
                valves = no_filter(seq, count)  # no filter, take all valves
            operation_valves += valves
        return operation_valves


# write sequencing for loading
class ValveSequencing:
    def __init__(self, valve_sequence, voperation, mode, constants):
        self.constants = constants
        self.operation = voperation
        self.valve_sequence = valve_sequence
        self.mode = mode

        if self.mode == self.constants.LOADING_OPS:
            # Loading
            cargo_loading_events = self.getEventsFromJSON(self.constants.LOADING_OPS)
            loading_arr = [np.nan] * len(cargo_loading_events)
            for c in cargo_loading_events:
                loading_rates, loading_tanks, loading_timelines = self.getTankTimelines(
                    cargo_loading_events[c])  # tank rates and timelines for current cargo parcel
                temp = self.createTimelinesDF(loading_tanks, loading_timelines,
                                              loading_rates)  # create df with timelines/rates for each tank
                loading_arr[c] = temp
            self.loading_df = pd.concat(loading_arr, axis=1).sort_index()  # combine all timelines/rates df of all cargo parcels
            self.correctLoadingSingleTank()
            # sort timings
            self.loading_df = self.loading_df.reindex(sorted(self.loading_df.columns), axis=1)
            # map tank timelines/rates to loading operations
            if len(self.loading_df.columns) > 0:
                self.createLoadingOperationsDF()
                self.load_valves = self.generateSequence(self.loading_df, self.loading_operations_df)

            # Deballasting
            deballast_events, deballast_pump = self.getEventsFromJSON(self.constants.DEBALLAST_OPS)
            deballast_arr = [np.nan] * len(deballast_events)
            # deballast eduction events for each cargo parcel, not applicable to discharging
            if mode == self.constants.LOADING_OPS:
                deballast_eduction_events = self.getEventsFromBallastEduction(valve_sequence, self.constants.EDUCTION_KEY)
            for c in deballast_events:
                cur_deballast_df = self.extractBallastTankPump(deballast_events[c], deballast_pump[c])
                if mode == self.constants.LOADING_OPS:  # add deballasting eduction for loading operations
                    deballast_arr[c] = self.addDeballastEduction(deballast_eduction_events[c], cur_deballast_df)
                else:
                    deballast_arr[c] = cur_deballast_df
            self.deballast_df = pd.concat(deballast_arr, axis=1).sort_index()  # combine all timelines/rates df of all cargo parcels
            # Find out all pumps and eductor used for deballasting
            self.deballast_pump = [i for i in self.deballast_df.index if (i not in self.constants.BALLAST_TANKS) & ( i in self.constants.BALLAST_MAP['pump'].values())]
            self.deballast_eductor = [i for i in self.deballast_df.index if (i not in self.constants.BALLAST_TANKS) & ( i in self.constants.BALLAST_MAP['eductor'].values())]
            # map tank timelines/rates to deballasting operations
            if len(self.deballast_df.columns) > 0:
                self.createDeballastOperationsDF()
                self.deballast_valves = self.generateSequence(self.deballast_df, self.deballast_operations_df)

        else:
            # Ballasting
            ballast_events, ballast_pump = self.getEventsFromJSON(self.constants.BALLAST_OPS)
            ballast_arr = [np.nan] * len(ballast_events)
            for c in ballast_events:
                cur_ballast_df = self.extractBallastTankPump(ballast_events[c], ballast_pump[c])
                #if self.ballasting_timing[c][self.constants.END] == cur_ballast_df.columns[-1]:
                ballast_arr[c] = cur_ballast_df
                #else:
                    #ballast_arr[c] = cur_ballast_df
            # combine all timelines/rates df of all cargo parcels
            self.ballast_df = pd.concat(ballast_arr, axis=1).sort_index()
            # Find out all pumps and eductor used for deballasting
            self.ballast_pump = [i for i in self.ballast_df.index if (i not in self.constants.BALLAST_TANKS) & (
                        i in self.constants.BALLAST_MAP['pump'].values())]
            # map tank timelines/rates to ballasting operations
            if len(self.ballast_df.columns) > 0:
                self.createBallastOperationsDF()
                self.ballast_valves = self.generateSequence(self.ballast_df, self.ballast_operations_df)

    # get events and timings from output json
    def getEventsFromJSON(self, module):
        if module == self.constants.LOADING_OPS:
            # stage wise timing for each cargo parcel
            self.loading_timing = self.getStagesTiming(self.valve_sequence)
            # cargo tank events for each cargo parcel
            cargo_loading_events = self.getEventsFromOutput(self.valve_sequence, self.constants.SIMCARGOLOADING_KEY)
            return cargo_loading_events
        elif module == self.constants.DEBALLAST_OPS:
            # stage wise timing
            self.deballasting_timing = self.getStagesTiming(self.valve_sequence)
            # deballast tank events for each cargo parcel
            deballast_events = self.getEventsFromOutput(self.valve_sequence, self.constants.SIMDEBALLASTING_KEY)
            # deballast pump events for each cargo parcel
            deballast_pump = self.getEventsFromOutputPump(self.valve_sequence, self.constants.BALLAST_KEY)
            return deballast_events, deballast_pump
        elif module == self.constants.BALLAST_OPS:
            # stage wise timing
            self.ballasting_timing = self.getStagesTiming(self.valve_sequence)
            # ballast tank events for each cargo parcel
            ballast_events = self.getEventsFromOutput(self.valve_sequence, self.constants.SIMBALLASTING_KEY)
            ballast_pump = self.getEventsFromOutputPump(self.valve_sequence, self.constants.BALLAST_KEY)
            return ballast_events, ballast_pump

    # reformat and extract information about ballast tanks and pumps into dataframe
    def extractBallastTankPump(self, tank_event, pump_event):
        # tank rates and timelines for current cargo
        ballast_rates, ballast_tanks, ballast_timelines = self.getTankTimelines(tank_event)
        # pump rates and timelines for current cargo
        pump_rates, ballast_pumps, pump_timelines = self.getPumpTimelines(pump_event)
        # combine tank and pump timelines
        tanks_pumps = np.unique(np.concatenate([ballast_tanks, ballast_pumps]))
        timelines = np.unique(np.concatenate([ballast_timelines, pump_timelines]))
        rates = {**pump_rates, **ballast_rates}
        cur_ballast_df = self.createTimelinesDF(tanks_pumps, timelines, rates)
        return cur_ballast_df

    # correct tanks for open single tank during loading stage
    def correctLoadingSingleTank(self):
        # ensure that openSingleTank has indication of which tank to open
        for c in self.loading_timing:
            initial_rate_time = self.loading_timing[c][self.constants.INITIALRATE][0]
            initial_tank_idx = pd.notna(self.loading_df.loc[:, initial_rate_time])
            open_single_tank_time = self.loading_timing[c][self.constants.OPENSINGLETANK][0]
            if open_single_tank_time not in self.loading_df.columns:
                self.loading_df[open_single_tank_time] = np.nan
            self.loading_df.loc[initial_tank_idx, open_single_tank_time] = -1  # indicate -1 on open single tank timing

    # Get start time of each stage for each cargo
    def getStagesTiming(self, sequence):
        seq = sequence[self.constants.EVENTS]
        events = {}
        for c in range(len(seq)):  # loop through cargo
            events[c] = {}
            cargo_details = seq[c][self.constants.SEQUENCE]
            for s in range(len(cargo_details)):  # loop through stages
                stage = cargo_details[s][self.constants.STAGE]
                timing = float(cargo_details[s][self.constants.TIMESTART])
                # get stage and timing
                if stage in events:
                    events[c][stage].append(timing)
                else:
                    events[c][stage] = [timing]
            # get end time of cargo
            lastTiming = float(cargo_details[s][self.constants.TIMEEND])
            events[c][self.constants.END] = [lastTiming]
        return events

    # get tank rates using key in output dictionary
    def getEventsFromOutput(self, sequence, key):
        seq = sequence[self.constants.EVENTS]
        events = {}
        for c in range(len(seq)):
            # extract "key" from input sequence
            events[c] = list(pd.DataFrame(seq[c][self.constants.SEQUENCE])[key])
        return events

    # get tank rates for cargo tank COW/Stripping using key in output dictionary
    def getEventsFromOutputCOW(self, sequence, key):
        seq = sequence[self.constants.EVENTS]
        events = {}
        for c in range(len(seq)):
            events[c] = []
            for stage in list(pd.DataFrame(seq[c][self.constants.SEQUENCE])[key]):
                # extract "key" from input sequence and reformat it
                for actions in stage.keys():
                    if len(stage[actions]) > 0:
                        events[c] += [[{idx: action for idx, action in enumerate(stage[actions])}]]
        return events

    # get pump rates for normal ballasting/deballasting using key in output dictionary
    def getEventsFromOutputPump(self, sequence, key):
        seq = sequence[self.constants.EVENTS]
        events = {}
        for c in range(len(seq)):
            events[c] = {}
            for stage in list(pd.DataFrame(seq[c][self.constants.SEQUENCE])[key]):
                # extract "key" from input sequence and reformat it
                for pump in stage.keys():
                    if len(stage[pump]) > 0:
                        pump_name = self.constants.BALLAST_MAP[self.constants.PUMP][str(pump)] if str(pump) in \
                                                                                                  self.constants.BALLAST_MAP[
                                                                                                      self.constants.PUMP] else str(
                            pump)
                        pump_timeline = [time_info for idx, time_info in enumerate(stage[pump]) if
                                         float(time_info[self.constants.RATEM3]) > 0.0]
                        if pump_name in events[c]:
                            events[c][pump_name] += pump_timeline
                        else:
                            events[c][pump_name] = pump_timeline
        return events

    # get pump/tank rates for eduction of ballast tank using key in output dictionary
    def getEventsFromBallastEduction(self, sequence, key):
        seq = sequence[self.constants.EVENTS]
        events = {}
        for c in range(len(seq)):
            events[c] = {}
            for stage in list(pd.DataFrame(seq[c][self.constants.SEQUENCE])[key]):
                if len(stage) > 0:
                    # ballast tanks
                    for tank in stage[self.constants.TANK].values():
                        events[c][tank] = {}
                        events[c][tank][self.constants.TIMESTART] = stage[self.constants.TIMESTART]
                        events[c][tank][self.constants.TIMEEND] = stage[self.constants.TIMEEND]
                        events[c][tank][self.constants.RATE] = -1
                    # ballast eductor
                    for eductorInfo in stage[self.constants.PUMP_VARIABLE].values():
                        eductor = eductorInfo[self.constants.PUMPNAME_VARIABLE]
                        events[c][eductor] = {}
                        events[c][eductor][self.constants.TIMESTART] = stage[self.constants.TIMESTART]
                        events[c][eductor][self.constants.TIMEEND] = stage[self.constants.TIMEEND]
                        events[c][eductor][self.constants.RATE] = -1
                        break  # only choose 1 ballast eductor
                    # ballast pumps
                    for eductorInfo in stage[self.constants.BALLASTPUMP_VARIABLE].values():
                        eductor = eductorInfo[self.constants.PUMPNAME_VARIABLE]
                        events[c][eductor] = {}
                        events[c][eductor][self.constants.TIMESTART] = stage[self.constants.TIMESTART]
                        events[c][eductor][self.constants.TIMEEND] = stage[self.constants.TIMEEND]
                        events[c][eductor][self.constants.RATE] = -1
        return events

    # get end and start timing of each pump for a cargo using output from getEventsFromOutputPump()
    def getPumpTimelines(self, events):
        timelines = []
        pumps = []
        pump_rates = {}
        for pump in events:  # Loop through list of rate events for each stage
            for time_info in events[pump]:
                if len(time_info) > 0:  # ensure pump event is available
                    if float(time_info[self.constants.TIMESTART]) <= float(time_info[self.constants.TIMEEND]): # ensure pump event is correct
                        if pump not in pumps: # record pumps
                            pumps.append(pump)
                        # initialise current pump
                        if pump not in pump_rates:
                            pump_rates[pump] = []
                        # time
                        timelines.append(float(time_info[self.constants.TIMESTART]))
                        timelines.append(float(time_info[self.constants.TIMEEND]))
                        # rates at current time
                        pump_rate_dict = {}
                        rates = float(time_info[self.constants.RATEM3]) if float(
                            time_info[self.constants.RATEM3]) > 0.0 else np.nan
                        pump_rate_dict[float(time_info[self.constants.TIMESTART])] = rates
                        pump_rate_dict[float(time_info[self.constants.TIMEEND])] = 0.0
                        pump_rates[pump].append(pump_rate_dict)
        pumps = np.unique(pumps)
        timelines = np.unique(timelines)
        return pump_rates, pumps, timelines

    # get end and start timing of each tank for a cargo using output from getEventsFromOutput()
    def getTankTimelines(self, events):
        timelines = []
        tanks = []
        tanks_rates = {}
        for event in events:  # Loop through list of rate events for each stage
            if isinstance(event, list):
                for sub_event in event:  # for each sub stage
                    for tank in sub_event.keys():  # extract timing, rates for each tank
                        tank_details = sub_event[tank]
                        # initialise current tank
                        if (tank_details[self.constants.TANKSHORTNAME] not in tanks_rates):
                            tanks_rates[tank_details[self.constants.TANKSHORTNAME]] = []
                        # tank name
                        tanks.append(tank_details[self.constants.TANKSHORTNAME])
                        # time
                        timelines.append(float(tank_details[self.constants.TIMESTART]))
                        timelines.append(float(tank_details[self.constants.TIMEEND]))
                        # tank rate at time
                        time_rate_dict = {}
                        rates = float(
                            tank_details[self.constants.RATE]) if self.constants.RATE in tank_details else -1.0
                        time_rate_dict[float(tank_details[self.constants.TIMESTART])] = rates
                        time_rate_dict[float(tank_details[self.constants.TIMEEND])] = 0.0
                        tanks_rates[tank_details[self.constants.TANKSHORTNAME]].append(time_rate_dict)
        tanks = np.unique(tanks)
        timelines = np.unique(timelines)
        return tanks_rates, tanks, timelines

    # Create dataframe of timings for each tank
    def createTimelinesDF(self, tanks, timelines, tanks_rates):
        df = pd.DataFrame(index=tanks, columns=timelines)
        for tank in tanks_rates.keys():
            for timeline in tanks_rates[tank]:
                # start/end timing of tank
                times = list(timeline.keys())
                start_time_in_minutes = times[0]
                end_time_in_minutes = times[1]
                # rate at that time period
                rate = float(timeline[start_time_in_minutes])
                # Populate rate for that time period for that tank
                cols_from_start_to_end = [i for i in timelines if
                                          (i >= start_time_in_minutes) & (i < end_time_in_minutes)]
                df.loc[tank][cols_from_start_to_end] = rate
        return df

    # timing and tank of tanks to be educted during deballasting
    def addDeballastEduction(self, events, df):
        for tank in events:
            # start/end timing of tank
            timeStart = float(events[tank][self.constants.TIMESTART])
            timeEnd = float(events[tank][self.constants.TIMEEND])
            # rate at that time
            startRate = events[tank][self.constants.RATE]
            endRate = np.nan
            # Populate rate for that time period for that tank
            df.loc[tank, timeStart] = startRate
            df.loc[tank, timeEnd] = endRate
        return df

    def getEquipmentTiming(self, df):
        result_dict = {time: {self.constants.OPEN: [], self.constants.CLOSE: []} for time in df.columns}
        for tank in df.index:
            prev = np.nan
            for idx, rate in enumerate(df.loc[tank, :].values):
                time = df.columns[idx]
                cur_operation = df.loc[tank, time]
                # open
                if np.isnan(prev) & (not np.isnan(rate)):
                    result_dict[time][self.constants.OPEN].append(tank)
                # close
                elif (not np.isnan(prev)) & (np.isnan(rate)):
                    result_dict[time][self.constants.CLOSE].append(tank)
                # close main ballast valve then open strip valve
                elif (not np.isnan(prev)) & (rate == -1):
                    result_dict[time][self.constants.CLOSE].append(tank)
                    result_dict[time][self.constants.OPEN].append(tank)
                prev = rate
        return result_dict

    # Create dataframe of loading operations for each tank using timings df
    def createLoadingOperationsDF(self):
        # operations
        ops = self.constants.ops_abbr_dict[self.constants.LOADING_OPS]
        OST = ops[self.constants.LOADING_SINGLE]
        OAT = ops[self.constants.LOADING_ALL]
        CTO = ops[self.constants.CARGO_TANK_OPEN]
        CTC = ops[self.constants.CARGO_TANK_CLOSE]
        SL = ops[self.constants.LOADING_SHUT]
        self.loading_operations_df = pd.DataFrame(index=self.loading_df.index, columns=self.loading_df.columns)

        # Timings for fixed operations of loading
        singleTankTime = [stages[self.constants.OPENSINGLETANK][0] for c, stages in self.loading_timing.items()]
        allTanksTime = [stages[self.constants.OPENALLTANKS][0] for c, stages in self.loading_timing.items()]
        shuttingTime = [stages[self.constants.END][0] for c, stages in self.loading_timing.items()]

        # Fixed Operations -  standard valve procedures
        for i in range(len(singleTankTime)):
            self.loading_operations_df[shuttingTime[i]] = f'{i}_{SL}'  # initialise shutting time
            if singleTankTime[i] in shuttingTime:  # for multiple cargo
                self.loading_operations_df[singleTankTime[i]] = f'{i - 1}_{SL}, {i}_{OST}'
            else:
                self.loading_operations_df[singleTankTime[i]] = f'{i}_{OST}'
            self.loading_operations_df[allTanksTime[i]] = f'{i}_{OAT}'

        # sort timings_OST
        self.loading_operations_df = self.loading_operations_df.reindex(sorted(self.loading_operations_df.columns),
                                                                        axis=1)

        # Variable Operations
        for tank in self.loading_df.index:  # loop through each tank
            prev = np.nan  # tank closed, no rate
            for idx, rate in enumerate(self.loading_df.loc[tank, :].values):  # loop thruogh timeline of tank
                time = self.loading_df.columns[idx]
                cur_operation = self.loading_operations_df.loc[tank, time]
                # open tank
                if np.isnan(prev) & (not np.isnan(rate)):
                    if pd.isna(cur_operation):
                        self.loading_operations_df.loc[tank, time] = CTO
                    elif not any(substring in cur_operation for substring in [OST, OAT]):
                        self.loading_operations_df.loc[tank, time] += f", {CTO}"
                # Close Tank
                elif (not np.isnan(prev)) & np.isnan(rate):
                    if pd.isna(cur_operation):
                        self.loading_operations_df.loc[tank, time] = CTC
                    elif not any(substring in cur_operation for substring in [SL]):
                        self.loading_operations_df.loc[tank, time] += f", {CTC}"
                prev = rate
        return

    def getDeballastValveTiming(self, start, end):
        col = (self.deballast_df.columns >= start) & (self.deballast_df.columns < end)
        if self.constants.GRAVITY in list(self.deballast_df.index):
            gravityTime = self.deballast_df.loc[self.constants.GRAVITY, col].first_valid_index()
        else:
            gravityTime = np.nan
        pumpTime = self.deballast_df.loc[self.deballast_pump, col].apply(lambda x: x.first_valid_index(), axis=1).min()
        eductorTime = self.deballast_df.loc[self.deballast_eductor, col].apply(lambda x: x.first_valid_index(),
                                                                               axis=1).min()
        if not np.isnan(eductorTime):
            beforeLast = self.deballast_df.loc[self.deballast_eductor, col].apply(lambda x: x.last_valid_index(),
                                                                                  axis=1).max()
            endTime = list(self.deballast_df.columns)[list(self.deballast_df.columns).index(beforeLast) + 1]
        else:
            beforeLast = self.deballast_df.loc[self.deballast_pump, col].apply(lambda x: x.last_valid_index(),
                                                                               axis=1).max()
            endTime = list(self.deballast_df.columns)[list(self.deballast_df.columns).index(beforeLast) + 1]
            # Latest shutting procedures should be at the end time of the cargo
        if endTime > end:
            endTime = end
        return (gravityTime, pumpTime, eductorTime, endTime)

    def getDeballastEductorPumps(self, eductorTime):
        boolean_eductor_pumps = pd.notna(self.deballast_df.loc[self.deballast_pump, eductorTime])
        eductor_pumps = boolean_eductor_pumps.index[boolean_eductor_pumps].tolist()
        boolean_eductor_closedpump = pd.isna(self.deballast_df.loc[self.deballast_pump, eductorTime])
        unused_pumps = boolean_eductor_closedpump.index[boolean_eductor_closedpump].tolist()
        return (eductor_pumps, unused_pumps)

    # Create dataframe of deballasting operations for each tank using timings df
    def createDeballastOperationsDF(self):
        # operations
        ops = self.constants.ops_abbr_dict[self.constants.DEBALLAST_OPS]
        DG = ops[self.constants.DEBALLAST_GRAVITY]
        DFBP = ops[self.constants.DEBALLAST_FLOOD]
        DPG = ops[self.constants.DEBALLAST_PUMP_GRAVITY]
        DPWG = ops[self.constants.DEBALLAST_PUMP]
        DSTSP = ops[self.constants.DEBALLAST_STSP]
        DSE = ops[self.constants.DEBALLAST_EDUCTOR]
        STSE = ops[self.constants.DEBALLAST_STSE]
        SD = ops[self.constants.DEBALLAST_SHUT]
        WBTC = ops[self.constants.BALLAST_TANK_CLOSE]
        WBTO = ops[self.constants.BALLAST_TANK_OPEN]
        BPO = ops[self.constants.BALLAST_PUMP_OPEN]
        BPC = ops[self.constants.BALLAST_PUMP_CLOSE]

        self.deballast_operations_df = pd.DataFrame(index=self.deballast_df.index, columns=self.deballast_df.columns)
        # Timings for fixed operations
        startEndTime = [(stages[self.constants.OPENSINGLETANK][0], stages[self.constants.END][0]) for c, stages in
                        self.deballasting_timing.items()]

        # Fixed Operations -  standard valve procedures
        for i in range(len(startEndTime)):
            s, e = startEndTime[i]
            # timing for fixed operations
            gravityTime, pumpTime, eductorTime, endTime = self.getDeballastValveTiming(s, e)

            # start with Gravity
            if pd.notna(gravityTime):
                # Gravity
                if gravityTime not in self.deballast_df.columns:
                    self.deballast_df[gravityTime] = np.nan
                if not isinstance(self.deballast_operations_df[gravityTime][0], str):
                    self.deballast_operations_df[gravityTime] = f"{i}_{DG}"
                else:
                    self.deballast_operations_df[gravityTime] += f", {i}_{DG}"
                if pumpTime not in self.deballast_df.columns:
                    self.deballast_df[pumpTime] = np.nan
                # Gravity then Pump
                self.deballast_operations_df[pumpTime] = f"{i}_{DFBP}, {i}_{DPG}"
                # Start without Gravity
            else:
                if pumpTime not in self.deballast_df.columns:
                    self.deballast_df[pumpTime] = np.nan
                if not isinstance(self.deballast_operations_df[pumpTime][0], str):
                    self.deballast_operations_df[pumpTime] = f"{i}_{DFBP}, {i}_{DPWG}"
                else:
                    self.deballast_operations_df[pumpTime] += f", {i}_{DFBP}, {i}_{DPWG}"

            # if eductor is present at the end of deballasting
            if pd.notna(eductorTime):
                # pumps for eductor, pumps to be closed
                eductor_pumps, unused_pumps = self.getDeballastEductorPumps(eductorTime)

                # Pump to eductor
                if eductorTime not in self.deballast_df.columns:
                    self.deballast_df[eductorTime] = np.nan
                self.deballast_operations_df[eductorTime] = f"{i}_{DSTSP}, {i}_{DSE}"

                if len(unused_pumps) > 0:  # close unused ballast pumps during eduction stage
                    for pump in unused_pumps:
                        self.deballast_operations_df.loc[pump, eductorTime] += f", {i}_{BPC}"
                # shutting sequence after eductor
                if endTime not in self.deballast_df.columns:
                    self.deballast_df[endTime] = np.nan
                self.deballast_operations_df[endTime] = f"{i}_{STSE}, {i}_{SD}"
            # NO EDUCTOR
            else:
                # shutting sequence after pumps
                if endTime not in self.deballast_df.columns:
                    self.deballast_df[endTime] = np.nan
                self.deballast_operations_df[endTime] = f"{i}_{DSTSP}, {i}_{SD}"

        # sort timings
        self.deballast_operations_df = self.deballast_operations_df.reindex(
            sorted(self.deballast_operations_df.columns), axis=1)
        self.deballast_df = self.deballast_df[sorted(self.deballast_df.columns)]

        # Variable Tank/Pump Operations
        for tank in self.deballast_df.index:
            prev = np.nan
            for idx, rate in enumerate(self.deballast_df.loc[tank, :].values):
                time = self.deballast_df.columns[idx]
                cur_operation = self.deballast_operations_df.loc[tank, time]
                # Ballast Tanks
                if (tank in self.constants.BALLAST_TANKS):
                    # Compare prev tank rate (nan means no rate) and current tank rate
                    # Open tank
                    if pd.isna(prev) & pd.notna(rate):  # prev ballast tank closed, current ballast tank flowing
                        if pd.isna(cur_operation):
                            self.deballast_operations_df.loc[tank, time] = WBTO
                        elif not any(substring in cur_operation for substring in [DG, DPWG]):
                            self.deballast_operations_df.loc[tank, time] += f", {WBTO}"
                    # Close Tank
                    elif pd.notna(prev) & pd.isna(rate):  # prev ballast tank flowing, current ballast tank closed
                        if pd.isna(cur_operation):
                            self.deballast_operations_df.loc[tank, time] = WBTC
                        elif not any(substring in cur_operation for substring in [DSTSP, STSE]):
                            self.deballast_operations_df.loc[tank, time] += f", {WBTC}"
                prev = rate

    def getBallastValveTiming(self, start, end):
        col = (self.ballast_df.columns >= start) & (self.ballast_df.columns <= end)
        if self.constants.GRAVITY in list(self.ballast_df.index):
            gravityTime = self.ballast_df.loc[self.constants.GRAVITY, col].first_valid_index()
        else:
            gravityTime = np.nan
        pumpTime = self.ballast_df.loc[self.ballast_pump, col].apply(lambda x: x.first_valid_index(), axis=1).min()
        beforeLast = self.ballast_df.loc[self.ballast_pump, col].apply(lambda x: x.last_valid_index(), axis=1).max()
        endTime = list(self.ballast_df.columns)[list(self.ballast_df.columns).index(beforeLast) + 1]
        if endTime > end:
            endTime = end
        return (gravityTime, pumpTime, endTime)

    # Create dataframe of ballasting operations for each tank using timings df
    def createBallastOperationsDF(self):
        # operations
        ops = self.constants.ops_abbr_dict[self.constants.BALLAST_OPS]
        BG = ops[self.constants.BALLAST_GRAVITY]
        FBP = ops[self.constants.BALLAST_FLOOD]
        BPG = ops[self.constants.BALLAST_PUMP_GRAVITY]
        BPWG = ops[self.constants.BALLAST_PUMP]
        STSP = ops[self.constants.BALLAST_STS]
        SB = ops[self.constants.BALLAST_SHUT]
        BPC = ops[self.constants.BALLAST_TANK_CLOSE]
        BPO = ops[self.constants.BALLAST_TANK_OPEN]
        WBTO = ops[self.constants.BALLAST_PUMP_OPEN]
        WBTC = ops[self.constants.BALLAST_PUMP_CLOSE]
        self.ballast_operations_df = pd.DataFrame(index=self.ballast_df.index, columns=self.ballast_df.columns)

        startEndTime = [(stages['floodSeparator'][0], stages[self.constants.END][0]) for c, stages in
                        self.ballasting_timing.items()]

        # Fixed Operations -  standard valve procedures
        for i in range(len(startEndTime)):
            s, e = startEndTime[i]
            if 'BP2' in self.ballast_df.index:
                df = pd.DataFrame(self.ballast_df.loc[['BP1','BP2']])
            else:
                df = pd.DataFrame(self.ballast_df.loc[['BP1']])
            column_values = df.columns.values.tolist()
            filtered_values = [number for number in column_values if (number >= s) and (number<=e)]
            col = df.loc[:,filtered_values]
            result = np.any(col > 0) 
            if  not result:
                continue
            if i == 3:
                i = 1
                gravityTime, pumpTime, endTime = self.getBallastValveTiming(s, e)
            else:    
            # timing for fixed operations
                gravityTime, pumpTime, endTime = self.getBallastValveTiming(s, e)

            # start with Gravity
            if pd.notna(gravityTime):
                # Gravity
                if gravityTime not in self.ballast_df.columns:
                    self.ballast_df[gravityTime] = np.nan
                if not isinstance(self.ballast_operations_df[gravityTime][0], str):
                    self.ballast_operations_df[gravityTime] = f"{i}_{BG}"
                else:
                    self.ballast_operations_df[gravityTime] += f", {i}_{BG}"

                # Gravity then Pump
                if pumpTime not in self.ballast_df.columns:
                    self.ballast_df[pumpTime] = np.nan
                self.ballast_operations_df[pumpTime] = f"{i}_{FBP}, {i}_{BPG}"

            # Start without Gravity
            else:
                if pumpTime not in self.ballast_df.columns:
                    self.ballast_df[pumpTime] = np.nan
                    
                if not isinstance(self.ballast_operations_df[pumpTime][0], str):
                    self.ballast_operations_df[pumpTime] = f"{i}_{FBP}, {i}_{BPWG}"
                else:
                    self.ballast_operations_df[pumpTime] += f", {i}_{FBP}, {i}_{BPWG}"

            # End
            if endTime not in self.ballast_df.columns:
                self.ballast_df[endTime] = np.nan
                self.ballast_df = self.ballast_df[sorted(self.ballast_df.columns)] 
            self.ballast_operations_df[endTime] = f"{i}_{STSP}, {i}_{SB}"

        # sort timings
        self.ballast_operations_df = self.ballast_operations_df.reindex(sorted(self.ballast_operations_df.columns),
                                                                        axis=1)
        self.ballast_df = self.ballast_df[sorted(self.ballast_df.columns)]

        # Variable Tank/Pump Operations
        for tank in self.ballast_df.index:
            prev = np.nan
            for idx, rate in enumerate(self.ballast_df.loc[tank, :].values):
                time = self.ballast_df.columns[idx]
                cur_operation = self.ballast_operations_df.loc[tank, time]

                if tank in self.constants.BALLAST_TANKS:
                    # Open tank
                    if np.isnan(prev) & (not np.isnan(rate)):  # prev ballast tank closed, current ballast tank flowing
                        if pd.isna(cur_operation):
                            self.ballast_operations_df.loc[tank, time] = WBTO
                        elif not any(substring in cur_operation for substring in [BG, BPWG]):
                            self.ballast_operations_df.loc[tank, time] += f", {WBTO}"
                    # Close Tank
                    elif (not np.isnan(prev)) & np.isnan(
                            rate):  # prev ballast tank flowing, current ballast tank closed
                        if pd.isna(cur_operation):
                            self.ballast_operations_df.loc[tank, time] = WBTC
                        elif not any(substring in cur_operation for substring in [STSP]):
                            self.ballast_operations_df.loc[tank, time] += f", {WBTC}"
                prev = rate

    # Populate valves operations according to operations df
    def generateSequence(self, time_df, operations_df):
        voperation = self.operation
        tank_time = self.getEquipmentTiming(time_df)
        all_valves = {}  # list of all valves info to open/close at each timing
        cur_cargo = 0
        for time in operations_df.columns:  # for each timing
            all_valves[time] = []
            flatten_ops = sum([i.split(',') for i in operations_df.loc[:, time].dropna()], [])
            ops = [flatten_ops[i] for i in
                   sorted(np.unique(flatten_ops, return_index=True)[1])]  # unique while retaining order
            for op in ops:  # for each operation to be carried out
                op = op.strip()
                if '_' in op:
                    cargo, op = op.split('_')
                    cur_cargo = cargo
                valves = voperation.key_operation_mapping[op](time, tank_time)
                for v in valves:
                    v[self.constants.CARGO] = cur_cargo
                all_valves[time] += valves
        return all_valves


# Discharging
def getManifoldUsed(sequence):
    manifold = {}
    for item in sequence['dischargingInformation']['machineryInUses']['machinesInUses']:
        if item['machineName'].startswith('Manifold'):
            if item['machineName'] in manifold:
                manifold[item['machineName']].append(item['tankTypeName'])
            else:
                manifold[item['machineName']] = []
                manifold[item['machineName']].append(item['tankTypeName'])
      #         manifold.append(item['machineName'])
    return manifold


class ValveFiltersDischarge:
    def __init__(self, constants):
        #         print('valve filters')
        self.constants = constants
        return

    def tankFilter(self, i, tank, cargo):
        # print('tank filter')
        all_steps = []
        value = {}
        # print(i)
        # if i[self.constants.TANKSHORTNAME] in tank:
        if i['tankShortName'] in tank:
            # print(i['tankShortName'])
            valveOpen = 'close' if i['shut'] else 'open'
            value = {'valve': i['valveNumber'], 'operation': valveOpen, 'Cargo': cargo, 'stageNo': i['stageNumber']}
            all_steps.append(value)
        # print(f_valves)
        # print(value)
        return all_steps

    def manifoldFilter(self, i, cargo):
        # print('manifold filter')
        all_steps = []
        # print(i['valveTypeName'])
        valveOpen = 'close' if i['shut'] else 'open'
        value = {'valve': i['valveNumber'], 'operation': valveOpen, 'Cargo': cargo, 'stageNo': i['stageNumber']}
        all_steps.append(value)

        return all_steps

    def slopcopFilter(self, airpurge):
        # print('SlopCOP filter')
        all_steps = []
        for valve in airpurge:
            pump = valve['pumpCode']
            slop = valve['shortname']
            if 'COP1' in pump and 'SLP' in slop:
                valveOpen = 'close' if valve['shut'] else 'open'
                valveLine = valve['pumpCode']
                valvetank = valve['shortname']
                valvenumber = valve['valveNumber']
                # valveSequence = valve['sequenceNumber']
                value = {'valve': valvenumber, 'line': valveLine, 'tank': valvetank, 'operation': valveOpen}
                all_steps.append(value)

        # print(airpurgevalves)
        return all_steps

    def noFilter(self, i, cargo):
        all_steps = []
        valveOpen = 'close' if i['shut'] else 'open'
        value = {'valve': i['valveNumber'], 'operation': valveOpen, 'Cargo': cargo, 'stageNo': i['stageNumber']}
        all_steps.append(value)
        return all_steps

    def cowFilter(self, i, cargo, Start):
        if Start:
            all_steps = []
            valveOpen = 'open'
            value = {'valve': i['valve'], 'operation': valveOpen, 'Cargo': cargo}
            all_steps.append(value)
        else:
            # print(Start)
            all_steps = []
            valveOpen = 'close'
            value = {'valve': i['valve'], 'operation': valveOpen, 'Cargo': cargo}
            # print(value)
            all_steps.append(value)
        return all_steps

    def tankStripFilter(self, i, tank, cargo, Start):
        all_steps = []
        # print(tank)
        if i['tankShortName'] in tank:
            if Start:
                all_steps = []
                valveOpen = 'open'
                value = {'valve': i['valve'], 'operation': valveOpen, 'Cargo': cargo, 'stageName': i['stageName']}
                all_steps.append(value)
            else:
                # print(Start)
                all_steps = []
                valveOpen = 'close'
                value = {'valve': i['valve'], 'operation': valveOpen, 'Cargo': cargo, 'stageName': i['stageName']}
                # print(value)
                all_steps.append(value)
        return all_steps

    def copFilter(self, i, cargo, Start):
        # print('COP Filter')
        all_steps = []
        #         print(Start)
        if Start:
            valveOpen = 'close' if i['shut'] else 'open'
        else:
            valveOpen = 'close'
        #             print(valveOpen)

        value = {'valve': i['valveNumber'], 'operation': valveOpen, 'pump': i['pumpName'], 'Cargo': cargo,
                 'stageNo': i['stageNumber']}
        all_steps.append(value)

        return all_steps

    def tcpFilter(self, i, cargo):

        all_steps = []
        valveOpen = 'close' if i['shut'] else 'open'
        value = {'valve': i['valveNumber'], 'operation': valveOpen, 'Cargo': cargo, 'stageNo': i['stageNumber']}
        all_steps.append(value)
        return all_steps


class ValveOperationsDischarge:

    def __init__(self, valve_filter, constants, eductor, manifold, vessel_json):
        self.valve_filter = valve_filter
        self.manifold = manifold
        self.key_operation_mapping = {}
        self.key_operation_mapping['floodSeparator'] = self.flood_Separator
        self.key_operation_mapping['warmPumps'] = self.warmingCOP
        self.key_operation_mapping['initialRate'] = self.pumpingCOP
        self.key_operation_mapping['FillingTCP'] = self.fillingTCP
        self.key_operation_mapping['warmTCP'] = self.warmTCP
        self.key_operation_mapping['TankOpen'] = self.tankOpen
        self.key_operation_mapping['COWStripping'] = self.COWPrep
        self.key_operation_mapping['COWStripping_end'] = self.COWPrep
        self.key_operation_mapping['SDstart'] = self.slopStart
        self.key_operation_mapping['COPSHUT'] = self.copSHUT
        self.key_operation_mapping['TCPSHUT'] = self.shutTCP
        self.key_operation_mapping['SDend'] = self.slopStart
        self.key_operation_mapping['SDmid'] = self.slopDischarge
        self.key_operation_mapping['TankClose'] = self.tankClose
        self.key_operation_mapping['Pump Open']=self.warmingCOP
        self.key_operation_mapping['Tso'] = self.tankStripOpen
        self.key_operation_mapping['Tsc'] = self.tankStripClose
        self.key_operation_mapping['Tco'] = self.tankCowOpen
        self.key_operation_mapping['Tcc'] = self.tankCowClose
        self.key_operation_mapping['dryCheck'] = self.dryCheck
        self.key_operation_mapping['finalStripping'] = self.FinalStripStart
        self.key_operation_mapping['finalStripping_mid'] = self.FinalStripMid
        self.key_operation_mapping['fStripmid'] = self.FinalStripMid
        self.key_operation_mapping['finalStripping_end'] = self.FinalStripEnd
        self.key_operation_mapping['PARSHUT'] = self.PARShut
        self.key_operation_mapping['slopDischarge'] = self.slopStart
        self.key_operation_mapping['slopDischarge_mid'] = self.slopDischarge
        self.key_operation_mapping['slopDischarge_end'] = self.slopStart
        self.data = {}
        if eductor in ['None','']:
            self.eductor = 'eductor1'
        else:    
            self.eductor = eductor

        self.vessel_json = vessel_json
        self.valves = self.vessel_json['vessel']['vesselValveSequence']
        # self.valve_steps = valve_step
        self.airpurge = self.valves['airPurge']
        self.floodSeparator = self.valves['discharging']['floodingOfSeperator']
        self.warmUpCop = self.valves['discharging']['warmUpCop']
        self.pumpingCop = self.valves['discharging']['pumpingCop']
        self.copShut = self.valves['discharging']['shuttingCop']
        self.fillTCP = self.valves['discharging']['fillingUpForWarmUpOfTcp']
        self.warmUpTCP = self.valves['discharging']['warmUpOfTcp']
        #self.prepCOW_eductor1 = self.valves['eductionProcess']['slopPortTank']['general']['stage_1'][self.eductor]
        #self.tankCOW = self.valves['eductionProcess']['slopPortTank']['tankStrippingAndCow']['stage_2'][self.eductor]
        self.stripNo1 = \
        self.valves['eductionProcess']['slopPortTank']['strippingNo1PpRiser-CopAndNo1DeckLine']['stage_5'][self.eductor]
        self.stripNo2 = \
        self.valves['eductionProcess']['slopPortTank']['strippingNo2PpRiser-CopAndNo2DeckLine']['stage_6'][self.eductor]
        self.stripNo3 = \
        self.valves['eductionProcess']['slopPortTank']['strippingNo3PpRiser-CopAndNo3deckLine']['stage_7'][self.eductor]
        self.stripbottom = self.valves['eductionProcess']['slopPortTank']['lineStripping']['stage_4'][self.eductor]
        self.finalStripStart = self.valves['strippingSequence']
        self.vessel_pump_mapping = self.vessel_json['vessel']['vesselPumpTankMappings']
        self.strip_lines = ['1','2','3','bottom']
        # print(self.valve_steps)

    def stripLines(self):
        line_dict = {}
        for values in self.vessel_pump_mapping:
            mapping = values['vesselPump']
            for key, value in mapping.items():
                tanks = []
                if key == 'vesselTanks':
                    tank_details = value
                    #                     print(tank_details)
                    for info in tank_details:
                        # print(elem['shortName'])
                        tanks.append(info['shortName'])
                        # print(tanks)
                elif key == 'id':
                    id = value
                    # print(id)
                line_dict[id] = tanks
        return line_dict

    def airPurge_operation(self, key, slop='Slop P', cop='COP1'):
        self.slop = slop
        self.cop = cop
        # sequence_a = []
        sequence_a = self.valve_filter.slopcopFilter(self.airpurge)
        # print('airpurge')

        return sequence_a

    # print(self.valve_steps)
    def tankOpen(self, param_dict,tank_list):
        sequence_f = []
        #         print(param_dict)
        for stage, info in self.floodSeparator.items():
            if len(info) == 0:  # no valve process
                pass
            else:
                for i in info:
                    if i['valveTypeName'] == 'CARGO PIPE LINE VALVES':
                        #tank = param_dict['tank']
                        sequence_t = self.valve_filter.tankFilter(i, tank_list, param_dict['Cargo'])
                        sequence_f += sequence_t
                    else:
                        pass
        # print(sequence_f)
        return sequence_f

    def tankClose(self, param_dict, tank_list):
        sequence_c = []
        for stage, info in self.copShut.items():
            if len(info) == 0:  # no valve process
                pass
            else:
                for i in info:
                    if i['valveTypeName'] == 'CARGO PIPE LINE VALVES':
                        # tank = self.tanks_dict['close'][key]
                        # tank = param_dict['tank']
                        sequence_t = self.valve_filter.tankFilter(i, tank_list, param_dict['Cargo'])
                        sequence_c += sequence_t
                    else:
                        pass
        return sequence_c

    def flood_Separator(self, param_dict, tank_list):
        sequence_f = []
        for stage, info in self.floodSeparator.items():
            # f_valves = []
            if len(info) == 0:  # no valve process
                pass
            else:
                for i in info:
                    # print(i)
                    # raw_valves = vessel_json['vessel']['vesselValveSequence']['discharging']['floodingOfSeperator'][i]
                    if i['valveTypeName'] != 'CARGO PIPE LINE VALVES':
                        sequence_v = self.valve_filter.noFilter(i, param_dict['Cargo'])
                        sequence_f += sequence_v
                    else:
                        sequence_t = self.valve_filter.tankFilter(i, tank_list, param_dict['Cargo'])
                        sequence_f += sequence_t

        return sequence_f

    # print(self.valve_steps)
    def warmingCOP(self, param_dict, pump_open_list):
        sequence_w = []
        for stage, info in self.warmUpCop.items():
            # print(info)
            if len(info) == 0:  # no valve process
                pass
            else:
                for i in info:
                    if i['pumpName'] in pump_open_list:
                        #                             print(i['pumpName'])
                        # print(pump_open_list)
                        sequence_w += self.valve_filter.copFilter(i, param_dict['Cargo'], Start=True)
                        # print(sequence)
                    # else:
                    # pass
        return sequence_w

    def dryCheck(self, param_dict, pump_open_list):
        sequence_d = []
        for stage, info in self.warmUpCop.items():
            # print(info)
            if len(info) == 0:  # no valve process
                pass
            else:
                for i in info:
                    if i['pumpName'] in pump_open_list:
                        sequence_d += self.valve_filter.copFilter(i, param_dict['Cargo'], Start=True)
                        # print(sequence)
                    # else:
                    # pass
        return sequence_d

    def pumpingCOP(self, param_dict):
        sequence_p = []
        manifold_type = self.manifold.values()
        valve = self.manifold.keys()
        for stage, info in self.pumpingCop.items():
            if len(info) == 0:
                pass
            else:
                for i in info:
                    if i['valveTypeName'].startswith('MANIFOLD'):
                        if (i['manifoldName'] in valve) and (i['manifoldSide'] in self.manifold[i['manifoldName']]):
                            sequence_m = self.valve_filter.manifoldFilter(i, param_dict['Cargo'])
                            sequence_p += sequence_m

                    else:
                        sequence_v = self.valve_filter.noFilter(i, param_dict['Cargo'])
                        sequence_p += sequence_v
        return sequence_p

    def FreshoilDischarge(self,param_dict):
        #sequence_w = warmingCOP(param_dict,pump_open_list)
        sequence_p = []
        manifold_type = self.manifold.values()
        valve = self.manifold.keys()
        for stage,info in self.pumpingCop.items():
            if len(info) == 0:
                pass
            else:
                for i in info:
                    if i['valveTypeName'].startswith('MANIFOLD'):
                         if (i['manifoldName'] in valve) and (i['manifoldSide'] in self.manifold[i['manifoldName']]):
                                sequence_m = self.valve_filter.manifoldFilter(i,param_dict['Cargo'])
                                sequence_p += sequence_m
                    
                    else:
                        sequence_v = self.valve_filter.noFilter(i,param_dict['Cargo'])
                        sequence_p += sequence_v
        return sequence_p    

    def slopDischarge(self, param_dict):
        sequence_s = []
        manifold_type = self.manifold.values()
        valve = self.manifold.keys()
        for stage, info in self.pumpingCop.items():
            if len(info) == 0:
                pass
            else:
                for i in info:
                    if i['valveTypeName'].startswith('MANIFOLD'):
                        if (i['manifoldName'] in valve) and (i['manifoldSide'] in self.manifold[i['manifoldName']]):
                            sequence_m = self.valve_filter.manifoldFilter(i, param_dict['Cargo'])
                            sequence_s += sequence_m

                    else:
                        sequence_v = self.valve_filter.noFilter(i, param_dict['Cargo'])
                        sequence_s += sequence_v
        return sequence_s

    def fillingTCP(self, param_dict):
        sequence_t = []
        for stage, info in self.fillTCP.items():
            if len(info) == 0:
                pass
            else:
                for i in info:
                    if i['valveTypeName'].startswith(('H', 'I')):
                        if (i['tankShortName'] in param_dict['Drive_tank']):
                            valves = self.valve_filter.tcpFilter(i, param_dict['Cargo'])
                            sequence_t += valves
                    else:
                        valves = self.valve_filter.noFilter(i, param_dict['Cargo'])
                        sequence_t += valves
        return sequence_t

    def warmTCP(self, param_dict, tcp_open_list):
        sequence_w = []
        # print(tcp_open_list)
        for stage, info in self.warmUpTCP.items():
            if len(info) == 0:
                pass
            else:
                for i in info:
                    if i['pumpName'] in tcp_open_list:
                        # print(i)
                        valves = self.valve_filter.copFilter(i, param_dict['Cargo'], Start=True)
                        sequence_w += valves
        # print(sequence_w)
        return sequence_w

    def shutTCP(self, param_dict):
        sequence_w = []
        # print(tcp_open_list)
        for stage, info in self.warmUpTCP.items():
            if len(info) == 0:
                pass
            else:
                for i in info:
                    if i['pumpName'] == param_dict['Pump']:
                        # print(i)
                        valves = self.valve_filter.copFilter(i, param_dict['Cargo'], Start=False)
                        sequence_w += valves
        # print(sequence_w)
        return sequence_w

    def tankStripOpen(self, param_dict, tank_list):
        sequence_c = []
        for info in sorted(self.tankCOW.keys()):
            if len(info) == 0:  # no valve process
                pass
            else:
                for i in self.tankCOW[info]:
                    if i['sequenceNumber'] == 5:
                        # tank = self.cow_time['open'][key]
                        sequence_t = self.valve_filter.tankStripFilter(i, tank_list, param_dict['Cargo'], Start=True)
                        sequence_c += sequence_t
                    elif i['sequenceNumber'] in [1,2,3]:
                        pass
                    
                    else:
                        valves = self.valve_filter.cowFilter(i,param_dict['Cargo'],Start=True)
                        sequence_c += valves    
        # print(sequence_c)
        return sequence_c

    def tankStripClose(self, param_dict, tank_list):
        sequence_c = []
        for info in sorted(self.tankCOW.keys()):
            if len(info) == 0:  # no valve process
                pass
            else:
                for i in self.tankCOW[info]:
                    if i['sequenceNumber'] == 5:
                        # tank = self.cow_time['close'][key]
                        sequence_t = self.valve_filter.tankStripFilter(i, tank_list, param_dict['Cargo'], Start=False)
                        sequence_c += sequence_t
                    elif i['sequenceNumber'] in [1,2,3]:
                        pass
                    
                    else:
                        valves = self.valve_filter.cowFilter(i,param_dict['Cargo'],Start=False)
                        sequence_c += valves    
        return sequence_c

    def tankCowOpen(self,param_dict,tank_list):
        sequence_c= []
        for info in sorted(self.tankCOW.keys()):
            if len(info) == 0:  # no valve process
                pass
            else:
                for i in self.tankCOW[info]:
                    #print(i)
#                     if i['sequenceNumber'] == '4':
#                         pass
                    if i['sequenceNumber'] == 3:
                        #print('TANK LIST',tank_list)
                        #tank = self.cow_time['open'][key]
                        sequence_t = self.valve_filter.tankStripFilter(i,tank_list,param_dict['Cargo'],Start = True)
                        #print('sequence_t',sequence_t)
                        sequence_c += sequence_t
                    elif i['sequenceNumber'] == 5:
                        #tank = self.cow_time['open'][key]
                        sequence_t = self.valve_filter.tankStripFilter(i,tank_list,param_dict['Cargo'],Start = True)
                        sequence_c += sequence_t    
                    elif i['sequenceNumber'] in [1,2]:
                        pass
                    else:
                        valves = self.valve_filter.cowFilter(i,param_dict['Cargo'],Start=True)
                        sequence_c += valves
                        
        #print(sequence_c) 
        #print('sequence_c',sequence_c)
        return sequence_c
    
    def tankCowClose(self,param_dict,tank_list):
        sequence_c= []
        for info in sorted(self.tankCOW.keys()):
            if len(info) == 0:  # no valve process
                pass
            else:
                for i in self.tankCOW[info]:
#                     if i['sequenceNumber'] == '4':
#                         pass
                    if i['sequenceNumber'] == 3:
                        #tank = self.cow_time['open'][key]
                        sequence_t = self.valve_filter.tankStripFilter(i,tank_list,param_dict['Cargo'],Start = False)
                        sequence_c += sequence_t
                    elif i['sequenceNumber'] == 5:
                        #tank = self.cow_time['open'][key]
                        sequence_t = self.valve_filter.tankStripFilter(i,tank_list,param_dict['Cargo'],Start = False)
                        sequence_c += sequence_t
                    elif i['sequenceNumber'] in [1,2]:
                        pass
                    else:
                        valves = self.valve_filter.cowFilter(i,param_dict['Cargo'],Start=False)
                        sequence_c += valves
                        
        #print(sequence_c)                
        return sequence_c
    
    def COWPrep(self, param_dict, Start):
        sequence_c = []
        if 'SLP' in param_dict['Drive_tank']:
            tank = 'slopPortTank'
        elif 'SLS' in param_dict['Drive_tank']:
            tank = 'slopStbdTank'
        self.prepCOW_eductor = self.valves['eductionProcess'][tank]['general']['stage_1'][self.eductor]
        self.tankCOW = self.valves['eductionProcess'][tank]['tankStrippingAndCow']['stage_2'][self.eductor]
        # items_to_append=[self.prepCOW_eductor1,self.tankCOW]
        if Start:
            for info in sorted(self.prepCOW_eductor.keys()):
                if len(self.prepCOW_eductor[info]) == 0:
                    pass
                else:
                    for i in self.prepCOW_eductor[info]:
                        valves = self.valve_filter.cowFilter(i, param_dict['Cargo'], Start)
                        sequence_c += valves
            for info in sorted(self.tankCOW.keys()):
                if len(info) == 0:
                    pass
                else:
                    for i in self.tankCOW[info]:
                        if i['sequenceNumber'] in [4,3,5]:
                            pass
                        else:
                            valves = self.valve_filter.cowFilter(i, param_dict['Cargo'], Start)
                            sequence_c += valves
        else:
            for info in sorted(self.tankCOW.keys())[::-1]:
                if len(info) == 0:
                    pass
                else:
                    for i in self.tankCOW[info]:
                        if i['sequenceNumber'] in [4,3,5]:
                            pass
                        else:
                            valves = self.valve_filter.cowFilter(i, param_dict['Cargo'], Start)
                            sequence_c += valves
            for info in sorted(self.prepCOW_eductor.keys())[::-1]:
                if len(info) == 0:
                    pass
                else:
                    for i in self.prepCOW_eductor[info]:
                        # print(i)
                        valves = self.valve_filter.cowFilter(i, param_dict['Cargo'], Start)
                        sequence_c += valves

        # print(sequence_c)
        return sequence_c

    def slopStart(self, param_dict, Start):
        sequence_s = []
        strip_lines_dict = {'1':self.stripNo1,'2':self.stripNo2,'3':self.stripNo3,'bottom':self.stripbottom}
        line_dict = self.stripLines()
        line = []
        for name, value in line_dict.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
            if any(elem in param_dict['Drive_tank'] for elem in value):
                line.append(str(name)) 
        for item in self.strip_lines:
            if item in line:
                del strip_lines_dict[item]
            else:
                pass
        for item in strip_lines_dict.keys():
            if Start:
                item_arr = sorted(strip_lines_dict[item].keys())
            else:
                item_arr = sorted(strip_lines_dict[item].keys())[::-1]
            for info in item_arr:
                if (strip_lines_dict[item][info] == 0):
                    pass
                else:
                    for i in strip_lines_dict[item][info]:
                        valves = self.valve_filter.cowFilter(i, param_dict['Cargo'], Start)
                        sequence_s += valves
        return sequence_s

    def FinalStripStart(self, param_dict, Start):
        sequence_f = []
        manifold_side = list(self.manifold.values())
        manifold_side_list = [item for sublist in manifold_side for item in sublist]
        manifold_side_list = list(set(manifold_side_list))
        # Int_valve=  ['CDV80']
        # marpol_valve = ['CDV81','CDV82','CDV83','CDV84']
        line_dict = self.stripLines()
        line = []
        for name, value in line_dict.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
            if any(x in param_dict['Drive_tank'] for x in value):
                line.append(str(name))
            else:
                pass
                #line.append(str(name))
        for info in self.finalStripStart:
            # print("Line:"+str(line)+",Sequence Number:"+str(info['sequenceNumber'])+",Valve:"+str(info['valve']))
            if len(info) == 0:
                pass
            else:

                if info['pipeLineName'][-1] in line:
                    # print(info)
                    if (info['sequenceNumber'] == 22):

                        if info['valveSide'] in manifold_side_list:
                            # print(info)
                            valves = self.valve_filter.cowFilter(info, param_dict['Cargo'], Start=True)
                            sequence_f += valves

                    elif (info['sequenceNumber'] == 24):
                        if (info['manifoldName'] in list(self.manifold.keys())) and (info['manifoldSide'] in self.manifold[info['manifoldName']]):
                            valves = self.valve_filter.cowFilter(info, param_dict['Cargo'], Start=True)
                            sequence_f += valves
                    elif info['sequenceNumber'] == 23:
                        valves = self.valve_filter.cowFilter(info, param_dict['Cargo'], Start=False)
                        sequence_f += valves
                    else:
                        #                         print(info)
                        valves = self.valve_filter.cowFilter(info, param_dict['Cargo'], Start)
                        sequence_f += valves
        last_valve = [{'valve': 'Stripper Pump', 'operation': 'Open', 'Cargo': param_dict['Cargo']}]
        sequence_f += last_valve
        # print(sequence_f)
        return sequence_f

    def FinalStripMid(self, param_dict, Start):
        sequence_f = []
        line_dict = self.stripLines()
        line = []
        for name, value in line_dict.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
            if any(x in param_dict['Drive_tank'] for x in value):
                line.append(str(name))
            else:
                pass
                #line.append(str(name))
        for info in self.finalStripStart:
            if len(info) == 0:
                pass
            else:
                if info['pipeLineName'][-1] in line:
                    if info['sequenceNumber'] == 23:
                        valves = self.valve_filter.cowFilter(info, param_dict['Cargo'], Start)
                        sequence_f += valves
                    elif info['sequenceNumber'] == 17:
                        valves = self.valve_filter.cowFilter(info, param_dict['Cargo'], Start=False)
                        sequence_f += valves
                    else:
                        pass

        return sequence_f

    def FinalStripEnd(self, param_dict, Start):
        sequence_f = []
        manifold_side = list(self.manifold.values())
        manifold_side_list = [item for sublist in manifold_side for item in sublist]
        manifold_side_list = list(set(manifold_side_list))
        # Int_valve = ['CDV80']
        # marpol_valve = ['CDV81','CDV82','CDV83','CDV84']
        line_dict = self.stripLines()
        line = []
        for name, value in line_dict.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
            if any (x in param_dict['Drive_tank'] for x in value):
                line.append(str(name))
            else:
                pass
                #line.append(str(name))
        last_valve = [{'valve': 'Stripper Pump', 'operation': 'Close', 'Cargo': param_dict['Cargo']}]
        sequence_f += last_valve
        for info in self.finalStripStart[::-1]:
            if len(info) == 0:
                pass
            else:
                if info['pipeLineName'][-1] in line:
                    if info['sequenceNumber'] == 22:

                        if info['valveSide'] in manifold_side_list:
                            # print(info)
                            valves = self.valve_filter.cowFilter(info, param_dict['Cargo'], Start=False)
                            sequence_f += valves

                    elif info['sequenceNumber'] == 24:
                        if (info['manifoldName'] in list(self.manifold.keys())) and (info['manifoldSide'] in self.manifold[info['manifoldName']]):
                            valves = self.valve_filter.cowFilter(info, param_dict['Cargo'], Start=False)
                            sequence_f += valves
                    else:
                        valves = self.valve_filter.cowFilter(info, param_dict['Cargo'], Start)
                        sequence_f += valves

        return sequence_f

    def copSHUT(self, param_dict, tank_list, pump_open_list):
        sequence_s = []
        manifold_type = self.manifold.values()
        valve = self.manifold.keys()
        #         print(pump_open_list)
        for stage, info in self.copShut.items():
            if len(info) == 0:
                pass
            else:
                for i in info:
                    if i['valveTypeName'].startswith('MANIFOLD'):
                        if (i['manifoldName'] in valve) and (i['manifoldSide'] in self.manifold[i['manifoldName']]):
                            sequence_m = self.valve_filter.manifoldFilter(i, param_dict['Cargo'])
                            sequence_s += sequence_m

                    elif i['valveTypeName'] == 'CARGO PIPE LINE VALVES':
                        # tank = ['SLS','1C','3C','5C']
                        sequence_t = self.valve_filter.tankFilter(i, tank_list, param_dict['Cargo'])
                        sequence_s += sequence_t
                    elif i['pumpType'] == 'Cargo Pump':
                        if i['pumpName'] in pump_open_list:
                            #                             print(i)
                            sequence_p = self.valve_filter.copFilter(i, param_dict['Cargo'], Start=False)
                            sequence_s += sequence_p
                    else:
                        sequence_v = self.valve_filter.noFilter(i, param_dict['Cargo'])
                        sequence_s += sequence_v
        return sequence_s

    def PARShut(self, param_dict):
        sequence_s = []
        for stage, info in self.copShut.items():
            if len(info) == 0:
                pass
            else:
                for i in info:
                    if i['pumpName'] == param_dict['Pump']:
                        sequence_p = self.valve_filter.copFilter(i, param_dict['Cargo'], Start=False)
                        sequence_s += sequence_p
        return sequence_s


class ValveSequencingDischarge:
    def __init__(self, cow_sequence, constants, vessel_json):
        self.sequence = cow_sequence
        self.vessel_json = vessel_json
        self.constants = constants

    def get_pump_maps(self):
        pumps_map = self.vessel_json['vessel']['vesselPumps']
        pump_dict = {}
        for item in pumps_map:
            # print(item)
            for name in item.keys():
                pump_dict[str(item['pumpId'])] = item['pumpName']
                # print(item['pumpName'])
        return pump_dict

    def getParcelPumpInfo(self, pump_dict):
    #     pump_cargo_timings_df=pd.DataFrame()

        for parcel in range(len(self.sequence['events'])):
            parcel_pump_arr=[]
            parcel_valve_timelines=[]#TO CREATE PARCEL SPECIFIC DATAFRAME
            parcel_pumprate_dict={}
            parcel_cargo_dict = {}

            cargo_id=self.sequence['events'][parcel]['cargoNominationId']
            #print(cargo_id)
            for stage in self.sequence['events'][parcel]['sequence']:
                pump_event = stage['cargo']
                for id_,info in pump_event.items():
                    pump_id = pump_dict[str(id_)]
                    parcel_pump_arr.append(pump_id)
                    if(pump_id not in parcel_pumprate_dict):
                        parcel_pumprate_dict[pump_id]=[]
                        #print(parcel_pumprate_dict)
                    for item in info:
                        time_rate_dict = {}
                        time_rate_dict[float(item['timeStart'])] = item['rateM3_Hr']
                        time_rate_dict[float(item['timeEnd'])] = item['rateM3_Hr']
                        #print(time_rate_dict)
                        parcel_pumprate_dict[pump_id].append(time_rate_dict)
                        parcel_valve_timelines.append(float(item['timeStart']))
                        parcel_valve_timelines.append(float(item['timeEnd']))
                    #print(info)
            #print(parcel_pump_arr)

        #parcel_pump_arr
        return parcel_valve_timelines, parcel_pumprate_dict, parcel_pump_arr

    def get_pump_groupings(self, pump_dict):
        pump_grouping_keys = ['COP', 'GS', 'Ballast', 'TCP', 'BP', 'Stripping', 'COW', 'Cargo Stripping Eductor 1',
                              'Cargo Stripping Eductor 2']
        pump_reverse_groupings = {}
        pump_groupings = {}
        for pump_id in pump_dict.keys():
            for group in pump_grouping_keys:
                if group in pump_dict[pump_id]:
                    if (group not in pump_groupings):
                        pump_groupings[group] = []
                    pump_groupings[group].append(pump_dict[pump_id])
                    pump_reverse_groupings[pump_dict[pump_id]] = group
        return pump_groupings, pump_reverse_groupings

    def get_pump_min_max_timelines(self, parcel_pumprate_dict, pump_groupings, pump_reverse_groupings):
        eductor = ""
        pump_min_max_timeline_dict = {}
        for pump in parcel_pumprate_dict.keys():

            pump_timelines = parcel_pumprate_dict[pump]
            timelines_arr = []
            for pump_timeline in pump_timelines:
                for timeline in list(pump_timeline.keys()):
                    timelines_arr.append(timeline)
            # print(timelines_arr)
            if pump == 'TCP' and len(timelines_arr)>2:
                pump_min_max_timeline_dict[pump]=[timelines_arr[0],timelines_arr[1],timelines_arr[2],timelines_arr[3]]
            else:
                pump_min_max_timeline_dict[pump]=(min(timelines_arr),max(timelines_arr))

        pump_group_max_timelines = {}
        for group in pump_groupings.keys():
            pump_group_max_timelines[group] = 0
            for pump in (pump_min_max_timeline_dict.keys()):
                max_timeline = pump_min_max_timeline_dict[pump][1]
                if (pump in pump_groupings[group]):
                    group_Timeline = max_timeline
                    if (pump_group_max_timelines[group] < group_Timeline):
                        pump_group_max_timelines[group] = group_Timeline

        pump_status = {}
        for pump in (pump_min_max_timeline_dict.keys()):
            if (pump not in pump_status):
                pump_status[pump] = {}
            if len(pump_min_max_timeline_dict[pump])>2:
                max_timeline = pump_min_max_timeline_dict[pump][1]
                #print(max_timeline)
                min_timeline = pump_min_max_timeline_dict[pump][0]
                max_timeline_1 = pump_min_max_timeline_dict[pump][3]
                #print(max_timeline)
                min_timeline_1 = pump_min_max_timeline_dict[pump][2]
                #print(min_timeline)
            else:        
                max_timeline = pump_min_max_timeline_dict[pump][1]
                min_timeline = pump_min_max_timeline_dict[pump][0]
            pump_group = pump_reverse_groupings[pump]
            if (pump_group == "COP"):
                #min_timeline = (float(min_timeline) - 30.0)
                # print(min_timeline)
                pump_status[pump][min_timeline] = "Pump Open"
                if (max_timeline < pump_group_max_timelines[pump_group]):
                    pump_status[pump][max_timeline] = "PARSHUT"
                else:
                    pump_status[pump][max_timeline] = "COPSHUT"
            elif (pump_group == "Stripping"):
                pump_status[pump][min_timeline] = "Strip Pump Open"
                pump_status[pump][max_timeline] = "STRIPSHUT"
            elif (pump_group == "Cargo Stripping Eductor 1"):
                eductor = 'eductor1'
                pump_status[pump][min_timeline] = "Eductor Open"
                pump_status[pump][max_timeline] = "EductorSHUT"
            elif (pump_group == "Cargo Stripping Eductor 2"):
                eductor = 'eductor2'
                pump_status[pump][min_timeline] = "Eductor Open"
                pump_status[pump][max_timeline] = "EductorSHUT"
            elif (pump_group == "TCP"):
                if len(pump_min_max_timeline_dict[pump])>2:
                    min_timeline_1 = (float(min_timeline_1) - 28.0)
                    pump_status[pump][min_timeline_1]="TCP Pump Open"
                    pump_status[pump][max_timeline_1]="TCPSHUT"
                    pump_status[pump][min_timeline]="TCP Pump Open"
                    pump_status[pump][max_timeline]="TCPSHUT"
                else:        
                    min_timeline = (float(min_timeline) - 28.0)
                    pump_status[pump][min_timeline]="TCP Pump Open"
                    pump_status[pump][max_timeline]="TCPSHUT"

        return pump_min_max_timeline_dict, pump_group_max_timelines, pump_status, eductor

    def get_pump_min_max_timelines_dc(self, parcel_pumprate_dict, pump_groupings, pump_reverse_groupings, time_):
        flag_pump = False
        eductor = ""
        
        pump_min_max_timeline_dict = {}
        for pump in parcel_pumprate_dict.keys():
            sep_time_arr = []
            timelines_arr = []
            timelines = []
            # print(pump)
            pump_timelines = parcel_pumprate_dict[pump]
            for pump_timeline in pump_timelines:
                # print(pump_timeline)
                for element in list(pump_timeline.keys()):
                    timelines.append(element)
            if pump in ['COP1','COP2','COP3'] and len(timelines)>2:
                timeline_arr_done = False
                for i in range(len(timelines)):
                    if i == 0:
                        timelines_arr.append(timelines[0])
                    elif timeline_arr_done:
                        sep_time_arr.append(timelines[i])
                    elif timelines[i] not in timelines[i+1:]:
                        if timelines[i] == timelines[i-1]:
                            pass
                        else:
                            timelines_arr.append(timelines[i])
                            timeline_arr_done = True
                    else:
                       pass
            elif pump in ['TCP','Cargo Stripping Eductor 1','Cargo Stripping Eductor 2']:
                for timeline in timelines:
                    #if timeline>=time_:
                    timelines_arr.append(timeline)
            elif pump in ['COP1','COP2','COP3'] and len(timelines)<=2:
                for timeline in timelines:
                    timelines_arr.append(timeline)
            else:
                pass
            # print(timelines_arr)
            # print(sep_time_arr)
            if len(timelines_arr)>2 and pump == 'TCP':
                pump_min_max_timeline_dict[pump]=[timelines_arr[0],timelines_arr[1],timelines_arr[2],timelines_arr[3]]
            else:    
                pump_min_max_timeline_dict[pump]=[min(timelines_arr),max(timelines_arr)]
            if (len(sep_time_arr) > 0):
                pump_min_max_timeline_dict[pump].append(min(sep_time_arr))
                pump_min_max_timeline_dict[pump].append(max(sep_time_arr))

            # print(pump_min_max_timeline_dict)
            pump_group_max_timelines = {}
            for group in pump_groupings.keys():
                # print(group)
                pump_group_max_timelines[group] = 0
                for pump in (pump_min_max_timeline_dict.keys()):
                    # if flag_pump:
                    # print(pump)
                    if len(pump_min_max_timeline_dict[pump]) > 2:
                        max_timeline = pump_min_max_timeline_dict[pump][3]
                    else:
                        max_timeline = pump_min_max_timeline_dict[pump][1]
                    # print(max_timeline)
                    if (pump in pump_groupings[group]):
                        group_Timeline = max_timeline
                        # print(group_Timeline)
                        if (pump_group_max_timelines[group] < group_Timeline):
                            pump_group_max_timelines[group] = group_Timeline
            # print(pump_group_max_timelines)

            pump_status = {}
            for pump in (pump_min_max_timeline_dict.keys()):
                # print(pump)
                # if flag_pump:
                if len(pump_min_max_timeline_dict[pump]) > 2:
                    max_timeline = pump_min_max_timeline_dict[pump][1]
                    # print(max_timeline)
                    min_timeline = pump_min_max_timeline_dict[pump][0]
                    max_timeline_1 = pump_min_max_timeline_dict[pump][3]
                    # print(max_timeline)
                    min_timeline_1 = pump_min_max_timeline_dict[pump][2]
                    # print(min_timeline)
                else:
                    max_timeline = pump_min_max_timeline_dict[pump][1]
                    # print(max_timeline)
                    min_timeline = pump_min_max_timeline_dict[pump][0]
                    # print(min_timeline)
                if (pump not in pump_status):
                    pump_status[pump] = {}

                pump_group = pump_reverse_groupings[pump]
                if (pump_group == "COP"):
                    #min_timeline = (float(min_timeline) - 30.0)
                    # print(min_timeline)
                   
                    if len(pump_min_max_timeline_dict[pump]) > 2:
                        pump_status[pump][float(min_timeline)] = "Pump Open"
                        pump_status[pump][float(min_timeline_1) - 30.0] = "Pump Open"
                        pump_status[pump][max_timeline] = "PARSHUT"
                        if (max_timeline_1< pump_group_max_timelines['COP']):
                            pump_status[pump][max_timeline_1]="PARSHUT"
                        else:
                             pump_status[pump][max_timeline_1]="COPSHUT"
                    else:
                        pump_status[pump][float(min_timeline)]="Pump Open"
                        if (max_timeline< pump_group_max_timelines['COP']):
                            pump_status[pump][max_timeline]="PARSHUT"
                        else:
                            pump_status[pump][max_timeline]="COPSHUT"         
                    #elif (max_timeline < pump_group_max_timelines[pump_group]):
                        #pump_status[pump][max_timeline] = "PARSHUT"
                    #else:
                        #pump_status[pump][max_timeline] = "COPSHUT"
                elif (pump_group == "Stripping"):
                    pump_status[pump][min_timeline] = "Strip Pump Open"
                    pump_status[pump][max_timeline] = "STRIPSHUT"
                elif (pump_group == "Cargo Stripping Eductor 1"):
                    eductor = 'eductor1'
                    pump_status[pump][min_timeline] = "Eductor Open"
                    pump_status[pump][max_timeline] = "EductorSHUT"
                elif (pump_group == "Cargo Stripping Eductor 2"):
                    eductor = 'eductor2'
                    pump_status[pump][min_timeline] = "Eductor Open"
                    pump_status[pump][max_timeline] = "EductorSHUT"
                elif (pump_group == "TCP"):
                    if len(pump_min_max_timeline_dict[pump])>2:
                        min_timeline_1 = (float(min_timeline_1) - 28.0)
                        pump_status[pump][min_timeline_1]="TCP Pump Open"
                        pump_status[pump][max_timeline_1]="TCPSHUT"
                        
                        pump_status[pump][min_timeline]="TCP Pump Open"
                        pump_status[pump][max_timeline]="TCPSHUT"
                    else:
                        min_timeline = (float(min_timeline) - 28.0)
                        pump_status[pump][min_timeline]="TCP Pump Open"
                        pump_status[pump][max_timeline]="TCPSHUT"

        return pump_min_max_timeline_dict, pump_group_max_timelines, pump_status, eductor

    def create_df_pump_operations(self, parcel_pump_arr, parcel_valve_timelines, df_pump_rate, pump_status, id_):
        df_pump_operations = pd.DataFrame(index=parcel_pump_arr, columns=parcel_valve_timelines)
        df_pump_operations = df_pump_operations.rename(columns=float).sort_index(axis=1)
        for i in df_pump_rate.index:
            for j in range(len(df_pump_rate.columns)):
                col_name = df_pump_rate.columns[j]
                # print(col_name)
                if (i in pump_status and col_name in pump_status[i]):
                    # print("Here")
                    status = pump_status[i][col_name]
                    # print(status)
                    # print("Pump Status Column Name:"+str(col_name)+"-"+str(i))
                    info_dict = {}
                    info_dict[status] = {}
                    info_dict[status]['Cargo'] = id_
                    info_dict[status]['Pump'] = i
                    # curr_col=df_pump_rate.columns[j]
                    if (col_name not in df_pump_operations):
                        df_pump_operations[col_name] = np.nan
                    df_pump_operations.loc[i, col_name] = json.dumps(
                        info_dict)  # status+separator+str(cargo_id)+separator+i
        df_pump_operations = df_pump_operations.reindex(sorted(df_pump_operations.columns), axis=1)
        return df_pump_operations

    def create_df_pump_rate(self, parcel_pump_arr, parcel_valve_timelines, parcel_pumprate_dict):
        df_pump_rate = pd.DataFrame(index=parcel_pump_arr, columns=parcel_valve_timelines)
        df_pump_rate = df_pump_rate.rename(columns=float).sort_index(axis=1)

        for pumps in parcel_pumprate_dict.keys():
            for timeline in parcel_pumprate_dict[pumps]:
                for dischargetimes in list(timeline.keys()):
                    time_in_minutes = dischargetimes
                    rate = timeline[time_in_minutes]
                    df_pump_rate.loc[pumps][time_in_minutes] = rate
        return df_pump_rate

    def create_df_rate(self, parcel_tanksrate_dict, parcel_tanks_arr, parcel_valve_timelines):
        df_rate = pd.DataFrame(index=parcel_tanks_arr, columns=parcel_valve_timelines)
        df_rate = df_rate.rename(columns=float).sort_index(axis=1)
        for tanks in parcel_tanksrate_dict.keys():
            for timeline in parcel_tanksrate_dict[tanks]:
                for dischargetimes in list(timeline.keys()):
                    time_in_minutes = dischargetimes
                    rate = float(timeline[time_in_minutes])
                    df_rate.loc[tanks][time_in_minutes] = rate
        #df_rate = df_rate.ffill(axis=1).where(df_rate.bfill(axis=1).notnull())
        return df_rate

    def create_df_operations(self, df_rate, parcel_tanks_arr, parcel_valve_timelines, cargoid,sd_time,fo_time):

        df_operations = pd.DataFrame(index=parcel_tanks_arr, columns=parcel_valve_timelines)
        df_operations = df_operations.rename(columns=float).sort_index(axis=1)
        for i in df_rate.index:
            tank_opened = False
            tank_closed = False
            for j in range(len(df_rate.columns)):
                info_dict = {}
                col_name = df_rate.columns[j]
                dischargerate = float(df_rate.loc[i][col_name])
                # print("Checking:"+str(i)+"-"+str(df_rate.columns[j])+"-"+str(dischargerate))
                if (dischargerate>=0 and not tank_opened and tank_closed):
                    tank_opened=True
                    if i in ['SLP','SLS']:
                        opening_timeline = col_name 
                    elif col_name == fo_time:
                        opening_timeline = col_name    
                    else:    
                        opening_timeline = (col_name-self.constants.TANKOPEN_TIMELINE)                
                    #print(opening_timeline)
                    if(opening_timeline not in df_operations):
                        df_operations[opening_timeline]=np.repeat(np.nan,len(df_operations))
                    #info_dict['operation'] = [constants.TANKOPEN]
                    info_dict[self.constants.TANKOPEN]={}
                    info_dict[self.constants.TANKOPEN]['tank']=i
                    info_dict[self.constants.TANKOPEN]['Cargo']=cargoid
                    
                    df_operations.loc[i,opening_timeline]=json.dumps(info_dict) 
                
                if (dischargerate > 0 and not tank_opened):
                    tank_opened = True
                    if col_name == sd_time:
                        opening_timeline = col_name
                    elif col_name == fo_time:
                        opening_timeline = col_name
                    else:    
                        opening_timeline = (col_name - self.constants.TANKOPEN_TIMELINE)
                    # print(opening_timeline)
                    if (opening_timeline not in df_operations):
                        df_operations[opening_timeline] = np.repeat(np.nan, len(df_operations))
                    # info_dict['operation'] = [self.constants.TANKOPEN]
                    info_dict[self.constants.TANKOPEN] = {}
                    info_dict[self.constants.TANKOPEN]['tank'] = i
                    info_dict[self.constants.TANKOPEN]['Cargo'] = cargoid

                    df_operations.loc[i, opening_timeline] = json.dumps(info_dict)
                    # print(df_operations.loc[i][opening_timeline])

                elif (pd.isna(dischargerate) and tank_opened):
                    tank_closed = True
                    tank_opened = False
                    prev_col = df_rate.columns[j - 1]
                    # print("closing:"+str(i)+"-"+str(prev_col))
                    # info_dict['operation']=[self.constants.TANKCLOSE]
                    info_dict[self.constants.TANKCLOSE] = {}
                    info_dict[self.constants.TANKCLOSE]['tank'] = i
                    info_dict[self.constants.TANKCLOSE]['Cargo'] = cargoid
                    df_operations.loc[i, prev_col] = json.dumps(info_dict)
                    #break
                elif (j == len(df_rate.columns) - 1 and tank_opened):
                    curr_col = df_rate.columns[j]
                    info_dict[self.constants.TANKCLOSE] = {}
                    info_dict[self.constants.TANKCLOSE]['tank'] = i
                    info_dict[self.constants.TANKCLOSE]['Cargo'] = cargoid
                    df_operations.loc[i, curr_col] = json.dumps(info_dict)
        df_operations = df_operations.reindex(sorted(df_operations.columns), axis=1)
        return df_operations

    def update_df_operations(self, df_operations, cow_timing, drive_oil, id_):
        open_close_events = ['open', 'close']
        oc_event_map = {'open': self.constants.TANKCOWOPEN, 'close': self.constants.TANKCOWCLOSE}
        for ocevent in open_close_events:
            for timeline in cow_timing[ocevent]:
                if (timeline not in df_operations):
                    df_operations[timeline] = np.repeat(np.nan, len(df_operations))
                tanks = cow_timing[ocevent][timeline]
                for tank in tanks:
                    if tank in list(df_operations.index):
                        info_dict = df_operations.loc[tank,timeline]
                        if (pd.isna(info_dict)):
                            info_dict = {}
                        else:
                            info_dict = json.loads(info_dict)
                    else:
                        info_dict = {}
                    
                    info_dict[oc_event_map[ocevent]] = {}
                    info_dict[oc_event_map[ocevent]]['Cargo'] = id_
                    info_dict[oc_event_map[ocevent]]['Drive_tank'] = drive_oil
                    info_dict[oc_event_map[ocevent]]['Tank'] = tank
                    df_operations.loc[tank, timeline] = json.dumps(info_dict)
        return df_operations

    def update_df_operations_strip(self, df_operations, strip_timing, drive_oil, id_):
        open_close_events = ['open', 'close']
        oc_event_map = {'open': self.constants.TANKSTRIPOPEN, 'close': self.constants.TANKSTRIPCLOSE}
        for ocevent in open_close_events:
            for timeline in strip_timing[ocevent]:
                if (timeline not in df_operations):
                    df_operations[timeline] = np.repeat(np.nan, len(df_operations))
                tanks = strip_timing[ocevent][timeline]
                for tank in tanks:
                    if tank in list(df_operations.index):
                        info_dict = df_operations.loc[tank,timeline]
                        if (pd.isna(info_dict)):
                            info_dict = {}
                        else:
                            info_dict = json.loads(info_dict)
                    else:
                        info_dict = {}
                    
                    info_dict[oc_event_map[ocevent]] = {}
                    info_dict[oc_event_map[ocevent]]['Cargo'] = id_
                    info_dict[oc_event_map[ocevent]]['Drive_tank'] = drive_oil
                    info_dict[oc_event_map[ocevent]]['Tank'] = tank
                    df_operations.loc[tank, timeline] = json.dumps(info_dict)
        return df_operations
    
    def update_common_operation(self, df_operations, parcel_cargo_stage_dict, id_):
        tanks = list(df_operations.index)
        for cargo_id in parcel_cargo_stage_dict.keys():
            cargo_info = parcel_cargo_stage_dict[cargo_id][0]
            for drive_oil in cargo_info.keys():
                drive_oil_info = cargo_info[drive_oil][0]
                for operation in drive_oil_info.keys():
                    timeline = drive_oil_info[operation]
                    # print(timeline)
                    for tank in tanks:
                        # print(str(tank)+","+str(timeline)+","+operation)
                        if (timeline in df_operations):
                            cell_value = df_operations.loc[tank, timeline]
                            # print(cell_value)
                            if (not pd.isna(cell_value)):
                                info_dict = json.loads(df_operations.loc[tank, timeline])
                            #                                 print(info_dict)
                            else:
                                info_dict = {}
                                # info_dict['operation']=[]
                                # info_dict['Drive_tank'] = []
                        else:
                            info_dict = {}
                            # info_dict['operation']=[]
                            # info_dict['Drive_tank'] = []
                        # info_dict['Drive_tank'] = []
                        # info_dict['operation'].append(operation)
                        info_dict[operation] = {}
                        info_dict[operation]['Drive_tank'] = drive_oil
                        info_dict[operation]['Cargo'] = id_
                        df_operations.loc[tank, timeline] = json.dumps(info_dict)
        return df_operations

    def compute_parcel_cargo_stage_dict(self, events, stage, special_stages, parcel_stage_dict, parcel_stage_arr,
                                        parcel_time_arr, parcel_oil_dict, parcel_cargo_stage_dict, \
                                        drive_oil, id_):
        for event in events:
            if event == stage['stage']:
                # print(stage)
                # print("#####################")
                category = event
                for info in special_stages:
                    if (info in 'COWStripping') and (info in category):
                        if stage['cowStartTime'] != None:
                            fillTCP_time_start = float(stage['cowStartTime']) - 30.0
                            parcel_stage_dict['FillingTCP'] = fillTCP_time_start
                            warmTCP_time_start = float(stage['cowStartTime']) - 28.0
                            parcel_stage_dict['warmTCP'] = warmTCP_time_start
                    if (info in 'slopDischarge') and (info in category):
                        slopmid_time_start = float(stage['timeStart']) + 30.0
                        parcel_stage_dict['slopDischarge_mid'] = slopmid_time_start
                    if (info in 'finalStripping') and (info in category):
                        fsmid_time_start = float(stage['timeStart']) + 40.0
                        parcel_stage_dict['finalStripping_mid'] = fsmid_time_start
                    if info in category:
                        time_end = stage['timeEnd']
                        parcel_stage_dict[info + '_end'] = float(time_end)
                parcel_stage_arr.append(event)
                parcel_stage_dict[category] = []

            else:
                if category == 'COWStripping':
                    if 'cowStartTime' in stage and stage['cowStartTime'] != None:
                        time_start = stage['cowStartTime']
                        parcel_stage_dict[category] = float(time_start)
                        parcel_time_arr.append(time_start)
                    else:
                        parcel_time_arr.append(event)
                        parcel_stage_dict[category] = float(event)
                else:
                    parcel_time_arr.append(event)
                    parcel_stage_dict[category] = float(event)
        #         print(parcel_stage_dict)
        if (drive_oil not in parcel_oil_dict):
            parcel_oil_dict[drive_oil] = []
            parcel_oil_dict[drive_oil].append(parcel_stage_dict)
        if (id_ not in parcel_cargo_stage_dict):
            parcel_cargo_stage_dict[id_] = []
            parcel_cargo_stage_dict[id_].append(parcel_oil_dict)
        return parcel_cargo_stage_dict

    def compute_parcel_pumprate_dict(self, pump_event, pump_dict, parcel_pumprate_dict, parcel_pump_arr,
                                     parcel_valve_timelines):
        for event in pump_event:
            for id_, info in event.items():
                pump_id = pump_dict[str(id_)]
                parcel_pump_arr.append(pump_id)
                if (pump_id not in parcel_pumprate_dict):
                    parcel_pumprate_dict[pump_id] = []
                for item in info:
                    time_rate_dict = {}
                    time_rate_dict[float(item['timeStart'])] = item['rateM3_Hr']
                    time_rate_dict[float(item['timeEnd'])] = item['rateM3_Hr']
                    parcel_pumprate_dict[pump_id].append(time_rate_dict)
                    parcel_valve_timelines.append(float(item['timeStart']))
                    parcel_valve_timelines.append(float(item['timeStart']) - 30)
                    parcel_valve_timelines.append(float(item['timeStart']) - 60)
                    parcel_valve_timelines.append(float(item['timeStart']) - 28)
                    parcel_valve_timelines.append(float(item['timeEnd']))
        return parcel_pumprate_dict, parcel_pump_arr, parcel_valve_timelines

    def compute_parcel_tanksrate_dict(self, events, parcel_tanksrate_dict, parcel_tanks_arr, parcel_valve_timelines):
        for event in events:
            if (len(event.keys()) > 0):
                for tank in event.keys():
                    tank_details = event[tank]
                    parcel_tanks_arr.append(tank_details[self.constants.TANKSHORTNAME])
                    if (tank_details[self.constants.TANKSHORTNAME] not in parcel_tanksrate_dict):
                        parcel_tanksrate_dict[tank_details[self.constants.TANKSHORTNAME]] = []
                    time_rate_dict = {}
                    time_rate_dict[float(tank_details[self.constants.TIMESTART])] = tank_details[self.constants.RATE]
                    time_rate_dict[float(tank_details[self.constants.TIMEEND])] = tank_details[self.constants.RATE]
                    parcel_tanksrate_dict[tank_details[self.constants.TANKSHORTNAME]].append(time_rate_dict)

                    parcel_valve_timelines.append(float(tank_details[self.constants.TIMESTART]))
                    parcel_valve_timelines.append(float(tank_details[self.constants.TIMEEND]))
        return parcel_tanksrate_dict, parcel_tanks_arr, parcel_valve_timelines

    def create_cleaning_cow_timing_dict(self, clean_event, cow_timing):
        # cow_timing = {'open' :{},'close':{}}
        for info in clean_event.keys():
            for element in clean_event[info]:
                # print(element)
                time_start = float(element['timeStart'])
                time_end = float(element['timeEnd'])
                if time_start not in cow_timing['open']:
                    cow_timing['open'][time_start] = [element['tankShortName']]
                else:
                    cow_timing['open'][time_start].append(element['tankShortName'])
                if time_end not in cow_timing['close']:
                    cow_timing['close'][time_end] = [element['tankShortName']]
                else:
                    cow_timing['close'][time_end].append(element['tankShortName'])
        return cow_timing

    def create_stripping_cow_timing_dict(self, stripping_event, strip_timing):
        # cow_timing = {'open' :{},'close':{}}
        for element in stripping_event:
            time_start = float(element['timeStart'])
            time_end = float(element['timeEnd'])
            if time_start not in strip_timing['open']:
                strip_timing['open'][time_start] = [element['tankShortName']]
            else:
                strip_timing['open'][time_start].append(element['tankShortName'])
            if time_end not in strip_timing['close']:
                strip_timing['close'][time_end] = [element['tankShortName']]
            else:
                strip_timing['close'][time_end].append(element['tankShortName'])
        return strip_timing

    def create_display_df(self, df):
        index_list = df.index
        column_list = df.columns
        df_display = pd.DataFrame(index=index_list, columns=column_list)
        for index in index_list:
            for column in column_list:
                info_dict = df.loc[index, column]
                # print(str(index)+","+str(column)+"="+str(info_dict))
                # print("========================")
                if (not pd.isna(info_dict)):
                    info_dict = json.loads(info_dict)
                    df_display.loc[index, column] = list(info_dict.keys())
        return df_display

    def union1(self, x):
        # print(x)
        # print("Length:"+str(len(x)))
        cell_vals = x.dropna()
        result = {}
        for d in list(cell_vals):
            d = json.loads(d)
            result.update(d)
        # print("---------------------")
        # print(result)
        # print("--------------------")
        # print("*********************")
        if (len(result.keys()) > 0):
            return json.dumps(result)
        else:
            return np.nan

    def combinecols(self,y):
        y_vals = list(y)
        final_dict={}
        value_found=False
        #print(y_vals)
        for val in y_vals:
            if(not pd.isna(val)):
                value_found=True
                #print(dict(val))
                final_dict.update(json.loads(val))
        if(value_found):
            return json.dumps(final_dict)
        else:
            return val   

    def df_final_merged_operations(self, sequence):
        separator = "#"
        info_dict = {}
        pump_timings = {}
        df_pump_rate_arr = []
        df_pump_operations_arr = []
        pump_dict = self.get_pump_maps()
        parcel_valve_timelines, parcel_pumprate_dict, parcel_pump_arr = self.getParcelPumpInfo(pump_dict)
        pump_groupings, pump_reverse_groupings = self.get_pump_groupings(pump_dict)
        special_stages = ['COWStripping', 'reducedRate', 'finalStripping', 'slopDischarge','freshOilDischarge']
        parcel_cargo_stage_arr = []
        parcel_df_rates_arr = []
        parcel_df_operations_arr = []
        df_merged_operations_arr = []
        id_ = 0
        
        sd_time = None
        fo_time = None
        for parcel in range(len(sequence['events'])):
            dc = False
            #############CARGO RELATED EVENTS####################
            parcel_stage_arr = []
            parcel_time_arr = []  # TO CREATE PARCEL SPECIFIC DATAFRAME
            parcel_stage_dict = {}
            parcel_oil_dict = {}
            parcel_cargo_stage_dict = {}

            #############PUMP RELATED EVENTS#####################
            parcel_pump_arr = []  # TO CREATE PARCEL SPECIFIC DATAFRAME
            parcel_valve_timelines_pump = []  # TO CREATE PARCEL SPECIFIC DATAFRAME
            parcel_pumprate_dict = {}
            # parcel_cargo_dict = {}

            ############Tank DISCHARGE EVENTS########################
            parcel_tanks_arr = []  # TO CREATE PARCEL SPECIFIC DATAFRAME
            parcel_valve_timelines = []  # TO CREATE PARCEL SPECIFIC DATAFRAME
            parcel_tanksrate_dict = {}

            ############CLEANING EVENTS##############################
            cow_timing = {'open': {}, 'close': {}}
            strip_timing = {'open' : {}, 'close': {}}
            cargo_id = sequence['events'][parcel]['cargoNominationId']
            drive_tank = []
            for element in sequence['events'][parcel]['driveTank']:
                drive_tank.append(element['tankShortName'])
            drive_oil = tuple(drive_tank)
            for stage in sequence['events'][parcel]['sequence']:
                if (stage['stage'] == 'COWStripping' and parcel == len(sequence['events'])-1):
                    time_ =  float(stage['timeStart'])
                    #print('time_',time_)
                    dc = True
                elif stage['stage'] == 'slopDischarge':
                    sd_time = float(stage['timeStart'])
                elif stage['stage'] == 'freshOilDischarge':
                    fo_time = float(stage['timeStart'])    
                
                else:
                    pass

                #############CARGO RELATED EVENTS####################

                cargo_event = [stage['stage'], stage['timeStart']]
                parcel_cargo_stage_dict = self.compute_parcel_cargo_stage_dict(cargo_event, stage, special_stages,
                                                                               parcel_stage_dict, parcel_stage_arr,
                                                                               parcel_time_arr, parcel_oil_dict,
                                                                               parcel_cargo_stage_dict, drive_oil, id_)

                #############PUMP RELATED EVENTS#####################
                pump_event = [stage['cargo'], stage['STPED'], stage['TCP']]
                parcel_pumprate_dict, parcel_pump_arr, parcel_valve_timelines_pump = self.compute_parcel_pumprate_dict(
                    pump_event, pump_dict, parcel_pumprate_dict, parcel_pump_arr, parcel_valve_timelines_pump)

                ############DISCHARGE EVENTS########################
                events = stage['simCargoDischargingRatePerTankM3_Hr']
                parcel_tanksrate_dict, parcel_tanks_arr, parcel_valve_timelines = self.compute_parcel_tanksrate_dict(
                    events, parcel_tanksrate_dict, parcel_tanks_arr, parcel_valve_timelines)

                ############CLEANING EVENT##########################
                cleaning_event = stage['Cleaning']
                cow_timing = self.create_cleaning_cow_timing_dict(cleaning_event, cow_timing)

                ############CLEANING EVENT##########################
                stripping_event = stage['stripping']
                strip_timing = self.create_stripping_cow_timing_dict(stripping_event, strip_timing)
                # print(cow_timing)

            parcel_cargo_stage_arr.append(parcel_cargo_stage_dict)
            # print(cow_timing)
            # print("#########################")

            if dc:
                pump_min_max_timeline_dict, pump_group_max_timelines, pump_status, eductor = self.get_pump_min_max_timelines_dc(
                    parcel_pumprate_dict, pump_groupings, pump_reverse_groupings, time_)
            else:
                pump_min_max_timeline_dict, pump_group_max_timelines, pump_status, eductor = self.get_pump_min_max_timelines(
                    parcel_pumprate_dict, pump_groupings, pump_reverse_groupings)
            #             print("Pump Status:"+str(pump_status))

            ##############Tank Related DataFrame Creation################
            parcel_tanks_arr = np.unique(parcel_tanks_arr)
            parcel_valve_timelines = np.unique(parcel_valve_timelines)

            df_rate = self.create_df_rate(parcel_tanksrate_dict, parcel_tanks_arr, parcel_valve_timelines)
            df_operations = self.create_df_operations(df_rate, parcel_tanks_arr, parcel_valve_timelines, id_,sd_time,fo_time)
            # print(df_operations)
            ################CLEANING RELATED EVENT######################
            df_operations = self.update_df_operations(df_operations, cow_timing, drive_oil, id_)
            df_operations = self.update_df_operations_strip(df_operations, strip_timing, drive_oil, id_)
            # print(df_operations)
            df_operations = self.update_common_operation(df_operations, parcel_cargo_stage_dict, id_)

            #############Pump Related DataFrame Creation################
            parcel_pump_arr = np.unique(parcel_pump_arr)
            parcel_valve_timelines_pump = np.unique(parcel_valve_timelines_pump)

            df_pump_rate = self.create_df_pump_rate(parcel_pump_arr, parcel_valve_timelines_pump, parcel_pumprate_dict)
            df_pump_rate_arr.append(df_pump_rate)

            df_pump_operations = self.create_df_pump_operations(parcel_pump_arr, parcel_valve_timelines_pump,
                                                                df_pump_rate, pump_status, id_)
            df_pump_operations_arr.append(df_pump_operations)
            # print(parcel_valve_timelines_pump)
            #     df_merged_operations = pd.concat([df_operations,df_pump_operations],axis=0,sort=True)
            #     df_merged_operations_arr.append(df_merged_operations)

            parcel_df_rates_arr.append(df_rate)
            parcel_df_operations_arr.append(df_operations)
            id_ = id_ + 1
        df_pump_operations_final = pd.concat(df_pump_operations_arr, axis=1)
        df_pump_final = df_pump_operations_final.groupby(level=0, axis=1).apply(lambda y: y.apply(self.combinecols, axis=1))
        df_rates_master = pd.concat(parcel_df_rates_arr)
        df_operations_master = pd.concat(parcel_df_operations_arr, sort=True)
        df_operations_master_final = df_operations_master.groupby(level=0, axis=1).apply(lambda y: y.apply(self.combinecols, axis=1))
        df_merged_final = pd.concat([df_operations_master_final, df_pump_final], sort=True)
        # pd.merge(df1, df2, left_index=True, right_index=True))
        # df_operations_final = pd.DataFrame()
        # for i in parcel_df_operations_arr:
        #     print(i)
        #     df_operations_final = df_operations_final.append(i)
        # df_final = df_operations_master.select_dtypes(object).groupby(level=0).first()
        # df_pump_operations_final
        df_merged_final_grouped = df_merged_final.groupby(by=df_merged_final.index).agg(self.union1)
        return df_merged_final_grouped, eductor

    def generate_sequence(self, valve_operation, df_merged_final_grouped):
        common_operations = ['floodSeparator', 'warmPumps', 'initialRate', 'TCPSHUT', 'FillingTCP', 'warmTCP',
                             'PARSHUT', 'COWStripping', 'COWStripping_end','freshOilDischarge','dryCheck', 'finalStripping',
                             'finalStripping_mid', 'finalStripping_end', 'slopDischarge_mid', 'slopDischarge',
                             'slopDischarge_end']
        Tank_specific_operations = ['TankOpen', 'TankClose', 'Tso', 'Tsc', 'Pump Open', 'TCP Pump Open', 'COPSHUT','Tco','Tcc']
        no_operations = ['increaseToMaxRate', 'reducedRate_end','freshOilDischarge_end']
        valve_dict = {}

        for (columnName, columnData) in df_merged_final_grouped.iteritems():

            key = columnName
            valve_dict[key] = []
            operation = []
            dict_ = {}
            dict_cp = {}
            FS_encountered = False
            drycheck_encountered = False
            warmpumps_encountered = False
            fo_encountered = False
            flag_dict = {'floodSeparator': False,'freshOilDischarge':False,'Tso': False, 'Tsc': False, 'PARSHUT': False, 'warmPumps': False,
                         'initialRate': False, 'COPSHUT': False, 'FillingTCP': False, 'warmTCP': False,
                         'COWStripping': False, 'COWStripping_end': False, 'TCPSHUT': False, 'dryCheck': False,
                         'finalStripping_mid': False, 'finalStripping': False, 'finalStripping_end': False,
                         'slopDischarge_mid': False, 'slopDischarge': False, 'slopDischarge_end': False,'Tco': False,'Tcc' : False}
            #             print('Column Name : ', columnName)
            tank_list = []
            tank_close_list = []
            tso_list = []
            tsc_list = []
            tco_list = []
            tcc_list = []
            pump_open_list = []
            tcp_open_list = []
            pump_shut_list = []
            special_ops = ['Tso', 'Tsc', 'COPSHUT', 'TankClose','TankOpen','Pump Open','Tco','Tcc']
            special_ops_arr = [tso_list, tsc_list, pump_shut_list, tank_close_list,tank_list,pump_open_list,tco_list,tcc_list]
            param_dict_tso, param_dict_tsc, param_dict_copshut, param_dict_tc,param_dict_to,param_dict_po,param_dict_tco,param_dict_tcc = {}, {}, {}, {},{},{},{},{}
            for element in columnData.values:

                if not pd.isna(element):
                    cell_value = json.loads(element)
                    for op in cell_value.keys():
                        if op in Tank_specific_operations:
                            if op == 'TankOpen':
                                param_dict_to = cell_value[op]
                                tank_list.append(param_dict_to['tank'])
                            elif op == 'TankClose':
                                param_dict_tc = cell_value[op]
                                # print()
                                tank_close_list.append(param_dict_tc['tank'])
                            elif op == 'Pump Open':
                                param_dict_po = cell_value[op]
                                pump_open_list.append(param_dict_po['Pump'])
                            elif op == 'TCP Pump Open':
                                param_dict_tcp = cell_value[op]
                                # print(param_dict_tcp)
                                tcp_open_list.append(param_dict_tcp['Pump'])
                            elif op == 'Tso':
                                param_dict_tso = cell_value[op]
                                tso_list.append(param_dict_tso['Tank'])
                            elif op == 'Tsc':
                                param_dict_tsc = cell_value[op]
                                tsc_list.append(param_dict_tsc['Tank'])
                            elif op == 'Tco':
                                param_dict_tco = cell_value[op]
                                tco_list.append(param_dict_tco['Tank'])
                            elif op == 'Tcc':
                                param_dict_tcc = cell_value[op]
                                tcc_list.append(param_dict_tcc['Tank'])    
                            elif op == 'COPSHUT':
                                param_dict_copshut = cell_value[op]
                                # print(param_dict_copshut)
                                pump_shut_list.append(param_dict_copshut['Pump'])
                                # cargo_id=param_dict_copshut['Cargo']
                                # tsc_list .append()
                        elif (op in common_operations) and (flag_dict[op] == False):
                            if op == 'floodSeparator':
                                flag_dict[op] = True
                                dict_fs = cell_value[op]
                                operation.append(op)
                                FS_encountered = True
                            elif op == 'dryCheck':
                                flag_dict[op] = True
                                drycheck_encountered = True
                                dict_dc = cell_value[op]
                                operation.append(op)
                            elif op == 'warmPumps':
                                flag_dict[op] = True
                                warmpumps_encountered = True
                                dict_wp = cell_value[op]
                                operation.append(op)
                            elif op =='freshOilDischarge':
                                flag_dict[op] = True
                                fo_encountered = True
                                dict_fo = cell_value[op]
                                operation.append(op)    
                            elif op == 'warmTCP':
                                flag_dict[op] = True
                                # warmTCP_encountered = True
                                dict_TCP = cell_value[op]
                                operation.append(op)
                            elif op == 'COWStripping':
                                flag_dict[op] = True
                                param_dict = cell_value[op]
                                valves = valve_operation.key_operation_mapping[op](param_dict, Start=True)
                                valve_dict[key] += valves

                            elif op == 'COWStripping_end':
                                flag_dict[op] = True
                                param_dict = cell_value[op]
                                valves = valve_operation.key_operation_mapping[op](param_dict, Start=False)
                                valve_dict[key] += valves

                            elif op == 'slopDischarge':
                                flag_dict[op] = True
                                #                                 print(op)
                                param_dict = cell_value[op]
                                valves = valve_operation.key_operation_mapping[op](param_dict, Start=True)
                                valve_dict[key] += valves

                            elif op == 'slopDischarge_end':
                                flag_dict[op] = True
                                param_dict = cell_value[op]
                                valves = valve_operation.key_operation_mapping[op](param_dict, Start=False)
                                valve_dict[key] += valves
                            elif op == 'slopDischarge_mid':
                                flag_dict[op] = True
                                param_dict = cell_value[op]
                                valves = valve_operation.key_operation_mapping[op](param_dict)
                                valve_dict[key] += valves

                            elif op == 'finalStripping':
                                # print(op)
                                flag_dict[op] = True
                                param_dict = cell_value[op]
                                # print("****************************")
                                # print("PARAM DICT:"+str(param_dict))
                                # print("****************************")
                                valves = valve_operation.key_operation_mapping[op](param_dict, Start=True)
                                valve_dict[key] += valves

                            elif op == 'finalStripping_mid':
                                # print(op)
                                flag_dict[op] = True
                                param_dict = cell_value[op]
                                valves = valve_operation.key_operation_mapping[op](param_dict, Start=True)
                                valve_dict[key] += valves

                            elif op == 'finalStripping_end':
                                flag_dict[op] = True
                                param_dict = cell_value[op]
                                valves = valve_operation.key_operation_mapping[op](param_dict, Start=False)
                                valve_dict[key] += valves

                            else:
                                flag_dict[op] = True
                                param_dict = cell_value[op]
                                valves = valve_operation.key_operation_mapping[op](param_dict)
                                valve_dict[key] += valves
                        #                                 print(valves)

                        elif (op in no_operations):
                            pass
            special_ops_param_arr = [param_dict_tso, param_dict_tsc, param_dict_copshut, param_dict_tc,param_dict_to,param_dict_po,param_dict_tco,param_dict_tcc]
            copshut = 0
            for sp_item in range(len(special_ops)):

                sp_op = special_ops[sp_item]
                if (len(special_ops_arr[sp_item]) > 0):
                    # print("**************************")
                    # print(special_ops_param_arr[sp_item])
                    # print(special_ops_arr[sp_item])
                    # print("**************************")
                    if (sp_op == 'COPSHUT'):
                        copshut = 1
                        #                         print(tank_close_list)
                        # valve_dict[key] =
                        sp_valve_seq = valve_operation.key_operation_mapping[sp_op](special_ops_param_arr[sp_item],
                                                                                    tank_close_list,
                                                                                    special_ops_arr[sp_item])
                        # print(sp_valve_seq)
                        valve_dict[key] += sp_valve_seq
                    elif (sp_op =='TankOpen' and FS_encountered == False):
                        #print('Here')
                        #print(special_ops_arr[sp_item])
                        sp_valve_seq = valve_operation.key_operation_mapping[sp_op](special_ops_param_arr[sp_item],special_ops_arr[sp_item]) 
                        #print(sp_valve_seq)
                        valve_dict[key] += sp_valve_seq
                
                    elif (sp_op =='Pump Open' and warmpumps_encountered == False):
                        sp_valve_seq = valve_operation.key_operation_mapping[sp_op](special_ops_param_arr[sp_item],special_ops_arr[sp_item]) 
                        valve_dict[key] += sp_valve_seq
                    elif (sp_op == 'TankClose'):
                        if copshut == 1:
                            pass
                        else:
                            sp_valve_seq = valve_operation.key_operation_mapping[sp_op](special_ops_param_arr[sp_item],
                                                                                        special_ops_arr[sp_item])
                            valve_dict[key] += sp_valve_seq
                        # print(sp_valve_seq)
                    elif sp_op in ['Tso','Tsc']:                
                        sp_valve_seq = valve_operation.key_operation_mapping[sp_op](special_ops_param_arr[sp_item],special_ops_arr[sp_item])
                        valve_dict[key] += sp_valve_seq
                    elif sp_op in ['Tco','Tcc']:                
                        sp_valve_seq = valve_operation.key_operation_mapping[sp_op](special_ops_param_arr[sp_item],special_ops_arr[sp_item])
                        valve_dict[key] += sp_valve_seq    
                    else:
                        pass

            # if(len(pump_shut_list)>0):
            #    cop_op='COPSHUT'
            #    valve_dict[key] = valve_operation.key_operation_mapping[cop_op](param_dict_copshut,pump_shut_list)
            # print(operation)
            # print(pump_open_list)
            # print(tsc_list)
            #             print(tcp_open_list)
            for element in operation:
                # print(element)
                if element == 'floodSeparator':
                    valves = valve_operation.key_operation_mapping[element](dict_fs, tank_list)
                    valve_dict[key] += valves

                #         elif element == 'COPSHUT':
                #             if key not in valve_dict:
                #                 valve_dict[key] = valve_operation.key_operation_mapping[element](dict_cp,tank_close_list,pump_open_list)
                #             else:
                #                  valve_dict[key].append(valve_operation.key_operation_mapping[element](dict_cp,tank_close_list,pump_open_list))
                #         elif element == 'Tso':
                #             if key not in valve_dict:
                #                 valve_dict[key] = valve_operation.key_operation_mapping[element](param_dict_tso,tso_list)
                #             else:
                #                  valve_dict[key].append(valve_operation.key_operation_mapping[element](param_dict_tso,tso_list))
                #         elif element == 'Tsc':
                #             if key not in valve_dict:
                #                 valve_dict[key] = valve_operation.key_operation_mapping[element](param_dict_tsc,tsc_list)
                #             else:
                #                  valve_dict[key].append(valve_operation.key_operation_mapping[element](param_dict_tsc,tsc_list))
                elif element == 'warmPumps':
                    valves = valve_operation.key_operation_mapping[element](dict_wp, pump_open_list)
                    valve_dict[key] += valves
                elif element == 'dryCheck':
                    valves = valve_operation.key_operation_mapping[element](dict_dc, pump_open_list)
                    valve_dict[key] += valves

                elif element == 'warmTCP':
                    # print(dict_TCP)
                    valves = valve_operation.key_operation_mapping[element](dict_TCP, tcp_open_list)
                    valve_dict[key] += valves

        valve_dict_final = {}

        for valve_time in valve_dict.keys():

            if valve_dict[valve_time]:
                valve_dict_final[valve_time] = []
                valve_dict_final[valve_time] += valve_dict[valve_time]
        return valve_dict_final


class ValveConversion:
    def __init__(self, final_json, constants):
        self.constants = constants
        self.json = final_json
        return

    def getValveInfo(self, valve, time):
        valves_code = valve[self.constants.VALVE] if len(valve[self.constants.VALVE]) > 0 else valve[
            self.constants.PUMP]
        json = {self.constants.TIME_JSON: time, self.constants.OP_JSON: valve[self.constants.VALVE_OP_VARIABLE],
                self.constants.VALVES_JSON: [valves_code]}
        operation = valve[self.constants.VALVE_OP_VARIABLE]
        return json, operation

    def convertValves(self, valves_dict, field):
        for c in range(len(self.json[self.constants.EVENTS])):
            for stage in range(len(self.json[self.constants.EVENTS][c][self.constants.SEQUENCE])):
                stage_info = self.json[self.constants.EVENTS][c][self.constants.SEQUENCE][stage]
                timeStart = float(stage_info[self.constants.TIMESTART])
                timeEnd = float(stage_info[self.constants.TIMEEND])
                if stage == (len(self.json[self.constants.EVENTS][c][self.constants.SEQUENCE]) - 1):
                    timeEnd = timeEnd + 1
                valves = {}
                for t in valves_dict:
                    if (t >= timeStart) & (t < timeEnd):
                        if t in valves:
                            valves[t] += valves_dict[t]
                        else:
                            valves[t] = valves_dict[t]

                cargoValves = []
                json = {}
                operation = None
                prev_time = None
                #if str(c) == '3':
                    #cargo = '1'
                #else:
                cargo = str(c)
                for time, valve_arr in valves.items():
                    for valve in valve_arr:
                        if str(valve[self.constants.CARGO]) == cargo:
                            if (operation != valve[self.constants.VALVE_OP_VARIABLE]) | (prev_time != time):
                                json, operation = self.getValveInfo(valve, time)
                                prev_time = time
                                cargoValves.append(json)
                            else:
                                valves_code = valve[self.constants.VALVE] if len(valve[self.constants.VALVE]) > 0 else \
                                valve[self.constants.PUMP]
                                cargoValves[-1][self.constants.VALVES_JSON].append(valves_code)
                self.json[self.constants.EVENTS][c][self.constants.SEQUENCE][stage][field] = cargoValves