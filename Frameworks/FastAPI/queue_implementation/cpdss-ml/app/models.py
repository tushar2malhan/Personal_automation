from sqlalchemy import Column, ForeignKey, Integer, String, Float

from .database import Base


class Cargo(Base):
    __tablename__ = "cargo"
    cargo_id = Column(Integer, primary_key=True)
    cargo = Column(String, nullable=False)


class CargoInfo(Base):
    __tablename__ = "cargo_info"
    cargo_info_id = Column(Integer, primary_key=True)
    ship = Column(String, nullable=False)
    port = Column(String, nullable=False)
    cargo_xid = Column(Integer, ForeignKey('cargo.cargo_id'), nullable=False)
    api = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    weekno = Column(Integer, nullable=False)
    date = Column(String, nullable=False)


class InstructionsFeatures(Base):
    __tablename__ = "instructions_feature_mapping"
    ins_feature_id = Column(Integer, primary_key=True)
    ins_xid = Column(Integer, ForeignKey('instructions.ins_id'), nullable=False)
    feature = Column(String, nullable=False)
    feature_type = Column(String, nullable=False)


class Instructions(Base):
    __tablename__ = "instructions"
    ins_id = Column(Integer, primary_key=True)
    instructions = Column(String, nullable=False)
    labels = Column(String, nullable=False)


class InstructionsMapping(Base):
    __tablename__ = "instructions_mapping"
    ins_map_id = Column(Integer, primary_key=True)
    ins_xid = Column(Integer, ForeignKey('instructions.ins_id'), nullable=False)
    ops_xid = Column(Integer, ForeignKey('voyage_operations.ops_id'), nullable=False)
    vessel = Column(String, nullable=False)


class VoyageDetails(Base):
    __tablename__ = "voyage_details"
    voy_details_id = Column(Integer, primary_key=True)
    cargo_xid = Column(Integer, ForeignKey('cargo.cargo_id'), nullable=False)
    api = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    nomination = Column(Float, nullable=False)
    maxtol = Column(String, nullable=False)
    mintol = Column(Float, nullable=False)
    ops_xid = Column(Integer, ForeignKey('voyage_operations.ops_id'), nullable=False)
    voy_xid = Column(Integer, ForeignKey('voyage.ins_id'), nullable=False)
    port = Column(String, nullable=False)
    vessel = Column(String, nullable=False)

    def serialize(self):
        return [self.nomination, self.maxtol, self.mintol, self.cargo_id]


class VoyageOperations(Base):
    __tablename__ = "voyage_operations"
    ops_id = Column(Integer, primary_key=True)
    voy_xid = Column(Integer, ForeignKey('voyage.ins_id'), nullable=False)
    port = Column(String, nullable=False)
    vessel = Column(String, nullable=False)
    operation = Column(String, nullable=False)
    berth = Column(String, nullable=False)
    hose_connection = Column(String, nullable=False)
    flow_rate = Column(Float, nullable=False)
    flow_pressure = Column(Float, nullable=False)
    bulk_rate = Column(Float, nullable=False)
    bulk_pressure = Column(Float, nullable=False)
    deviation_rate = Column(Float, nullable=False)
    deviation_pressure = Column(Float, nullable=False)
    onhand = Column(Float, nullable=False)
    ballast = Column(Float, nullable=False)
    cargotanks = Column(Float, nullable=False)


class VoyagePump(Base):
    __tablename__ = "voyage_pump"
    pump_id = Column(Integer, primary_key=True)
    ops_xid = Column(Integer, ForeignKey('voyage_operations.ops_id'), nullable=False)
    seq = Column(Integer, nullable=False)
    pressure = Column(Float, nullable=False)
    rate = Column(Float, nullable=False)


class VoyageStowages(Base):
    __tablename__ = "voyage_stowages"
    stowage_id = Column(Integer, primary_key=True)
    voy_xid = Column(Integer, ForeignKey('voyage.ins_id'), nullable=False)
    tank = Column(String, nullable=False)
    cargo_xid = Column(Integer, ForeignKey('cargo.cargo_id'), nullable=False)
    bbls = Column(Float, nullable=False)
    mt = Column(Float, nullable=False)


class Voyages(Base):
    __tablename__ = "voyage"
    voy_id = Column(Integer, primary_key=True)
    vessel = Column(String, nullable=False)
    voy_no = Column(Integer, nullable=False)
    start_port = Column(String, nullable=False)
    end_port = Column(String, nullable=False)


class NominationFeatures(Base):
    __tablename__ = "nomination_features"
    feature_id = Column(Integer, primary_key=True)
    voy_xid = Column(Integer, ForeignKey('voyage.ins_id'), nullable=False)
    nomination0 = Column(Float, nullable=False)
    nomination1 = Column(Float, nullable=False)
    nomination2 = Column(Float, nullable=False)
    nomination3 = Column(Float, nullable=False)
    nomination4 = Column(Float, nullable=False)
    nomination5 = Column(Float, nullable=False)
    nomination6 = Column(Float, nullable=False)
    api0 = Column(Float, nullable=False)
    api1 = Column(Float, nullable=False)
    api2 = Column(Float, nullable=False)
    api3 = Column(Float, nullable=False)
    api4 = Column(Float, nullable=False)
    api5 = Column(Float, nullable=False)
    api6 = Column(Float, nullable=False)
    total_vol = Column(Float, nullable=False)
    ports = Column(Float, nullable=False)

    def serialise(self):
        return [self.nomination0, self.nomination1, self.nomination2, self.nomination3, self.nomination4,
                self.nomination5, self.nomination6,
                self.api0, self.api1, self.api2, self.api3, self.api4, self.api5, self.api6, self.total_vol, self.ports]

    def getVoyID(self):
        return self.voy_xid
