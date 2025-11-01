-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS Troop_Upgrade_Paths;
DROP TABLE IF EXISTS Troop_Equipment_Junction;
DROP TABLE IF EXISTS Skills;
DROP TABLE IF EXISTS Attributes;
DROP TABLE IF EXISTS Troops;
DROP TABLE IF EXISTS Items;
DROP TABLE IF EXISTS Item_Types;
DROP TABLE IF EXISTS Cultures;

-- Create Cultures Table
CREATE TABLE Cultures (
    culture_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

-- Create Item_Types Table
CREATE TABLE Item_Types (
    item_type_id INT PRIMARY KEY,
    item_type VARCHAR(50) NOT NULL
);

-- Create Items Table
CREATE TABLE Items (
    item_id INT PRIMARY KEY,
    item_type_id INT,
    culture_id INT,
    name VARCHAR(100) NOT NULL,
    FOREIGN KEY (item_type_id) REFERENCES Item_Types(item_type_id),
    FOREIGN KEY (culture_id) REFERENCES Cultures(culture_id)
);

-- Create Troops Table
CREATE TABLE Troops (
    troop_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    tier INT NOT NULL,
    wage INT NOT NULL,
    is_mounted BOOLEAN NOT NULL,
    culture_id INT,
    FOREIGN KEY (culture_id) REFERENCES Cultures(culture_id)
);

-- Create Attributes Table
CREATE TABLE Attributes (
    attribute_id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
);

-- Create Skills Table
CREATE TABLE Skills (
    skill_id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    is_combat_skill BOOLEAN NOT NULL,
    attribute_id INT,
    FOREIGN KEY (attribute_id) REFERENCES Attributes(attribute_id)
);

-- Create Troop_Equipment_Junction Table
CREATE TABLE Troop_Equipment_Junction (
    troop_id INT,
    item_id INT,
    slot VARCHAR(50),
    PRIMARY KEY (troop_id, item_id, slot),
    FOREIGN KEY (troop_id) REFERENCES Troops(troop_id),
    FOREIGN KEY (item_id) REFERENCES Items(item_id)
);

-- Create Troop_Upgrade_Paths Table
CREATE TABLE Troop_Upgrade_Paths (
    base_troop_id INT,
    upgraded_troop_id INT,
    xp_cost INT,
    PRIMARY KEY (base_troop_id, upgraded_troop_id),
    FOREIGN KEY (base_troop_id) REFERENCES Troops(troop_id),
    FOREIGN KEY (upgraded_troop_id) REFERENCES Troops(troop_id)
);