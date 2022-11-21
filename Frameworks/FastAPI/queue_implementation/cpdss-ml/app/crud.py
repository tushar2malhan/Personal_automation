from sqlalchemy.orm import Session

from . import models


# Cargo
def getCargoID(db: Session, cargo: str):
    result = db.query(models.Cargo.cargo_id).filter(models.Cargo.cargo == cargo).first()
    return result


def getCargo(db: Session, cargoid: int):
    return db.query(models.Cargo.cargo).filter(models.Cargo.cargo_id == cargoid).first()


# Cargo Info
def getTemp(db: Session, port: str, cargoid: int, week: int):
    return db.query(models.CargoInfo.temperature).filter(models.CargoInfo.port == port,
                                                         models.CargoInfo.cargo_xid == cargoid,
                                                         models.CargoInfo.weekno == week).all()


def getAPI(db: Session, port: str, cargoid: int):
    return db.query(models.CargoInfo.api).filter(models.CargoInfo.port == port,
                                                 models.CargoInfo.cargo_xid == cargoid).all()


# Voyage Info
def getVoyagesAtPort(db: Session, port: str, vessel: str):
    if len(vessel) == '':
        result = db.query(models.VoyageOperations).filter(models.VoyageOperations.port == port).all()
    else:
        result = db.query(models.VoyageOperations).filter(models.VoyageOperations.port == port,
                                                          models.VoyageOperations.vessel == vessel).all()
    return result


# Instructions ID
def getInstructionsID(db: Session, featureType: str, feature: str):
    return db.query(models.InstructionsFeatures.ins_xid).filter(models.InstructionsFeatures.feature_type == featureType,
                                                                models.InstructionsFeatures.feature == feature).all()


# Instructions
def getInstructions(db: Session, instructionid: int):
    return db.query(models.Instructions).filter(models.Instructions.ins_id == instructionid).first()


def getVoyageInstructions(db: Session, ops_id: int):
    return db.query(models.InstructionsMapping.ins_xid).filter(models.InstructionsMapping.ops_xid == ops_id).all()


# Voyages
def getVoyageID(db: Session, vessel: str, voy: int):
    return db.query(models.Voyages.voy_id).filter(models.Voyages.vessel == vessel, models.Voyages.voy_no == voy).first()


# Voyages
def getVoyage(db: Session, voy_id: int):
    return db.query(models.Voyages).filter(models.Voyages.voy_id == voy_id).first()


# Voyages Operation
def getAllVoyageOperations(db: Session, voy_id: int):
    return db.query(models.VoyageOperations).filter(models.VoyageOperations.voy_xid == voy_id).all()


def getOperations(db: Session, voy_id: int, port: str):
    return db.query(models.VoyageOperations).filter(models.VoyageOperations.port == port,
                                                    models.VoyageOperations.voy_xid == voy_id).first()


# Voyage Details
def getAllVoyageDetails(db: Session, voyid: int):
    return db.query(models.VoyageDetails).filter(models.VoyageDetails.voy_xid == voyid).all()


def getOperationDetails(db: Session, voy_id: int, port: str):
    return db.query(models.VoyageDetails).filter(models.VoyageDetails.port == port,
                                                 models.VoyageDetails.voy_xid == voy_id).all()


# Voyage Stowage
def getStowage(db: Session, voyid: int):
    return db.query(models.VoyageStowages).filter(models.VoyageStowages.voy_xid == voyid).all()


# Voyage Pump
def getPump(db: Session, opsid: int):
    return db.query(models.VoyagePump).filter(models.VoyagePump.ops_xid == opsid).all()


# Nomination Features
def getNominationFeatures(db: Session):
    return db.query(models.NominationFeatures).all()
