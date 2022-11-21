DROP TABLE  nomination_features, voyage_stowages, voyage_pump, voyage_details, voyage_operations,voyage, instructions_feature_mapping, instructions_mapping, instructions ,cargo, cargo_info;

-- Cargo Related Tables
CREATE TABLE Cargo(
	Cargo_ID INT GENERATED ALWAYS AS IDENTITY,
	Cargo VARCHAR(255) NOT NULL,
	PRIMARY KEY(Cargo_ID)
);

CREATE TABLE Cargo_Info(
    Cargo_Info_ID INT GENERATED ALWAYS AS IDENTITY,
    Ship VARCHAR(255) NOT NULL,
    Port VARCHAR(255) NOT NULL,
    Cargo_XID INT NOT NULL,
    API Double Precision NOT NULL,
    Temperature Double Precision NOT NULL,
    WeekNo INT NOT NULL,
    Date VARCHAR(255) NOT NULL,
	PRIMARY KEY(Cargo_Info_ID),
	CONSTRAINT fk_cargo
	FOREIGN KEY(Cargo_XID) 
	REFERENCES Cargo(Cargo_ID)
	ON DELETE CASCADE
);


-- Voyage Related Tables 
CREATE TABLE Voyage(
   Voy_ID INT GENERATED ALWAYS AS IDENTITY,
   Vessel VARCHAR(255) NOT NULL,
   Voy_No INT NOT NULL,
   Start_Port VARCHAR(255) NOT NULL,
   End_Port VARCHAR(255) NOT NULL,
   PRIMARY KEY(Voy_ID)
);

CREATE TABLE Voyage_Operations(
	Ops_ID INT GENERATED ALWAYS AS IDENTITY,
	Voy_XID INT,
    Vessel VARCHAR(255) NOT NULL,
    Port VARCHAR(255) NOT NULL,
    Operation VARCHAR(255) NOT NULL,
    Arrival timestamp without time zone,
    Departure timestamp without time zone,
    Berth VARCHAR(255),
	Hose_Connection VARCHAR(255),
	Onhand Double Precision,
	Ballast Double Precision,
	CargoTanks INT,
	Deviation_Rate  Double Precision,
	Bulk_Rate  Double Precision,
	Flow_Rate  Double Precision,
	Deviation_Pressure  Double Precision,
	Bulk_Pressure  Double Precision,
	Flow_Pressure  Double Precision,
	PRIMARY KEY(Ops_ID),
    CONSTRAINT fk_operations
	FOREIGN KEY(Voy_XID) 
	REFERENCES Voyage(Voy_ID)
	ON DELETE CASCADE
);

CREATE TABLE Voyage_Details(
    Voy_Details_ID INT GENERATED ALWAYS AS IDENTITY,
	Voy_XID INT NOT NULL,
	Ops_XID INT NOT NULL,
    Vessel VARCHAR(255) NOT NULL,
    Port VARCHAR(255) NOT NULL,
	API Double Precision,
	Temperature Double Precision,
    Nomination Double Precision,
    MaxTol VARCHAR(255),
    MinTol Double Precision,
    Cargo_XID INT NOT NULL,
	PRIMARY KEY(Voy_Details_ID),
    CONSTRAINT fk_voyages
	FOREIGN KEY(Voy_XID) 
	REFERENCES Voyage(Voy_ID) ON DELETE CASCADE,
	CONSTRAINT fk_operations
	FOREIGN KEY(Ops_XID) 
	REFERENCES Voyage_Operations(Ops_ID) ON DELETE CASCADE,
	CONSTRAINT fk_cargo
	FOREIGN KEY(Cargo_XID) 
	REFERENCES Cargo(Cargo_ID) ON DELETE CASCADE
);

CREATE TABLE Voyage_Pump (
	Pump_ID INT GENERATED ALWAYS AS IDENTITY,
	Voy_ID INT NOT NULL,
	Ops_ID INT NOT NULL,
	Seq INT NOT NULL,
    Pressure Double Precision NOT NULL,
    Rate Double Precision NOT NULL,
	PRIMARY KEY(Pump_ID),
    CONSTRAINT fk_voyages
	FOREIGN KEY(Voy_XID) 
	REFERENCES Voyage(Voy_ID) ON DELETE CASCADE,
	CONSTRAINT fk_operations
	FOREIGN KEY(Ops_XID) 
	REFERENCES Voyage_Operations(Ops_ID) ON DELETE CASCADE
);

CREATE TABLE Voyage_Stowages(
	Stowage_ID INT GENERATED ALWAYS AS IDENTITY,
	Voy_XID INT NOT NULL,
	Vessel VARCHAR(255) NOT NULL,
    Tank VARCHAR(255) NOT NULL,
    Cargo_XID INT NOT NULL,
    BBLS Double Precision ,
    MT Double Precision,
	PRIMARY KEY(Stowage_ID),
    CONSTRAINT fk_voyages
	FOREIGN KEY(Voy_XID) 
	REFERENCES Voyage(Voy_ID) ON DELETE CASCADE,
	CONSTRAINT fk_cargo
	FOREIGN KEY(Cargo_XID) 
	REFERENCES Cargo(Cargo_ID) ON DELETE CASCADE
);

CREATE TABLE Nomination_Features(
	Feature_ID INT GENERATED ALWAYS AS IDENTITY,
	Voy_XID INT NOT NULL,
	Nomination0 Double Precision Not Null,
	Nomination1 Double Precision Not Null,
	Nomination2 Double Precision Not Null,
	Nomination3 Double Precision Not Null,
	Nomination4 Double Precision Not Null,
	Nomination5 Double Precision Not Null,
	Nomination6 Double Precision Not Null,
	API0 Double Precision Not Null,
	API1 Double Precision Not Null,
	API2 Double Precision Not Null,
	API3 Double Precision Not Null,
	API4 Double Precision Not Null,
	API5 Double Precision Not Null,
	API6 Double Precision Not Null,
	Total_Vol Double Precision Not Null,
	Ports Double Precision Not Null,
	PRIMARY KEY(Feature_ID),
    CONSTRAINT fk_voyages
	FOREIGN KEY(Voy_XID) 
	REFERENCES Voyage(Voy_ID) ON DELETE CASCADE
);



-- Instructions Related Tables
CREATE TABLE Instructions(
	Ins_ID INT GENERATED ALWAYS AS IDENTITY,
	Instructions Text NOT NULL,
	Labels VARCHAR(255) NOT NULL,
	PRIMARY KEY(Ins_ID)
);

CREATE TABLE Instructions_Feature_Mapping(	
    Ins_Feature_ID INT GENERATED ALWAYS AS IDENTITY,
    Ins_XID INT NOT NULL,
    Feature VARCHAR(255),
    Feature_Type VARCHAR(255) NOT NULL,
	PRIMARY KEY(Ins_Feature_ID),
	CONSTRAINT fk_instructions
	FOREIGN KEY(Ins_XID) 
	REFERENCES Instructions(Ins_ID) ON DELETE CASCADE
);

CREATE TABLE Instructions_Mapping(
	Ins_Map_ID INT GENERATED ALWAYS AS IDENTITY,
	Ops_XID INT NOT NULL,
	Vessel VARCHAR(255) NOT NULL,
    Ins_XID INT NOT NULL,
	PRIMARY KEY(Ins_Map_ID),
	CONSTRAINT fk_operations
	FOREIGN KEY(Ops_XID) 
	REFERENCES Voyage_Operations(Ops_ID) ON DELETE CASCADE,
	CONSTRAINT fk_instructions
	FOREIGN KEY(Ins_XID) 
	REFERENCES Instructions(Ins_ID) ON DELETE CASCADE
);

-- Cargo
CREATE UNIQUE INDEX ix_cargo_cargo on cargo(cargo);

-- Cargo Info
CREATE INDEX ix_cargoinfo_cargoxid ON cargo_info(cargo_xid);
CREATE INDEX ix_cargoinfo_port_cargoxid ON cargo_info(port, cargo_xid);
CREATE INDEX ix_cargoinfo_port_cargoxid_week ON cargo_info(port, cargo_xid, weekno);

-- Instructions Feature mapping
CREATE INDEX ix_instructionsfeaturemapping_insxid ON instructions_feature_mapping(ins_xid);
Create INDEX ix_instructionsfeaturemapping_featuretype_feature ON instructions_feature_mapping(feature_type, feature);

-- Instructions Mapping
CREATE INDEX ix_instructionsmapping_insxid ON instructions_mapping(ins_xid);
CREATE INDEX ix_instructionsmapping_opsxid ON instructions_mapping(ops_xid);

-- Nomination Features
CREATE INDEX ix_nominationfeatures_voyxid ON nomination_features(voy_xid);

-- Voyage Details
CREATE INDEX ix_voyagedetails_voyxid ON voyage_details(voy_xid);
CREATE INDEX ix_voyagedetails_opsxid ON voyage_details(ops_xid);
CREATE INDEX ix_voyagedetails_cargoxid ON voyage_details(cargo_xid);

-- Voyage Operations
CREATE INDEX ix_voyageoperations_voyxid ON voyage_operations(voy_xid);
CREATE INDEX ix_voyageoperations_vessel_port ON voyage_operations(vessel, port);

-- Voyage Pump
CREATE INDEX ix_voyagepump_voyxid ON voyage_pump(voy_xid);

-- Voyage Stowages
CREATE INDEX ix_voyagestowages_voyxid ON voyage_stowages(voy_xid);