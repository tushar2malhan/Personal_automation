import numpy as np
import json
import pandas as pd
import copy


class Generate_valves:
    def __init__(self, input_param, output, raw_output):
        print('')
        print('GENERATE VALVES')
        # Vessel Details
        self.vesselId = input_param.vessel_id
        with open('valves_config.json') as f_:
            self.valve_config = json.load(f_)
        self.vesselDetails = self.valve_config["vessel"][str(input_param.vessel_id)]

        # Operation
        self.module = input_param.module
        self.stages = list(self.valve_config[self.module.lower()].keys())
        self.cargo = input_param.loading.info['loading_order']
        self.cargoTanksUsed = input_param.loading.info['cargoTanksUsed']
        self.ballastTanksUsed = input_param.loading.info['ballastTanksUsed']  #### to check
        # self.BWTS = False  # False for all MOL VLCC, need to update for other vessel
        # self.firstport = input_param.first_loading_port
        self.gravityAllowed = {c: False for c in self.cargo}  # update based on output
        # self.gravityAllowed = {c: (not self.BWTS) & (self.firstport) & (c == self.cargo[0]) for c in self.cargo}

        # Cargo
        # Machinery/Processes
        self.manifold = sum(
            [self.vesselDetails["manifold"][str(i)] for i in input_param.loading.load_param['Manifolds']], [])
        self.manifoldSide = [i['tankTypeName'] for i in input_param.loading_info_json['loadingMachinesInUses'] if i['machineTypeName'] == 'MANIFOLD'][0].lower()
        self.bottomLines = sum(
            [self.vesselDetails["bottomLines"][str(i)] for i in input_param.loading.load_param['BottomLines']], [])
        self.cargoPumps = []
        ##Tanks
        preloaded = input_param.loading.preloaded_cargos
        self.tanks = {cargo: input_param.loading.info['cargo_tank'][cargo] for cargo in self.cargo if
                      cargo not in preloaded}
        self.initialTanks = {cargo: [input_param.loading.seq[cargo]['firstTank']] for cargo in
                             self.cargo}  # for loading
        self.toppingSequence = {}  ## topping sequence for loading, staggering sequence for discharging
        self.lastTank = {}  # last tank to top off
        self.tankValvesMap = {}

        # Ballast
        # Machinery/Processes
        self.ballastPumps = {'pump': [], 'eductor': []}
        self.eductionTime = float(input_param.loading.time_eduction)
        self.eductionEquipment = []
        self.eductionPumpRestriction = self.vesselDetails['pumpVesselSide'] # Pump usage restriction for eduction (1 pump only or based on port/stbd)
        self.timeSwitch = {}  # change dataframe
        ## Tanks
        self.ballastTanks = {}  # at each timing what tanks are being used change dataframe
        self.eductionTanks = {c:[] for c in self.cargo}  # Tanks to be educted
        self.ballastValvesMap = {}  # mapping of ballast tank and main valve
        allBallastPumps = {**input_param.vessel.info['vesselPumps']['ballastPump'],
                           **input_param.vessel.info['vesselPumps']['ballastEductor']}
        self.ballastPumpMap = {str(info['pumpId']): info['pumpCode'] for pump, info in allBallastPumps.items()}

        # Valve Sequence
        self.valves = input_param.vessel_json['vessel']['vesselValveSequence']

        # other data
        self.input = input_param
        self.output = copy.deepcopy(output)
        self.raw_output = raw_output

        # Processed data
        self.opened_valves = {}  ## track record of what valves are opened
        ## filtered valves and operation (for selected tanks, manifold, bottom lines) for each stage
        self.loading_valves = {}
        self.deballast_valves = {}
        self.discharging_valves = {}
        self.ballast_valves = {}
        # timeline for valves (cargo and ballast)
        self.loading_timeline = {}

    def prepOperation(self):
        """Extract and reformat data required from output to generate valves"""
        self.getToppingSequence('topping')
        self.getBallastTanks('deballasting')  # only has gravity/pump data
        self.getBallastTanks('ballasting')
        self.getDeballastTiming('loadingAtMaxRate')
        return

    def integrateValves(self):
        """Get valves sequence (cargo and ballast) and integrate into output"""
        # get valves from vessel json and put into its respective stages.
        # E.g valves for start of loading seq into open single tank stage
        self.getLoadingValves()
        self.getDeballastValves()
        # self.getDeballastTanksValves()

        # # combine ballast and cargo valves and timing for valves
        self.getLoadingValvesTimeLine()
        self.combineValves()
        return self.output

    def combineValves(self):
        """Combine valves sequence with timeline into output format"""
        for idx, cargo in enumerate(self.cargo):  # cargo in self.loading_timeline:
            cargo_idx = idx
            # cargo_idx = [idx for idx, info in enumerate(self.output["events"]) \
            #              if str(info['cargoNominationId']) == cargo[1:]][0]  # cargo nomination id no prefix P
            for stage in self.loading_timeline[cargo]:

                cargo_valves = []
                ballast_valves = []
                stage_idx = self.stages.index(stage)
                stageTimeEnd = int(self.output["events"][cargo_idx]["sequence"][stage_idx]['timeEnd'])
                for time, info in self.loading_timeline[cargo][stage].items():
                    cargoValveInfoJson = {'time': "0", 'operation': '', 'valves': [], 'stage': []}
                    ballastValveInfoJson = {'time': "0", 'operation': '', 'valves': [], 'stage': []}
                    # Cargo
                    for cvalve in info['cargo']:
                        # loop through all valves for particular time in stage
                        # separate new dictionary if operation changes
                        if cvalve['operation'] != cargoValveInfoJson['operation']:
                            if len(cargoValveInfoJson['valves']) > 0:
                                cargo_valves.append(cargoValveInfoJson.copy())
                            cargoValveInfoJson = {'time': str(time), 'operation': cvalve['operation'],
                                                    'valves': [cvalve['valve']], 'stage': [cvalve['stageNo']]}
                        else:
                            cargoValveInfoJson['valves'].append(cvalve['valve'])
                            cargoValveInfoJson['stage'].append(cvalve['stageNo'])

                    # Ballast
                    for bvalve in info['ballast']:
                        # loop through all valves for particular time in stage
                        # separate new dictionary if operation changes
                        if ballastValveInfoJson['operation'] != bvalve['operation']:
                            if len(ballastValveInfoJson['valves']) > 0:
                                ballast_valves.append(ballastValveInfoJson.copy())
                            ballastValveInfoJson = {'time': str(time), 'operation': bvalve['operation'],
                                                    'valves': [bvalve['valve']], 'stage': [bvalve['stageNo']]}

                        else:
                            ballastValveInfoJson['valves'].append(bvalve['valve'])
                            ballastValveInfoJson['stage'].append(bvalve['stageNo'])

                    # Last valve
                    if (cargoValveInfoJson not in cargo_valves) & (len(cargoValveInfoJson['valves']) > 0):
                        cargo_valves.append(cargoValveInfoJson.copy())
                    if (ballastValveInfoJson not in ballast_valves) & (len(ballastValveInfoJson['valves']) > 0):
                        ballast_valves.append(ballastValveInfoJson.copy())

                self.output["events"][cargo_idx]["sequence"][stage_idx]['cargoValves'] = cargo_valves
                self.output["events"][cargo_idx]["sequence"][stage_idx]['ballastValves'] = ballast_valves
        return

    # TODO: pipelines info (generalise for single segregation)
    def getLoadingValves(self):
        """Get cargo loading valves from the given valves sequence and classify it into the
            different stages in loading"""
        final_valves = {}
        # Loop through all cargoes
        for cargo in self.tanks:
            cargo_valves = {}
            # Loop through each stage in loading process and get required valve process
            for stage, info in self.valve_config['loading'].items():
                stage_valves = {}
                if len(info) == 0:  # no valve process
                    cargo_valves[stage] = stage_valves
                else:
                    for i in info:  # loop through all valve processes
                        # # Check if current stage is topping
                        # isTopping = '_' in i ## topping stage represented by shuttingSequence_5
                        # if isTopping:
                        #     seqno = i.split('_')[-1] # only sequence 5
                        #     raw_valves = self.valves['loading'][i.split('_')[0]]
                        # else:
                        #     seqno = '0'
                        #     raw_valves = self.valves['loading'][i]
                        # For each step in valve process, get required valve info
                        allsteps = []
                        raw_valves = self.valves['loading'][i]
                        for step in raw_valves:
                            if ('0' not in step):
                                valveType = raw_valves[step][0]['valveTypeName']  ## check type of valve
                                # get valves for each type of valves in sequence
                                if 'MANIFOLD' in valveType:
                                    name = 'manifoldValves'
                                    valves = self.getManifoldValves(raw_valves[step], name)
                                    # self.updateValveStatus(valves, name)
                                    allsteps += valves
                                elif 'CARGO PIPE LINE VALVES' == valveType:
                                    name = 'tankValves'
                                    tanks = self.getCargoTanksForStage(stage, cargo)
                                    valves = self.getTankValves(tanks, raw_valves[step],
                                                                'CARGO PIPE LINE VALVES', name)
                                    self.updateValveStatus(valves, name)
                                    if len(valves) > 0:
                                        allsteps += valves
                                    for valve in valves:
                                        if valve['tank'] not in self.tankValvesMap:
                                            self.tankValvesMap[valve['tank']] = valve
                                else:
                                    name = self.nameTankValve(valveType)
                                    valves = self.getOtherValves(raw_valves[step], name)
                                    # self.updateValveStatus(valves, name)
                                    allsteps += valves
                        stage_valves[i] = allsteps
                    cargo_valves[stage] = stage_valves
            final_valves[cargo] = cargo_valves
        self.loading_valves = final_valves

        return

    def getDeballastValves(self):
        """Get deballast loading valves from the given valves sequence and classify it into the
            different stages in loading"""
        final_valves = {}
        # Loop through all cargoes
        for cargo in self.cargo:
            ballast_valves = {}
            # Get correct valves based on loading plan

            deballast_config = {}
            isGravity = 'gravity' if self.gravityAllowed[cargo] else 'nogravity' # 1) with gravity or not
            excludeEductor = ['seaTosea', 'strippingByEductor'] if (len(self.eductionTanks[cargo]) == 0) else [] # 2) with eduction or not
            for process, item in self.valve_config['deballasting'][isGravity].items():
                if process not in excludeEductor:
                    deballast_config[process] = item

            # Loop through each stage in loading process and get required valve process
            for stage, info in deballast_config.items():
                stage_valves = {}
                if len(info) == 0:  # no valve process
                    ballast_valves[stage] = stage_valves
                else:
                    for i in info:  # loop through all valve processes
                        # For each step in valve process, get required valve info
                        raw_valves = self.valves['deballast'][i]
                        allsteps = []
                        for step in raw_valves:
                            if ('0' not in step):  # not sequence 0
                                valveType = raw_valves[step][0]['valveTypeName']  # Check type of valve
                                pumpType = raw_valves[step][0]['pumpType']
                                # get valves for each type of valves in sequence
                                if (valveType == '') & (pumpType == 'Ballast Pump'):  # Ballast Pumps
                                    name = 'ballastPumps'
                                    valves = self.getBallastPumps(raw_valves[step], name)
                                    # self.updateValveStatus(valves, name)
                                    allsteps += valves

                                elif valveType.startswith('EDUCTOR'):  # Eductor related valves
                                    name = self.nameTankValve(valveType)
                                    valves = self.getBallastEductorValves(raw_valves[step], name)
                                    # self.updateValveStatus(valves, name)
                                    allsteps += valves

                                elif valveType.startswith('STRIPPER SUCTION'):  # Tank stripping valve
                                    name = self.nameTankValve(valveType)
                                    valves = self.getTankValves(self.eductionTanks[cargo], raw_valves[step],
                                                                'STRIPPER SUCTION VALVE', name)
                                    # self.updateValveStatus(valves, name)
                                    allsteps += valves

                                elif 'BALLLAST VALVES' == valveType:  # Main Tank Valves
                                    name = 'tankValves'
                                    tanks = list(self.input.loadable['ballastOperation'].keys())
                                    valves = self.getTankValves(tanks, raw_valves[step], 'BALLLAST VALVES', name)
                                    # self.updateValveStatus(valves, name)
                                    for valve in valves:
                                        if valve['tank'] not in self.ballastValvesMap:
                                            self.ballastValvesMap[valve['tank']] = valve

                                else:  # Others
                                    name = self.nameTankValve(valveType)
                                    valves = self.getOtherValves(raw_valves[step], name)
                                    # self.updateValveStatus(valves, name)
                                    allsteps += valves
                        stage_valves[i] = allsteps
                    ballast_valves[stage] = stage_valves
            final_valves[cargo] = ballast_valves
        self.deballast_valves = final_valves

        # Additional pump closing before eduction if more than 1 ballast pump used
        pumpCount = len([i for i in self.ballastPumps['pump'] if i != 'Gravity'])
        ballastPump = ''
        if self.eductionPumpRestriction['useOnePump']:  # Only use 1 ballast pump for eduction
            if (pumpCount >= 2) & (len(self.eductionTanks[cargo]) > 0):  # Assumption close 2nd pumps if theres 2 pumps
                ballastPumps = [i for i in self.ballastPumps['pump'] if
                                (i not in self.eductionEquipment) & (i != 'Gravity')]
                if len(ballastPumps) == 0:
                    ballastPump = self.ballastPumps['pump'][-1]
                else:
                    ballastPump = ballastPumps[0]
        else:  # select ballast pump based on port/stbd
            portTanks = [i for i in self.eductionTanks[cargo] if i.endswith('P')]
            if len(portTanks) == 0:
                ballastPump = self.eductionPumpRestriction['port']
            stbdTanks = [i for i in self.eductionTanks[cargo] if i.endswith('S')]
            if len(stbdTanks) == 0:
                ballastPump = self.eductionPumpRestriction['stbd']


            # Get valve details of pump
            if len(ballastPump) > 0:
                closePump = self.ballastValvesMap[ballastPump].copy()
                closePump['operation'] = 'close'
                self.deballast_valves[cargo]['loadingAtMaxRate']['strippingByEductor'] = [closePump] + \
                                                                                         self.deballast_valves[cargo][
                                                                                             'loadingAtMaxRate'][
                                                                                             'strippingByEductor']
                # for subsequent valve closing, do not close particular pump again, remove that pump
                pumpIdx = -1
                for idx, valves in enumerate(self.deballast_valves[cargo]['loadingAtMaxRate']['shuttingSequence']):
                    if (valves['category'] == 'ballastPumps') & (valves['valve'] == ballastPump):
                        pumpIdx = idx
                if pumpIdx != -1:
                    self.deballast_valves[cargo]['loadingAtMaxRate']['shuttingSequence'].pop(pumpIdx)
        return

    def getLoadingValvesTimeLine(self):
        """Format cargo and ballast valve according to time to open each valve"""
        # cargo: only topping have variable timeline for valves
        # ballast: max rate: by pump only if theres gravity, change to eductor/seatosea (2hrs), shut down/sea to sea at the end
        result = {}
        # Loop through all cargo in current loading plan
        for c in self.output['events']:
            cargo = 'P' + str(c['cargoNominationId'])
            result[cargo] = {}
            # Loop through all stages for each cargo
            for s in c['sequence']:
                # Get information of stage
                stage = s['stage']
                time = int(s['timeStart'])
                timeEnd = int(s['timeEnd'])
                stage_timeline = {}

                # Process valve timing for each stage
                if stage == 'loadingAtMaxRate':
                    pump = self.ballastPumps['pump'][-1]  # get one of the pump, assume pump same time if > 1
                    pumpTime = int(self.timeSwitch[cargo][pump]['start'])
                    stage_timeline[pumpTime] = {'cargo': [], 'ballast': []}
                    if (len(self.eductionTanks[cargo]) > 0) & (cargo == self.cargo[-1]):
                        eductorTime = int(self.timeSwitch[cargo]['eduction']['start'])
                        stage_timeline[eductorTime] = {'cargo': [], 'ballast': []}
                        shutTime = int(self.timeSwitch[cargo]['eduction']['end'])
                        stage_timeline[shutTime] = {'cargo': [], 'ballast': []}
                    else:
                        shutTime = int(self.timeSwitch[cargo][pump]['end'])
                        stage_timeline[shutTime] = {'cargo': [], 'ballast': []}

                    # Ballast Gravity -> Pump: valve sequence for change over (after 2h/4 if <10k)
                    if self.gravityAllowed[cargo]:  # no BWTS and is first loading port: gravity
                        stage_timeline[pumpTime]['ballast'] += self.deballast_valves[cargo][stage][
                            'floodingTheBallastPump']
                        stage_timeline[pumpTime]['ballast'] += self.deballast_valves[cargo][stage][
                            'debalastingByPumpAfterGravity']
                    else:  # no gravity
                        pass

                    # Ballast Pump -> Eductor: Eductor and Sea to Sea sequence 3hours before stage end
                    # Ballast Shutting: shutting sequence 1hr before stage end
                    if (len(self.eductionTanks[cargo]) > 0) & (cargo == self.cargo[-1]):
                        stage_timeline[eductorTime]['ballast'] += self.deballast_valves[cargo][stage]['seaToSea']
                        stage_timeline[eductorTime]['ballast'] += self.deballast_valves[cargo][stage][
                            'strippingByEductor']
                        stage_timeline[shutTime]['ballast'] += self.deballast_valves[cargo][stage]['seaTosea']
                        stage_timeline[shutTime]['ballast'] += self.deballast_valves[cargo][stage]['shuttingSequence']
                    else:
                        stage_timeline[shutTime]['ballast'] += self.deballast_valves[cargo][stage]['seaToSea']
                        stage_timeline[shutTime]['ballast'] += self.deballast_valves[cargo][stage]['shuttingSequence']

                elif stage == 'topping':
                    # Cargo Shutting: shutting sequence and close final tank in topping sequence
                    toppingSeq = self.toppingSequence[cargo]
                    for process, valves in self.loading_valves[cargo][stage].items():
                        for valve in valves:
                            # Other valves
                            if 'tankValves' == valve['category']:
                                continue
                            if timeEnd not in stage_timeline:
                                stage_timeline[timeEnd] = {'cargo': [], 'ballast': []}
                            stage_timeline[timeEnd]['cargo'] += [valve]

                    # Cargo Topping: close valves for topping sequence
                    for info in self.toppingSequence[cargo]:
                        tank = info['tank']
                        time = info['time']
                        cargoTankValves = {k: v for k, v in self.tankValvesMap[tank].items() if
                                           k != 'operation'}
                        cargoTankValves['operation'] = 'close'
                        if time not in stage_timeline:
                            stage_timeline[time] = {'cargo': [], 'ballast': []}
                        stage_timeline[time]['cargo'] += [cargoTankValves]

                else:
                    # Other stages: empty stages with no valve action
                    # Other stages where valve action occurs at the start of the stage
                    if time not in stage_timeline:
                        stage_timeline[time] = {'cargo': [], 'ballast': []}
                    for process, valves in self.loading_valves[cargo][stage].items():
                        stage_timeline[time]['cargo'] += valves
                    for process, valves in self.deballast_valves[cargo][stage].items():
                        stage_timeline[time]['ballast'] += valves

                # Process opening and closing of ballast tanks
                if stage in self.ballastTanks[cargo]['deballasting']:
                    for time, actions in self.ballastTanks[cargo]['deballasting'][stage].items():
                        valves_arr = []
                        for tank in actions['open']:
                            if tank in self.ballastValvesMap:  # Check for ballast tanks not in ballast system
                                ballastTankValves = {k: v for k, v in self.ballastValvesMap[tank].items() if
                                                     k != 'operation'}
                                ballastTankValves['operation'] = 'open'
                                valves_arr += [ballastTankValves]
                        for tank in actions['close']:
                            if tank in self.ballastValvesMap:
                                ballastTankValves = {k: v for k, v in self.ballastValvesMap[tank].items() if
                                                     k != 'operation'}
                                ballastTankValves['operation'] = 'close'
                                valves_arr += [ballastTankValves]
                        if time not in stage_timeline:
                            stage_timeline[time] = {'cargo': [], 'ballast': []}
                        if len(valves_arr) > 0:
                            stage_timeline[time]['ballast'] += valves_arr

                if stage in self.ballastTanks[cargo]['ballasting']:
                    for time, actions in self.ballastTanks[cargo]['ballasting'][stage].items():
                        valves_arr = []
                        for tank in actions['open']:
                            if tank in self.ballastValvesMap:
                                ballastTankValves = {k: v for k, v in self.ballastValvesMap[tank].items() if
                                                     k != 'operation'}
                                ballastTankValves['operation'] = 'open'
                                valves_arr += [ballastTankValves]
                        for tank in actions['close']:
                            if tank in self.ballastValvesMap:
                                ballastTankValves = {k: v for k, v in self.ballastValvesMap[tank].items() if
                                                     k != 'operation'}
                                ballastTankValves['operation'] = 'close'
                                valves_arr += [ballastTankValves]
                        if time not in stage_timeline:
                            stage_timeline[time] = {'cargo': [], 'ballast': []}
                        if len(valves_arr) > 0:
                            stage_timeline[time]['ballast'] += valves_arr

                stage_timeline = {k: stage_timeline[k] for k in sorted(stage_timeline)}
                result[cargo][stage] = stage_timeline
        self.loading_timeline = result
        return

    def updateValveStatus(self, valves, category):
        """Update current status of valve which are opened while extracting valve action.
            To track opening and closing of valves to identify errors"""
        if category not in self.opened_valves:
            self.opened_valves[category] = []
        # Loop through sequence of valves
        for valve in valves:
            operation = valve['operation']
            valveName = valve['valve']
            # If valve is to be opened
            if operation == 'open':
                # Check if valve is already opened, cannot open an opened valve
                if valveName in self.opened_valves[category]:
                    pass
                else:
                    self.opened_valves[category].append(valveName)
            # If valve is to be closed
            else:
                # Check if valve is already closed, cannot close a closed valve
                if valveName in self.opened_valves[category]:
                    self.opened_valves[category].remove(valveName)
                else:
                    pass  # cannot close valve thats already closed
        return

    def nameTankValve(self, raw_name):
        """To extract short name of valves for labelling"""
        name = ''.join([i[0].upper() + i[1:].lower() for i in raw_name.split(' ')])
        name = name[0].lower() + name[1:]
        return name

    def getCargoTanksForStage(self, stage, cargo):
        """Get tanks being used for a particular stage"""
        if stage == 'openSingleTank':
            tanks = self.initialTanks[cargo]
        elif stage == 'topping':
            tanks = []
            # tanks = [i['tank'] for i in self.toppingSequence[cargo]]
            # if topping:  # If isTopping is true, then get tanks in order except final tank
            #     tanks = [i['tank'] for i in self.toppingSequence[cargo] if i['tank'] not in self.lastTank[cargo]]
            # else:  # get final tank for shutting sequence
            #     tanks = self.lastTank[cargo]
        else:
            tanks = [tank for tank in self.tanks[cargo] if tank not in self.initialTanks[cargo]]

        newTanks = []
        for tank in tanks:
            # Separate wing tanks into individual tank to get individual tank valves
            if tank[-1] == 'W':
                newTanks.append(tank[:-1] + 'P')
                newTanks.append(tank[:-1] + 'S')
            else:
                newTanks.append(tank)
        return newTanks

    def getTankValves(self, tanks, seq, valveType,
                      name):  # E.g tanks:['1W', '1C', 'SLS'], seq: sequence0/1 from vessel json
        """Filter Tank Valves (valveTypeName: CARGO PIPE LINE VALVES) for required tanks.
            Valves for all tanks are given for all valve processes"""
        tankValves = []  # Final set of tank valves to return
        # Loop through all tank valves given and extract valves of required tank
        for valve in seq:
            if valve['valveTypeName'] == valveType:
                valveName = valve['valveNumber']
                valveOpen = 'close' if valve['shut'] else 'open'  # C for Close, O for Open
                tankName = valve['tankShortName']
                if tankName in tanks:
                    value = {'valve': valveName, 'tank': tankName, 'operation': valveOpen,
                             'stageNo': valve['stageNumber'], 'category': name}
                    if name in self.opened_valves:
                        # Cannot reopen tank valves (for singleTank stage where there are 2 tank opening sequence)
                        if (valveOpen == 'open') & (valveName in self.opened_valves[name]):
                            pass
                        else:
                            tankValves += [value]
                    else:
                        tankValves += [value]
        tankValves = sorted(tankValves, key=lambda x: tanks.index(x['tank']))
        return tankValves

    def getManifoldValves(self, seq, name):  # E.g lines:[1,2,3], side = port/stbd, seq: sequence0/1 from vessel json
        """Filter Manifold valves for required manifold.
                    Valves for all manifold are given for all valve processes"""
        lines = self.manifold
        side = self.manifoldSide
        manifoldValves = []
        for valve in seq:
            # identify corect valves
            valveline = int(valve['pipelineName'][-1])
            valveTypeName = valve['valveTypeName'].lower()  # MANIFOLD GATE VALVE PORT SIDE
            if 'manifold' in valveTypeName:
                # valve info
                valveName = valve['valveNumber']
                valveOpen = 'close' if valve['shut'] else 'open'
                valveLine = valve['pipelineName']
                if (side.lower() in valveTypeName) & (valveName in lines):
                    value = {'valve': valveName, 'line': valveLine, 'operation': valveOpen,
                             'stageNo': valve['stageNumber'], 'category': name}
                    manifoldValves.append(value)
        return manifoldValves

    def getOtherValves(self, seq, name):
        """Filter all the types of valves for required info. """
        preferValves = self.vesselDetails['preferredValves']['name'] if name in self.vesselDetails['preferredValves'] else []
        valves = []
        for valve in seq:
            valveOpen = 'close' if valve['shut'] else 'open'
            valveName = valve['valveNumber']
            valveLine = valve['pipelineName']
            value = {'valve': valveName, 'line': valveLine, 'operation': valveOpen, 'stageNo': valve['stageNumber'],
                     'category': name}
            if len(preferValves) > 0:  # Preference for particular valve type available
                if valveName in preferValves:
                    valves.append(value)
            else:
                valves.append(value)
        return valves

    def getBallastPumps(self, seq, name):
        valves = []
        for valve in seq:
            valveOpen = 'close' if valve['shut'] else 'open'
            valveName = valve['pumpCode']
            valveLine = valve['pumpType']
            value = {'valve': valveName, 'line': valveLine, 'operation': valveOpen, 'stageNo': valve['stageNumber'],
                     'category': name}
            if valveName in self.ballastPumps['pump']:
                valves.append(value)
                if valveName not in self.ballastValvesMap:
                    self.ballastValvesMap[valveName] = value
        return valves

    def getBallastEductorValves(self, seq, name):
        valves = []
        for valve in seq:
            valveOpen = 'close' if valve['shut'] else 'open'
            valveName = valve['valveNumber']
            valveLine = valve['pipelineName']
            value = {'valve': valveName, 'line': valveLine, 'operation': valveOpen, 'stageNo': valve['stageNumber'],
                     'category': name}
            if valveName in self.eductionEquipment:
                valves.append(value)
        return valves

    # TODO: input.loading.info-> tanksto ballast/tanksto deballast?
    def getBallastTanks(self, operation):
        """Get Ballast tanks used at each stage and time.
            Certain ballast tanks may start deballasting at a later time,
            rather than right from the start"""
        output = self.output
        result = {}
        for e in output['events']:
            cargo = 'P' + str(e['cargoNominationId'])
            ballast_time = {}  # Tanks being used for ballasting at each timestamp
            deballast_time = {}
            if cargo in self.cargo:
                if cargo not in self.ballastTanks:
                    self.ballastTanks[cargo] = {}
                prevDeballastTank = []
                startTime = -100 # initialise
                endTime = -100
                for stages in e['sequence'][1:]:  # First stage omitted, arrival condition
                    stageName = stages['stage']
                    # Tanks used for deballasting
                    if f'sim{operation.title()}RateM3_Hr' in stages:
                        deballast_time[stageName] = {}
                        prevEndTime = 0
                        for substages in stages[f'sim{operation.title()}RateM3_Hr']:
                            if len(substages) > 0:  # get timings and tank info for non empty dictionary
                                startTime = int(float(list(substages.values())[0]["timeStart"]))
                                endTime = int(float(list(substages.values())[0]["timeEnd"]))
                                deballast_time[stageName][startTime] = {'close': [], 'open': []}
                                deballast_time[stageName][endTime] = {'close': [], 'open': []}

                                tanks = [info['tankShortName'] for i, info in substages.items()]  # Current stage opened tanks

                                # Close tanks in previous stages but not in current stages
                                tanksToBeClosed = [prevTank for prevTank in prevDeballastTank if prevTank not in tanks]
                                for prevTank in tanksToBeClosed:
                                    deballast_time[stageName][prevEndTime]['close'].append(prevTank)
                                    prevDeballastTank.remove(prevTank)

                                # Open tanks not in previous stages but in current stages
                                tanksToBeOpened = [tank for tank in tanks if tank not in prevDeballastTank]
                                for tank in tanksToBeOpened:
                                    deballast_time[stageName][startTime]['open'].append(tank)
                                    prevDeballastTank.append(tank)
                                prevEndTime = endTime

                # Close last set of tanks opened at the stage
                nonEmptystageName = [i for i in deballast_time.keys() if len(deballast_time[i]) > 0]
                if (endTime > 0) & (len(nonEmptystageName) >= 1):
                    lastStageName = nonEmptystageName[-1]
                    if len(deballast_time[lastStageName][endTime]['close']) == 0:
                        deballast_time[lastStageName][endTime]['close'] = prevDeballastTank
            self.ballastTanks[cargo][operation] = deballast_time
        return

    def getToppingSequence(self, stage='topping'):
        """Get Ballast tanks used at each stage and time.
            Certain ballast tanks may start deballasting at a later time,
            rather than right from the start"""
        output = self.output
        topping = {}
        last = {}
        for e in output['events']:
            cargo = 'P' + str(e['cargoNominationId'])
            tank_endTime = []
            if cargo in self.tanks:
                for stages in e['sequence'][1:]:  # First stage omitted, arrival condition
                    if stages['stage'] == stage:  # Topping stage for loading, staggering for discharging
                        # Get end time of each tank
                        for substages in stages['simCargoLoadingRatePerTankM3_Hr']:
                            for tankId, tanks in substages.items():
                                time = int(tanks['timeEnd'])
                                tankName = tanks['tankShortName']
                                tank_endTime.append({'time': time, 'tank': tankName})

            # Sort tanks according to first to end to last
            tank_endTime = sorted(tank_endTime, key=lambda k: k['time'])
            topping[cargo] = tank_endTime
            # For center tanks, sls, slp
            if ('C' in tank_endTime[-1]['tank'][-1]) | (tank_endTime[-1]['tank'] in ['SLS', 'SLP']):
                last[cargo] = [tank_endTime[-1]['tank']]
            else:  # For wing tanks (both wing tanks)
                last[cargo] = [tank_endTime[-2]['tank'], tank_endTime[-1]['tank']]
        self.toppingSequence = topping
        self.lastTank = last
        return

    def getDeballastTiming(self, stage='loadingAtMaxRate'):

        for e in self.output['events']:
            cargo = 'P' + str(e['cargoNominationId'])
            if cargo in self.tanks:
                self.timeSwitch[cargo] = {}
                for stages in e['sequence'][1:]:  # First stage omitted, arrival condition
                    # Gravity, Pumps
                    for equipment, info in stages['ballast'].items():
                        # map pump id to pump name if available
                        if len(info) > 0:
                            pumpName = self.ballastPumpMap[str(equipment)] if str(
                                equipment) in self.ballastPumpMap else str(equipment)

                            if pumpName not in self.ballastPumps['pump']:
                                self.ballastPumps['pump'].append(pumpName)
                            if pumpName == 'Gravity':
                                self.gravityAllowed[cargo] = True
                            # if pumpName != equipment:  # save ballast pumps being used
                            #     if pumpName[0] not in self.ballastPumps['pump']:
                            #         self.ballastPumps['pump'].append(pumpName)
                            # else:  # If pump not in pump data(gravity), then use equipment name given in output
                            #     self.ballastPumps['pump'].append(pumpName)

                            # Get gravity and pump timings
                            for substage in info:
                                start = float(substage['timeStart'])
                                end = float(substage['timeEnd'])
                                if float(substage['rateM3_Hr']) > 0.001:  # if theres deballasting
                                    if pumpName not in self.timeSwitch[cargo]:
                                        self.timeSwitch[cargo][pumpName] = {}
                                    if 'start' not in self.timeSwitch[cargo][pumpName]:  # First gravity/pump operation
                                        self.timeSwitch[cargo][pumpName]['start'] = start
                                        self.timeSwitch[cargo][pumpName]['end'] = end
                                    else:  # last/subsequent gravity operation, update end time if theres a later end time
                                        prevEnd = self.timeSwitch[cargo][pumpName]['end']
                                        if prevEnd < end:
                                            self.timeSwitch[cargo][pumpName]['end'] = end

                    # Eductor
                    if len(stages['eduction']) > 0:
                        self.timeSwitch[cargo]['eduction'] = {}
                        self.timeSwitch[cargo]['eduction']['start'] = stages['eduction']['timeStart']
                        self.timeSwitch[cargo]['eduction']['end'] = stages['eduction']['timeEnd']
                        self.eductionTanks[cargo] = list(stages['eduction']['tank'].values())
                        if len(stages['eduction']['pumpSelected']) == 0:
                            self.ballastPumps['eductor'].append('Ballast Eductor 1')
                            eductorUsed = ["1"]
                        else:
                            self.ballastPumps['eductor'] += stages['eduction']['pumpSelected']
                            eductorUsed = [i['pumpName'][-1] for i in list(stages['eduction']['pumpSelected'].values())]
                        for i in eductorUsed:
                            self.eductionEquipment += self.vesselDetails["eductorValves"][i]
        return
