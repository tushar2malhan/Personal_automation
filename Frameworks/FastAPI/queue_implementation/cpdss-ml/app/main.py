"""
Created on Tues Mar 2 15:45:00 2021

@author: Shu Qi
"""
# dump data
# pg_restore --host "localhost" --port "5432" --username "postgres" --dbname "ship" --section=pre-data --section=data --section=post-data --no-owner --clean --verbose "C:\\Users\\Me\\Desktop\\ALPHA_~1\\VLCC\\ML_API\\docker\\cpdss_db.sql"
# uvicorn app.main:app --reload
#

import pickle
import os
from datetime import datetime
import numpy as np
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, pump, cargo, nomination, ballast, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


# def loadLatestPickleFiles(dir, keyword):
#     key_files = [file.replace('.pickle', '') for file in os.listdir(dir) if file.startswith(keyword)]
#     idx = np.argmax([datetime.strptime('_'.join(file.split('_')[1:]), "%Y-%m-%d_%H-%M-%S") for file in key_files])
#     key_model = pickle.load(open(dir + key_files[idx] + '.pickle', 'rb'))
#     return key_model


app = FastAPI()
# dir = './tmp/'

# ballast_model = loadLatestPickleFiles(dir, 'ballast')
# cargotanks_model = loadLatestPickleFiles(dir, 'cargotanks')


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pump Rates -
@app.post("/pumprates")
def getPumpRates(pumpinfo: schemas.PumpInfo, db: Session = Depends(get_db)):
    if len(pumpinfo.Vessel) == 0:
        raise HTTPException(status_code=404, detail="Input Error. Vessel not given.")
    else:
        portVesselDetails = crud.getVoyagesAtPort(db, port=pumpinfo.Port, vessel=pumpinfo.Vessel)
        if portVesselDetails is None:
            return None

    count = len(portVesselDetails)
    deviation = [i.deviation_rate for i in portVesselDetails if pd.notna(i.deviation_rate)]
    if len(deviation) <= 1:
        return None
    std = np.std(deviation)
    average = np.mean(deviation)

    pumpRates = pump.estimatePumpRates(count, std, average, pumpinfo.MaxRate)
    result = {'vessel': pumpinfo.Vessel, 'port': pumpinfo.Port, 'Pump Rates (KL/hrs)': pumpRates,
              'Theoretical Max(KL/hrs)': pumpinfo.MaxRate}
    return result


# # Cargo API Temp - get cargo name from cargo table then filter cargo name/date/week and average
@app.post("/cargo")
def getCargoAPITemp(cargoinfo: schemas.CargoInfo, db: Session = Depends(get_db)):
    week = cargo.cleanWeekNo(cargoinfo.Year, cargoinfo.Month, cargoinfo.Date)
    cargoid = crud.getCargoID(db, cargo=cargoinfo.Cargo)
    if cargoid is None:
        raise HTTPException(status_code=404, detail="No Such Cargo.")

    # GET API
    apiList = crud.getAPI(db, port=cargoinfo.Port, cargoid=cargoid[0])
    if len(apiList) == 0:
        raise HTTPException(status_code=404, detail="Wrong Port or Cargo Grade. No API Found.")
    _, api = cargo.avgResults(apiList)

    # GET TEMP
    tempList = crud.getTemp(db, port=cargoinfo.Port, cargoid=cargoid[0], week=week)
    if len(tempList) == 0:  # Able to find records of cargo grade at port (api), date/week problem
        raise HTTPException(status_code=404, detail="Historical Data does not have Temperature of cargo grade for "
                                                    "that date. Try 1/2 weeks before or after.")
    _, temp = cargo.avgResults(tempList)

    result = {'port': cargoinfo.Port, 'cargo': cargoinfo.Cargo, 'api': api, 'temp (F)': temp,
              'date': f'{cargoinfo.Year}-{cargoinfo.Month}-{cargoinfo.Date}'}
    return result


# Instructions
@app.post("/instructions")
def getInstructions(instructionsinfo: schemas.InstructionsInfo, db: Session = Depends(get_db)):
    instructionsList = []
    # Cargoes
    for c in instructionsinfo.Cargoes:
        instructions = crud.getInstructionsID(db, featureType='Cargo', feature=c)
        if len(instructions) > 0:
            instructionsList.append([i[0] for i in instructions])
    # Port
    instructions = crud.getInstructionsID(db, featureType='Port', feature=instructionsinfo.Port)
    if len(instructions) > 0:
        instructionsList.append([i[0] for i in instructions])

    # Berth
    instructions = crud.getInstructionsID(db, featureType='Berth', feature=instructionsinfo.Berth)
    if len(instructions) > 0:
        instructionsList.append([i[0] for i in instructions])

    # Connection
    instructions = crud.getInstructionsID(db, featureType='Connection', feature=instructionsinfo.Connection)
    if len(instructions) > 0:
        instructionsList.append([i[0] for i in instructions])

    # Operation
    instructions = crud.getInstructionsID(db, featureType='Operation', feature=instructionsinfo.Operation)
    if len(instructions) > 0:
        instructionsList.append([i[0] for i in instructions])

    instruction_set = set.intersection(*map(set, instructionsList))
    if len(instruction_set) == 0:
        raise HTTPException(status_code=404, detail="No instructions found. Please check features being input.")

    result = []
    for idx in instruction_set:
        ins = crud.getInstructions(db, instructionid=idx)
        result.append({'Labels': ins.labels, 'Instructions': ins.instructions})

    return result


@app.post("/nomination")
def getNominationSimilarity(nominationinfo: schemas.NominationInfo, db: Session = Depends(get_db)):
    # Get similar voyages
    features = []
    voyid_list = []
    history = crud.getNominationFeatures(db)

    for his in history:
        features.append(his.serialise())
        voyid_list.append(his.getVoyID())
    new_feature = nomination.preprocess(nominationinfo.Vol, nominationinfo.API, nominationinfo.LoadingPortsCount)
    features = [new_feature] + features
    features = (features - np.mean(features, axis=0)) / np.std(features, axis=0)
    features = np.nan_to_num(features)
    similarity = 1 - nomination.cosine([features[0]], features[1:])

    top_voyid, score = nomination.getTop(similarity[0], voyid_list, 7)

    result = {}
    for idx in range(len(top_voyid)):
        voyid = top_voyid[idx]
        voy_row = crud.getVoyage(db, voy_id=voyid)

        if voy_row is not None:
            vessel = voy_row.vessel
            voyno = voy_row.voy_no
            # Get Nomination Plan of similar voyage
            nomination_plan = crud.getAllVoyageDetails(db, voyid=voyid)
            clean_nomination = {}
            for nplan in nomination_plan:
                if not pd.isna(nplan.nomination):
                    # Cargo
                    cargo = crud.getCargo(db, cargoid=nplan.cargo_xid)[0]
                    # Nomination
                    amount = nplan.nomination
                    # Min Tolerance
                    if pd.notna(nplan.mintol):
                        mintol = round(1 - nplan.mintol, 5)
                    else:
                        mintol = None
                    # Max Tolerance
                    if nplan.maxtol != 'Max':
                        if pd.notna(float(nplan.maxtol)):
                            maxtol = round(float(nplan.maxtol) - 1, 5)
                        else:
                            maxtol = None
                    else:
                        maxtol = 'Max'
                    clean_nomination[cargo] = {'Vol (BBLS)': amount, 'Max Tol': maxtol, 'Min Tol': mintol}

            # Get Stowage Plan of similar voyage
            stowage_plan = crud.getStowage(db, voyid=voyid)
            clean_stowage = {}
            for tank in stowage_plan:
                cargo = crud.getCargo(db, cargoid=tank.cargo_xid)[0]
                clean_stowage[tank.tank] = {'Cargo': cargo, 'Vol (BBLS)': round(np.nan_to_num(tank.bbls), 5),
                                            'Weight (MT)': round(np.nan_to_num(tank.mt), 5)}

            result[idx + 1] = {'Vessel': vessel, 'Voyage': voyno, 'similarity': score[idx],
                               'Nomination': clean_nomination,
                               'Stowage': clean_stowage}

    return result


# @app.post("/ballast")
# def getBallast(ballastinfo: schemas.BallastInfo):
#     cargo = len(ballastinfo.CurrPort)
#     nom = 0
#     api = 0
#     leftover_nom = 0
#     leftover_api = 0
#     cum_nom = 0
#     cum_api = 0
#
#     for cur in ballastinfo.CurrPort:
#         nom += cur['Vol']
#         api += cur['API']
#
#     for nex in ballastinfo.NextPort:
#         leftover_nom += nex['Vol']
#         leftover_api += nex['API']
#
#     for past in ballastinfo.PrevPort:
#         cum_nom += past['Vol']
#         cum_api += past['API']
#
#     feature = [cargo, nom, api, leftover_nom, leftover_api, cum_nom, cum_api]
#     ballastPred = ballast_model.predict(np.array(feature).reshape(1, -1))[0]
#     cargoTanksPred = cargotanks_model.predict(np.array(feature).reshape(1, -1))[0]
#     result = {'Cargo Tanks': int(cargoTanksPred), 'Ballast (MT)': float(ballastPred)}
#     return result
