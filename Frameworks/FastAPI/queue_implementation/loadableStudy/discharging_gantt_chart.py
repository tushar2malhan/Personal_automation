import pandas as pd
import numpy as np
import json
from datetime import datetime

PORT_WING_TANKS = 'P'
STBD_WING_TANKS = 'S'


def getCargoTankSet(tank):
    if tank.endswith(PORT_WING_TANKS):
        return [tank, tank[:-1] + STBD_WING_TANKS]
    elif tank.endswith(STBD_WING_TANKS):
        return [tank[:-1] + PORT_WING_TANKS, tank]
    else:
        return [tank]


# self = DischargingOperations, data = Process_input
# vesseL_json : data.vessel_json, discharging_info : self.discharging.info, vessel_info: self.vessel.info,
# input_json : data.discharging_information
def gantt_chart_input_parameters(vessel_json, discharging_info, vessel_info, input_json):
    vessel_tanks = {i['id']: i['shortName'] for i in vessel_json["vesselTanks"]}

    tank_condition = discharging_info['cargo_plans']

    # BASIC INFO
    cargo_full_capacity = {i['shortName']: i['fullCapcityCubm'] for i in vessel_json["vesselTanks"] if
                           'fullCapcityCubm' in i}

    cargo_30_capacity = {i['shortName']: 0.3 * float(i['fullCapcityCubm']) for i in vessel_json["vesselTanks"] if
                         'fullCapcityCubm' in i}

    CARGO_TANK = sorted([i['shortName'] for i in vessel_json["vesselTanks"] if i["categoryId"] == 1])

    SLOP_TANK = sorted([i['shortName'] for i in vessel_json["vesselTanks"] if i["slopTank"]])

    strip_vol = vessel_info['sounding30cmVol']

    sounding2m = vessel_info['sounding2mVol']

    port = input_json['portId']
    voyage = input_json['voyageId']

    dischargeStudy = input_json["dischargeStudy"]
    dischargeStudyPortRotation = [i for i in dischargeStudy["dischargeStudyPortRotation"] if i['portId'] == port][0]

    # ds cargo nomination to cargo id
    dscargoNominationMapping = {i["id"]: i["cargoId"] for i in dischargeStudy["cargoNomination"]}
    # cargo nomination to cargo id
    cargoNominationMapping = {i["cargoNominationId"]: dscargoNominationMapping[i["dscargoNominationId"]] for i in
                              dischargeStudy["cargoNominationOperationDetails"]}
    # ds cargo nomination to cargo nomination
    dscargoToCargoNomination = {
        i["dscargoNominationId"]: i["cargoNominationId"] if pd.notna(i["cargoNominationId"]) else 0 for i in
        dischargeStudy["cargoNominationOperationDetails"]}
    # option for cow in port
    canCOW = dischargeStudyPortRotation['cow']

    # cargo details
    cargoDetails = {}
    for c in dischargeStudy["cargoNomination"]:
        cargo_id = 'P' + str(dscargoToCargoNomination[c['id']])
        cargoDetails[cargo_id] = {}
        cargoDetails[cargo_id]["cargoId"] = c["cargoId"]
        cargoDetails[cargo_id]["abbv"] = c["abbreviation"]
        cargoDetails[cargo_id]["api"] = c["api"]
        cargoDetails[cargo_id]["temperature"] = c["temperature"]
        cargoDetails[cargo_id]["isCondensateCargo"] = False if not c["isCondensateCargo"] else c["isCondensateCargo"]
        cargoDetails[cargo_id]["isHrvpCargo"] = False if not c["isHrvpCargo"] else c["isHrvpCargo"]
        cargoDetails[cargo_id]["isCommingled"] = False if not c["isCommingled"] else c["isCommingled"]
        if 'isUsedForCOW' in c:
            cargoDetails[cargo_id]["isUsedForCOW"] = False if not c["isUsedForCow"] else c["isUsedForCow"]
        else:
            cargoDetails[cargo_id]["isUsedForCOW"] = not cargoDetails[cargo_id]["isCondensateCargo"]

        if c['isCommingled']:
            commingled_details = dischargeStudy["loadablePlanPortWiseDetails"]["loadableQuantityCommingleCargoDetails"]
            for com in commingled_details:
                if c["abbreviation"] == com["abbreviation"]:
                    cargoDetails[cargo_id]['commingledCargoes'] = [com["cargo1NominationId"],
                                                                   com["cargo2NominationId"]]

    dischargeInformation = input_json["dischargeInformation"]

    # gantt chart interval and stages
    ganttChartStages = dischargeInformation["dischargeStages"]['stageOffset']
    ganttChartHrs = dischargeInformation["dischargeStages"]['stageDuration']
    ganttChartInterval = {'indicator': 'duration', 'value': ganttChartHrs}
    if 'isStageOffsetUsed' in dischargeInformation["dischargeStages"]:
        if dischargeInformation["dischargeStages"]['isStageOffsetUsed']:
            ganttChartInterval = {'indicator': 'stages', 'value': ganttChartStages}

    cowType = dischargeInformation["cowPlan"]["cowOptionType"]
    cowPercentage = dischargeInformation["cowPlan"]["cowPercentage"]

    # cow history
    pastCowHistory = []
    currentVoyageCOWedTanks = []
    for h in dischargeInformation["cowPlan"]["cowHistories"]:
        tank = getCargoTankSet(vessel_tanks[h["tankId"]])
        date = datetime.strptime(h["voyageEndDate"], '%Y-%m-%dT%H:%M')
        if h["voyageId"] == voyage:
            currentHistory = {"date": h["voyageEndDate"], "tank": tank}
            currentVoyageCOWedTanks.append(currentHistory)
        else:
            newHistory = {"date": h["voyageEndDate"], "tank": tank}
            pastCowHistory.append(newHistory)
    pastCowHistory = sorted(pastCowHistory, key=lambda x: x['date'])

    # manual cow
    manualCOW = {}
    washing_cargo = True
    if cowType == 'MANUAL':
        for t in dischargeInformation["cowPlan"]["topCowTankIds"]:
            tank = vessel_tanks[t]
            manualCOW[tank] = {'cowType': 'Top', 'washingCargo': ''}
        for t in dischargeInformation["cowPlan"]["bottomCowTankIds"]:
            tank = vessel_tanks[t]
            manualCOW[tank] = {'cowType': 'Bottom', 'washingCargo': ''}
        for t in dischargeInformation["cowPlan"]["allCowTankIds"]:
            tank = vessel_tanks[t]
            manualCOW[tank] = {'cowType': 'Full', 'washingCargo': ''}

        if 'cargoCowTankIds' in dischargeInformation["cowPlan"]:
            for item in dischargeInformation["cowPlan"]["cargoCowTankIds"]:
                washingCargo = 'P' + str(dscargoToCargoNomination[item["washingCargoNominationId"]])
                originalCargo = 'P' + str(dscargoToCargoNomination[item["cargoNominationId"]])
                for t in item['tankIds']:
                    tank = vessel_tanks[t]
                    manualCOW[tank]['cargo'] = originalCargo
                    manualCOW[tank]['washingCargo'] = washingCargo
        else:
            washing_cargo = False
    # cow duration
    vesselCOWParameters = vessel_json['vesselCowParameters'][0]
    cowDuration = {'top': float(vesselCOWParameters["topCowMaxDuration"]),
                   'bottom': float(vesselCOWParameters["bottomCowMaxDuration"]),
                   'full': float(vesselCOWParameters["fullCowMaxDuration"])}

    planPortWise = [i for i in input_json["planPortWiseDetails"] if i["portId"] == port][0]

    # dishcarge stuudy planned cow tanks
    try:
        dischargeStudyPlannedCOWTanks = planPortWise['cowTanks']
    except:
        dischargeStudyPlannedCOWTanks = []

    # load on top discharge
    try:
        loadOnTopTanks = [i['tankId'] for i in planPortWise["arrivalCondition"]["dischargePlanStowageDetails"] if
                          i["isLoadOnTop"]]
        loadOnTopTanksDeparture = [vessel_tanks[i['tankId']] for i in planPortWise["departureCondition"][
            'dischargePlanStowageDetails'] if (i['tankId'] in loadOnTopTanks) & pd.notna(i['quantityMT'])]
        loadOnTopSlopTanks = [i for i in loadOnTopTanksDeparture if vessel_tanks[i] in SLOP_TANK]
    except:
        loadOnTopSlopTanks = []

    # driveOilTankLimit
    try:
        reuseCargo = dischargeInformation["berthDetails"]["selectedBerths"][0]["reuseCargoforCOW"]
    except:
        reuseCargo = False

    driveOilTankLimit = reuseCargo

    # sunset, sunrise, start time
    startdate = dischargeInformation["dischargeDetails"]["commonDate"]
    sunset = dischargeInformation["dischargeDetails"]["timeOfSunset"]
    sunrise = dischargeInformation["dischargeDetails"]["timeOfSunrise"]
    startTime = dischargeInformation["dischargeDetails"]["startTime"]

    # option for day light
    dayLightCOW = dischargeInformation["berthDetails"]["selectedBerths"][0]["enableDayLightRestriction"]

    # fresh oil
    try:
        haveFreshOil = dischargeInformation["berthDetails"]["selectedBerths"][0]["needFlushingOilAndCrudeStorage"]
    except:
        haveFreshOil = False

    freshOilAmt = dischargeInformation["berthDetails"]["selectedBerths"][0]["freshCrudeOilQuantity"]

    # airpurge
    try:
        airPurge = dischargeInformation["berthDetails"]["selectedBerths"][0]["airPurge"]
    except:
        airPurge = False

    # heavy weather tank
    heavyWeatherTank = []
    for i in vessel_json["vesselTanks"]:
        if "isHwBallastTank" in i:
            if i["isHwBallastTank"]:
                heavyWeatherTank.append(i['shortName'])

    # pump tank mapping
    pump_tank_mapping = {}
    for p in vessel_json["vesselPumpTankMappings"]:
        cop = p["vesselPump"]["pumpName"]
        tanks = [t["shortName"] for t in p["vesselPump"]["vesselTanks"]]
        pump_tank_mapping[cop] = tanks

    # Slop tank COP mapping
    sloptank_pump_mapping = {}
    for p in vessel_json["vesselPumpTankMappings"]:
        cop = p["vesselPump"]["pumpName"]
        for t in p["vesselPump"]["vesselTanks"]:
            sloptank_pump_mapping[t['shortName']] = cop

    # pump selected
    pumps = {}
    for i in dischargeInformation["machineryInUses"]["machinesInUses"]:
        pump_name = i["machineName"]
        if 'COP' in pump_name:
            pumps[pump_name] = i["capacity"]

    # initial, max discharge rate
    initialRate = dischargeInformation["dischargeRates"]["initialDischargingRate"]
    maxRate = dischargeInformation["dischargeRates"]["maxDischargingRate"]
    dischargeRatesSection = dischargeInformation["dischargeSequences"]["dischargeDelays"]
    try:
        maxRateStages = [float(i["dischargingRate"]) for i in dischargeRatesSection]
    except:
        maxRateStages = [float(maxRate) for i in dischargeRatesSection]
    delayStages = [float(i["duration"]) for i in dischargeRatesSection]

    # final stages duration
    dryCheckDuration = dischargeInformation["postDischargeStages"]["timeForDryCheck"]
    slopDischargeDuration = dischargeInformation["postDischargeStages"]["timeForSlopDischarging"]
    freshOilDuration = dischargeInformation["postDischargeStages"]["freshOilWashing"]
    finalStrippingDuration = dischargeInformation["postDischargeStages"]["timeForFinalStripping"]

    input_details = {
        # basic info
        "port": port,
        "voyage": voyage,
        "cargoTanks": CARGO_TANK,
        "slopTanks": SLOP_TANK,
        "cargoDetails": cargoDetails,
        # discharging stages
        "ganttChartIntermediateInterval": ganttChartInterval,

        # discharging sequence
        "tankCondition": tank_condition,
        "30cmSounding": strip_vol,
        "2mSounding": sounding2m,
        "cargoTankCapacity": cargo_full_capacity,
        "cargoTank30Capacity": cargo_30_capacity,

        # COW
        "canCOWAtPort": canCOW,
        "pastVoyageCOWHistory": pastCowHistory,
        "currentVoyageCOWHistory": currentVoyageCOWedTanks,
        "cowType": cowType,  # auto/manual
        "cowPercentage": cowPercentage,
        "dayLightCOW": dayLightCOW,
        "manualCOW": manualCOW,  # check for manual cow cargo
        "heavyWeatherTank": heavyWeatherTank,
        "cowDuration": cowDuration,
        "driveOilTankCOWLimit": driveOilTankLimit,
        "dischargeStudyCOW": dischargeStudyPlannedCOWTanks,
        "washingCargo" : washing_cargo,
        # timing
        "startDate": startdate,
        "sunset": sunset,
        "sunrise": sunrise,
        "startTime": startTime,

        # fresh oil
        "haveFreshOil": haveFreshOil,
        "freshOilAmt": freshOilAmt,

        # load on top slop tanks to be discharged
        'loadOnTopTanksDischarge': loadOnTopSlopTanks,

        # air purge
        "airPurge": airPurge,

        # volume calculation
        "pumpTankMapping": pump_tank_mapping,
        "slopTankPumpMapping": sloptank_pump_mapping,
        "pumpsSelected": pumps,
        "initialRate": initialRate,
        "maxRate": maxRateStages,
        "delays": delayStages,

        # finalStages
        "dryCheckDuration": dryCheckDuration,
        "slopDischargeDuration": slopDischargeDuration,
        "freshOilDuration": freshOilDuration,
        "finalStrippingDuration": finalStrippingDuration,
    }

    return input_details


# get tanks to cow
def getAbsentTankSet(currentTanks, cargo_tanks):
    absentTanks = []
    for i in cargo_tanks:
        tanks = getCargoTankSet(i)
        if (tanks not in currentTanks) & (tanks not in absentTanks):
            absentTanks.append(tanks)
    return absentTanks


def getOrderedTankSetInCOWHistory(cow_history):
    tankList = []
    for i in range(len(cow_history)):
        tanks = cow_history[i]['tank']
        if tanks not in tankList:
            tankList.append(tanks)
    return tankList


def getVoyageCOWTankList(past_cow_history, requiredTankCount, heavyWeatherTank, cargo_tanks):
    tankList = getOrderedTankSetInCOWHistory(past_cow_history)
    tankList = heavyWeatherTank + tankList
    # take earliest tanks in history
    if len(tankList) > requiredTankCount:
        tankList = tankList[:requiredTankCount]

    # not enough tanks in history
    elif len(tankList) < requiredTankCount:
        diff = requiredTankCount - len(tankList)
        absentTank = getAbsentTankSet(tankList, cargo_tanks)
        extraTanks = absentTank[:diff]
        tankList += extraTanks
    return tankList


def calcCOWTankCount(percent, cargo_tanks):
    result = int(np.ceil((percent / 100) * len(cargo_tanks)))
    return result

def flatten(nested_list, container):
    for item in nested_list:
        if isinstance(item, list):
            flatten(item, container)
        else:
            container.append(item)
    return container        

def getTanksToCOW(input_details):
    tankList = []
    if not input_details['canCOWAtPort']:
        return []
    elif len(input_details['manualCOW'])>0:
        for tank in input_details['manualCOW'].keys():
            tankList.append(tank)
    else:        
        cargo_tanks = input_details["cargoTanks"]
        # Get all tanks that need to be washed in current voyage
        past_cow_history = input_details['pastVoyageCOWHistory']
        requiredTankCount = calcCOWTankCount(input_details['cowPercentage'], cargo_tanks)
        heavyWeatherTank = input_details['heavyWeatherTank']
        voyageCOWTanks = getVoyageCOWTankList(past_cow_history, requiredTankCount, heavyWeatherTank, cargo_tanks)

        # Get all tanks that need to be washed in current port
        current_cow_history = input_details['currentVoyageCOWHistory']
        if len(current_cow_history) > 0:
            excludeTankList = getOrderedTankSetInCOWHistory(current_cow_history)
            tankList = [i for i in voyageCOWTanks if i not in excludeTankList]
            tankList = sorted(sum(tankList, []))
        elif input_details['cowPercentage'] !=None:
            tank_to_cow = voyageCOWTanks
            tankList = flatten(tank_to_cow, tankList)
        else:
            tankList = input_details["dischargeStudyCOW"]
    return tankList


# get compatible cargo
def getAutoCargoCompatibilityForCOW(input_details):
    # cargo in tank vs cow cargo
    all_cargoes = input_details['cargoDetails'].keys()
    compatiblity = {c: [] for c in all_cargoes}
    for cargo in all_cargoes:
        cargo_details = input_details['cargoDetails'][cargo]
        for cow_cargo in all_cargoes:
            cow_cargo_details = input_details['cargoDetails'][cow_cargo]
            isHighVapour = cow_cargo_details['isHrvpCargo']
            isCondensate = cow_cargo_details['isCondensateCargo']
            if 'isUsedForCOW' in cow_cargo_details:
                isUsedForCOW = cow_cargo_details['isUsedForCOW']
            else:
                isUsedForCOW = True
            # higher_api = cow_cargo_details['api'] >= cargo_details['api']
            if (not isHighVapour) & (not isCondensate) & isUsedForCOW:
                compatiblity[cargo].append(cow_cargo)
    return compatiblity


def getManualCargoCompatibilityForCOW(input_details):
    ERROR = []
    manual_cow = input_details['manualCOW']
    all_cargoes = input_details['cargoDetails'].keys()
    compatiblity = {c: [] for c in all_cargoes}
    for tank, item in manual_cow.items():
        cargo = item['cargo']
        cow_cargo = item['washingCargo']
        cow_cargo_details = input_details['cargoDetails'][cow_cargo]
        isHighVapour = cow_cargo_details['isHrvpCargo']
        isCondensate = cow_cargo_details['isCondensateCargo']
        if (not isHighVapour) & (not isCondensate):
            if cow_cargo not in compatiblity[cargo]:
                compatiblity[cargo].append(cow_cargo)
        else:
            cow_cargo_error = [f'COW cargo {cow_cargo_details["abbv"]} is unsuitable for COW']
            ERROR.append(cow_cargo_error)

    return compatiblity, ERROR


def extract_all_gantt_chart_parameters(vessel_json, discharging_info, vessel_info, input_json):
    ERROR = []
    input_details = gantt_chart_input_parameters(vessel_json, discharging_info, vessel_info, input_json)
    all_cargoes = input_details['cargoDetails'].keys()
    cow_type = input_details["cowType"]
    cow_cargo_manual = input_details['washingCargo']
    if cow_type == 'AUTO' or cow_cargo_manual == False:
        compatiblity = getAutoCargoCompatibilityForCOW(input_details)
    else:
        compatiblity, ERROR = getManualCargoCompatibilityForCOW(input_details)

    input_details['cargo_compatibility'] = compatiblity

    tanks_to_cow_at_port = getTanksToCOW(input_details)

    input_details['tanks_to_cow_at_port'] = tanks_to_cow_at_port
    return input_details, ERROR
