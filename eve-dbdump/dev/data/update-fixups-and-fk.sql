
alter table eveIcons modify iconID smallint;
alter table eveGraphics modify graphicID smallint;

ALTER TABLE `agtAgents` ADD FOREIGN KEY (`agentID`) REFERENCES `eveNames` (`itemID`);
ALTER TABLE `agtAgents` ADD FOREIGN KEY (`divisionID`) REFERENCES `crpNPCDivisions` (`divisionID`);
ALTER TABLE `agtAgents` ADD FOREIGN KEY (`corporationID`) REFERENCES `crpNPCCorporations` (`corporationID`);
-- ALTER TABLE `agtAgents` ADD FOREIGN KEY (`stationID`) REFERENCES `staStations` (`stationID`);
ALTER TABLE `agtAgents` ADD FOREIGN KEY (`locationID`) REFERENCES `mapDenormalize` (`itemID`);
ALTER TABLE `agtAgents` ADD FOREIGN KEY (`agentTypeID`) REFERENCES `agtAgentTypes` (`agentTypeID`);

ALTER TABLE `agtConfig` ADD FOREIGN KEY (`agentID`) REFERENCES `agtAgents` (`agentID`);

ALTER TABLE `agtResearchAgents` ADD FOREIGN KEY (`agentID`) REFERENCES `agtAgents` (`agentID`);
ALTER TABLE `agtResearchAgents` ADD FOREIGN KEY (`typeID`) REFERENCES `invTypes` (`typeID`);

ALTER TABLE `chrAncestries` ADD FOREIGN KEY (`bloodlineID`) REFERENCES `chrBloodlines` (`bloodlineID`);
-- ALTER TABLE `chrAncestries` ADD FOREIGN KEY (`graphicID`) REFERENCES `eveGraphics` (`graphicID`);
alter table chrAncestries modify iconID smallint;
ALTER TABLE `chrAncestries` ADD FOREIGN KEY (`iconID`) REFERENCES `eveIcons` (`iconID`);

-- ALTER TABLE `chrAttributes` ADD FOREIGN KEY (`graphicID`) REFERENCES `eveGraphics` (`graphicID`);
alter table chrAttributes modify iconID smallint;
ALTER TABLE `chrAttributes` ADD FOREIGN KEY (`iconID`) REFERENCES `eveIcons` (`iconID`);

ALTER TABLE `chrBloodlines` ADD FOREIGN KEY (`raceID`) REFERENCES `chrRaces` (`raceID`);
ALTER TABLE `chrBloodlines` ADD FOREIGN KEY (`shipTypeID`) REFERENCES `invTypes` (`typeID`);
ALTER TABLE `chrBloodlines` ADD FOREIGN KEY (`corporationID`) REFERENCES `crpNPCCorporations` (`corporationID`);
-- ALTER TABLE `chrBloodlines` ADD FOREIGN KEY (`graphicID`) REFERENCES `eveGraphics` (`graphicID`);
alter table chrBloodlines modify iconID smallint;
ALTER TABLE `chrBloodlines` ADD FOREIGN KEY (`iconID`) REFERENCES `eveIcons` (`iconID`);

ALTER TABLE `chrFactions` ADD FOREIGN KEY (`solarSystemID`) REFERENCES `mapSolarSystems` (`solarSystemID`);
ALTER TABLE `chrFactions` ADD FOREIGN KEY (`corporationID`) REFERENCES `crpNPCCorporations` (`corporationID`);
ALTER TABLE `chrFactions` ADD FOREIGN KEY (`militiaCorporationID`) REFERENCES `crpNPCCorporations` (`corporationID`);
alter table chrFactions modify iconID smallint;
ALTER TABLE `chrFactions` ADD FOREIGN KEY (`iconID`) REFERENCES `eveIcons` (`iconID`);

-- ALTER TABLE `chrRaces` ADD FOREIGN KEY (`graphicID`) REFERENCES `eveGraphics` (`graphicID`);
alter table chrRaces modify iconID smallint;
ALTER TABLE `chrRaces` ADD FOREIGN KEY (`iconID`) REFERENCES `eveIcons` (`iconID`);

ALTER TABLE `crpNPCCorporationDivisions` ADD FOREIGN KEY (`corporationID`) REFERENCES `crpNPCCorporations` (`corporationID`);
ALTER TABLE `crpNPCCorporationDivisions` ADD FOREIGN KEY (`divisionID`) REFERENCES `crpNPCDivisions` (`divisionID`);

ALTER TABLE `crpNPCCorporationResearchFields` ADD FOREIGN KEY (`corporationID`) REFERENCES `crpNPCCorporations` (`corporationID`);
ALTER TABLE `crpNPCCorporationResearchFields` ADD FOREIGN KEY (`skillID`) REFERENCES `invTypes` (`typeID`);

ALTER TABLE `crpNPCCorporations` ADD FOREIGN KEY (`corporationID`) REFERENCES `eveNames` (`itemID`);
ALTER TABLE `crpNPCCorporations` ADD FOREIGN KEY (`solarSystemID`) REFERENCES `mapSolarSystems` (`solarSystemID`);
ALTER TABLE `crpNPCCorporations` ADD FOREIGN KEY (`factionID`) REFERENCES `chrFactions` (`factionID`);
ALTER TABLE `crpNPCCorporations` ADD FOREIGN KEY (`investorID1`) REFERENCES `crpNPCCorporations` (`corporationID`);
ALTER TABLE `crpNPCCorporations` ADD FOREIGN KEY (`investorID2`) REFERENCES `crpNPCCorporations` (`corporationID`);
ALTER TABLE `crpNPCCorporations` ADD FOREIGN KEY (`investorID3`) REFERENCES `crpNPCCorporations` (`corporationID`);
ALTER TABLE `crpNPCCorporations` ADD FOREIGN KEY (`investorID4`) REFERENCES `crpNPCCorporations` (`corporationID`);
ALTER TABLE `crpNPCCorporations` ADD FOREIGN KEY (`friendID`) REFERENCES `crpNPCCorporations` (`corporationID`);
ALTER TABLE `crpNPCCorporations` ADD FOREIGN KEY (`enemyID`) REFERENCES `crpNPCCorporations` (`corporationID`);
alter table crpNPCCorporations modify iconID smallint;
ALTER TABLE `crpNPCCorporations` ADD FOREIGN KEY (`iconID`) REFERENCES `eveIcons` (`iconID`);

ALTER TABLE `crpNPCCorporationTrades` ADD FOREIGN KEY (`corporationID`) REFERENCES `crpNPCCorporations` (`corporationID`);
ALTER TABLE `crpNPCCorporationTrades` ADD FOREIGN KEY (`typeID`) REFERENCES `invTypes` (`typeID`);

ALTER TABLE `crtRecommendations` ADD FOREIGN KEY (`certificateID`) REFERENCES `crtCertificates` (`certificateID`);
ALTER TABLE `crtRecommendations` ADD FOREIGN KEY (`shipTypeID`) REFERENCES `invTypes` (`typeID`);

update crtRelationships set parentID=null where parentID in (0,-1) and parentTypeID > 0; 
update crtRelationships set parentTypeID=null where parentTypeID in (0,-1) and parentID > 0;
ALTER TABLE `crtRelationships` ADD FOREIGN KEY (`parentID`) REFERENCES `crtCertificates` (`certificateID`);
ALTER TABLE `crtRelationships` ADD FOREIGN KEY (`parentTypeID`) REFERENCES `invTypes` (`typeID`);
ALTER TABLE `crtRelationships` ADD FOREIGN KEY (`childID`) REFERENCES `crtCertificates` (`certificateID`);

ALTER TABLE `crtCertificates` ADD FOREIGN KEY (`categoryID`) REFERENCES `crtCategories` (`categoryID`);
ALTER TABLE `crtCertificates` ADD FOREIGN KEY (`classID`) REFERENCES `crtClasses` (`classID`);
ALTER TABLE `crtCertificates` ADD FOREIGN KEY (`corpID`) REFERENCES `crpNPCCorporations` (`corporationID`);
alter table crtCertificates modify iconID smallint;
update crtCertificates set iconID=null where iconID not in (select iconID from eveIcons);
ALTER TABLE `crtCertificates` ADD FOREIGN KEY (`iconID`) REFERENCES `eveIcons` (`iconID`);

ALTER TABLE `dgmAttributeTypes` ADD FOREIGN KEY (`categoryID`) REFERENCES `dgmAttributeCategories` (`categoryID`);
-- ALTER TABLE `dgmAttributeTypes` ADD FOREIGN KEY (`graphicID`) REFERENCES `eveGraphics` (`graphicID`);
ALTER TABLE `dgmAttributeTypes` ADD FOREIGN KEY (`unitID`) REFERENCES `eveUnits` (`unitID`);
alter table dgmAttributeTypes modify iconID smallint;
ALTER TABLE `dgmAttributeTypes` ADD FOREIGN KEY (`iconID`) REFERENCES `eveIcons` (`iconID`);

-- effectCategory spec missing
-- ALTER TABLE `dgmEffects` ADD FOREIGN KEY (`graphicID`) REFERENCES `eveGraphics` (`graphicID`);
ALTER TABLE `dgmEffects` ADD FOREIGN KEY (`durationAttributeID`) REFERENCES `dgmAttributeTypes` (`attributeID`);
ALTER TABLE `dgmEffects` ADD FOREIGN KEY (`trackingSpeedAttributeID`) REFERENCES `dgmAttributeTypes` (`attributeID`);
ALTER TABLE `dgmEffects` ADD FOREIGN KEY (`dischargeAttributeID`) REFERENCES `dgmAttributeTypes` (`attributeID`);
ALTER TABLE `dgmEffects` ADD FOREIGN KEY (`rangeAttributeID`) REFERENCES `dgmAttributeTypes` (`attributeID`);
ALTER TABLE `dgmEffects` ADD FOREIGN KEY (`falloffAttributeID`) REFERENCES `dgmAttributeTypes` (`attributeID`);
ALTER TABLE `dgmEffects` ADD FOREIGN KEY (`npcUsageChanceAttributeID`) REFERENCES `dgmAttributeTypes` (`attributeID`);
ALTER TABLE `dgmEffects` ADD FOREIGN KEY (`npcActivationChanceAttributeID`) REFERENCES `dgmAttributeTypes` (`attributeID`);
ALTER TABLE `dgmEffects` ADD FOREIGN KEY (`fittingUsageChanceAttributeID`) REFERENCES `dgmAttributeTypes` (`attributeID`);
alter table dgmEffects modify iconID smallint;
ALTER TABLE `dgmEffects` ADD FOREIGN KEY (`iconID`) REFERENCES `eveIcons` (`iconID`);

delete from dgmTypeAttributes where typeID not in (select typeID from invTypes);
ALTER TABLE `dgmTypeAttributes` ADD FOREIGN KEY (`typeID`) REFERENCES `invTypes` (`typeID`);
ALTER TABLE `dgmTypeAttributes` ADD FOREIGN KEY (`attributeID`) REFERENCES `dgmAttributeTypes` (`attributeID`);

delete from dgmTypeEffects where typeID not in (select typeID from invTypes);
ALTER TABLE `dgmTypeEffects` ADD FOREIGN KEY (`typeID`) REFERENCES `invTypes` (`typeID`);
ALTER TABLE `dgmTypeEffects` ADD FOREIGN KEY (`effectID`) REFERENCES `dgmEffects` (`effectID`);

alter table eveGraphics modify explosionID smallint;
ALTER TABLE `eveGraphics` ADD FOREIGN KEY (`explosionID`) REFERENCES `eveGraphics` (`graphicID`);

ALTER TABLE `eveNames` ADD FOREIGN KEY (`categoryID`) REFERENCES `invCategories` (`categoryID`);
ALTER TABLE `eveNames` ADD FOREIGN KEY (`groupID`) REFERENCES `invGroups` (`groupID`);
ALTER TABLE `eveNames` ADD FOREIGN KEY (`typeID`) REFERENCES `invTypes` (`typeID`);

ALTER TABLE `invBlueprintTypes` ADD FOREIGN KEY (`blueprintTypeID`) REFERENCES `invTypes` (`typeID`);
ALTER TABLE `invBlueprintTypes` ADD FOREIGN KEY (`parentBlueprintTypeID`) REFERENCES `invTypes` (`typeID`);
delete from invBlueprintTypes where productTypeID not in (select typeID from invTypes);
ALTER TABLE `invBlueprintTypes` ADD FOREIGN KEY (`productTypeID`) REFERENCES `invTypes` (`typeID`);

-- ALTER TABLE `invCategories` ADD FOREIGN KEY (`graphicID`) REFERENCES `eveGraphics` (`graphicID`);
alter table invCategories modify iconID smallint;
ALTER TABLE `invCategories` ADD FOREIGN KEY (`iconID`) REFERENCES `eveIcons` (`iconID`);

ALTER TABLE `invContrabandTypes` ADD FOREIGN KEY (`factionID`) REFERENCES `chrFactions` (`factionID`);
ALTER TABLE `invContrabandTypes` ADD FOREIGN KEY (`typeID`) REFERENCES `invTypes` (`typeID`);

ALTER TABLE `invControlTowerResources` ADD FOREIGN KEY (`controlTowerTypeID`) REFERENCES `invTypes` (`typeID`);
ALTER TABLE `invControlTowerResources` ADD FOREIGN KEY (`resourceTypeID`) REFERENCES `invTypes` (`typeID`);
ALTER TABLE `invControlTowerResources` ADD FOREIGN KEY (`factionID`) REFERENCES `chrFactions` (`factionID`);
-- insert into invControlTowerResourcePurposes select * from dbo.invControlTowerResourcePurposes;
ALTER TABLE `invControlTowerResources` ADD FOREIGN KEY (`purpose`) REFERENCES `invControlTowerResourcePurposes` (`purpose`);

ALTER TABLE `invGroups` ADD FOREIGN KEY (`categoryID`) REFERENCES `invCategories` (`categoryID`);
-- ALTER TABLE `invGroups` ADD FOREIGN KEY (`graphicID`) REFERENCES `eveGraphics` (`graphicID`);
alter table invGroups modify iconID smallint;
ALTER TABLE `invGroups` ADD FOREIGN KEY (`iconID`) REFERENCES `eveIcons` (`iconID`);

ALTER TABLE `invMarketGroups` ADD FOREIGN KEY (`parentGroupID`) REFERENCES `invMarketGroups` (`marketGroupID`);
-- ALTER TABLE `invMarketGroups` ADD FOREIGN KEY (`graphicID`) REFERENCES `eveGraphics` (`graphicID`);
alter table invMarketGroups modify iconID smallint;
ALTER TABLE `invMarketGroups` ADD FOREIGN KEY (`iconID`) REFERENCES `eveIcons` (`iconID`);

-- ALTER TABLE `invMetaGroups` ADD FOREIGN KEY (`graphicID`) REFERENCES `eveGraphics` (`graphicID`);
alter table invMetaGroups modify iconID smallint;
ALTER TABLE `invMetaGroups` ADD FOREIGN KEY (`iconID`) REFERENCES `eveIcons` (`iconID`);

ALTER TABLE `invMetaTypes` ADD FOREIGN KEY (`typeID`) REFERENCES `invTypes` (`typeID`);
ALTER TABLE `invMetaTypes` ADD FOREIGN KEY (`parentTypeID`) REFERENCES `invTypes` (`typeID`);
ALTER TABLE `invMetaTypes` ADD FOREIGN KEY (`metaGroupID`) REFERENCES `invMetaGroups` (`metaGroupID`);

ALTER TABLE `invTypeMaterials` ADD FOREIGN KEY (`typeID`) REFERENCES `invTypes` (`typeID`);
ALTER TABLE `invTypeMaterials` ADD FOREIGN KEY (`materialTypeID`) REFERENCES `invTypes` (`typeID`);

ALTER TABLE `invTypeReactions` ADD FOREIGN KEY (`reactionTypeID`) REFERENCES `invTypes` (`typeID`);
ALTER TABLE `invTypeReactions` ADD FOREIGN KEY (`typeID`) REFERENCES `invTypes` (`typeID`);

ALTER TABLE `invTypes` ADD FOREIGN KEY (`groupID`) REFERENCES `invGroups` (`groupID`);
alter table invTypes modify graphicID smallint;
ALTER TABLE `invTypes` ADD FOREIGN KEY (`graphicID`) REFERENCES `eveGraphics` (`graphicID`);
ALTER TABLE `invTypes` ADD FOREIGN KEY (`raceID`) REFERENCES `chrRaces` (`raceID`);
ALTER TABLE `invTypes` ADD FOREIGN KEY (`marketGroupID`) REFERENCES `invMarketGroups` (`marketGroupID`);
alter table invTypes modify iconID smallint;
ALTER TABLE `invTypes` ADD FOREIGN KEY (`iconID`) REFERENCES `eveIcons` (`iconID`);

ALTER TABLE `mapCelestialStatistics` ADD FOREIGN KEY (`celestialID`) REFERENCES `mapDenormalize` (`itemID`);

alter table mapConstellations add unique key (`constellationID`, `regionID`);
ALTER TABLE `mapConstellationJumps` ADD FOREIGN KEY (`fromConstellationID`, `fromRegionID`) REFERENCES `mapConstellations` (`constellationID`, `regionID`);
ALTER TABLE `mapConstellationJumps` ADD FOREIGN KEY (`toConstellationID`, `toRegionID`) REFERENCES `mapConstellations` (`constellationID`, `regionID`);
ALTER TABLE `mapConstellationJumps` add foreign key (`toConstellationID`, `toRegionID`) REFERENCES `mapConstellationJumps` (`fromConstellationID`, `fromRegionID`);
ALTER TABLE `mapConstellationJumps` add foreign key (`fromConstellationID`, `fromRegionID`) REFERENCES `mapConstellationJumps` (`toConstellationID`, `toRegionID`);

ALTER TABLE `mapConstellations` ADD FOREIGN KEY (`regionID`) REFERENCES `mapRegions` (`regionID`);
ALTER TABLE `mapConstellations` ADD FOREIGN KEY (`factionID`) REFERENCES `chrFactions` (`factionID`);

ALTER TABLE `mapDenormalize` ADD FOREIGN KEY (`typeID`) REFERENCES `invTypes` (`typeID`);
ALTER TABLE `mapDenormalize` ADD FOREIGN KEY (`groupID`) REFERENCES `invGroups` (`groupID`);
ALTER TABLE `mapDenormalize` ADD FOREIGN KEY (`solarSystemID`) REFERENCES `mapSolarSystems` (`solarSystemID`);
ALTER TABLE `mapDenormalize` ADD FOREIGN KEY (`constellationID`) REFERENCES `mapConstellations` (`constellationID`);
ALTER TABLE `mapDenormalize` ADD FOREIGN KEY (`regionID`) REFERENCES `mapRegions` (`regionID`);
ALTER TABLE `mapDenormalize` ADD FOREIGN KEY (`orbitID`) REFERENCES `mapDenormalize` (`itemID`);

ALTER TABLE `mapJumps` ADD FOREIGN KEY (`stargateID`) REFERENCES `mapDenormalize` (`itemID`);
ALTER TABLE `mapJumps` ADD FOREIGN KEY (`celestialID`) REFERENCES `mapDenormalize` (`itemID`);

-- plenty of nulls in locationID
ALTER TABLE `mapLandmarks` ADD FOREIGN KEY (`locationID`) REFERENCES `mapSolarSystems` (`solarSystemID`);
-- ALTER TABLE `mapLandmarks` ADD FOREIGN KEY (`graphicID`) REFERENCES `eveGraphics` (`graphicID`);
alter table mapLandmarks modify iconID smallint;
ALTER TABLE `mapLandmarks` ADD FOREIGN KEY (`iconID`) REFERENCES `eveIcons` (`iconID`);

ALTER TABLE `mapLocationScenes` ADD FOREIGN KEY (`locationID`) REFERENCES `mapDenormalize` (`itemID`);

ALTER TABLE `mapLocationWormholeClasses` ADD FOREIGN KEY (`locationID`) REFERENCES `mapDenormalize` (`itemID`);

ALTER TABLE `mapRegionJumps` ADD FOREIGN KEY (`fromRegionID`) REFERENCES `mapRegions` (`regionID`);
ALTER TABLE `mapRegionJumps` ADD FOREIGN KEY (`toRegionID`) REFERENCES `mapRegions` (`regionID`);

ALTER TABLE `mapRegions` ADD FOREIGN KEY (`factionID`) REFERENCES `chrFactions` (`factionID`);


alter table mapSolarSystems add unique key (`solarSystemID`, `constellationID`, `regionID`);
ALTER TABLE `mapSolarSystemJumps` ADD FOREIGN KEY (`fromSolarSystemID`, `fromConstellationID`, `fromRegionID`) REFERENCES `mapSolarSystems` (`solarSystemID`, `constellationID`, `regionID`);
ALTER TABLE `mapSolarSystemJumps` ADD FOREIGN KEY (`toSolarSystemID`, `toConstellationID`, `toRegionID`) REFERENCES `mapSolarSystems` (`solarSystemID`, `constellationID`, `regionID`);
ALTER TABLE `mapSolarSystemJumps` add foreign key (`fromSolarSystemID`, `fromConstellationID`, `fromRegionID`) REFERENCES `mapSolarSystemJumps` (`toSolarSystemID`, `toConstellationID`, `toRegionID`);
ALTER TABLE `mapSolarSystemJumps` add foreign key (`toSolarSystemID`, `toConstellationID`, `toRegionID`) REFERENCES `mapSolarSystems` (`solarSystemID`, `constellationID`, `regionID`);

ALTER TABLE `mapSolarSystems` ADD FOREIGN KEY (`regionID`) REFERENCES `mapRegions` (`regionID`);
ALTER TABLE `mapSolarSystems` ADD FOREIGN KEY (`constellationID`) REFERENCES `mapConstellations` (`constellationID`);
ALTER TABLE `mapSolarSystems` ADD FOREIGN KEY (`factionID`) REFERENCES `chrFactions` (`factionID`);
ALTER TABLE `mapSolarSystems` ADD FOREIGN KEY (`sunTypeID`) REFERENCES `invTypes` (`typeID`);

ALTER TABLE `planetSchematicsPinMap` ADD FOREIGN KEY (`schematicID`) REFERENCES `planetSchematics` (`schematicID`);
ALTER TABLE `planetSchematicsPinMap` ADD FOREIGN KEY (`pinTypeID`) REFERENCES `invTypes` (`typeID`);

delete from planetSchematicsTypeMap where schematicID not in (select schematicID from planetSchematics);
ALTER TABLE `planetSchematicsTypeMap` ADD FOREIGN KEY (`schematicID`) REFERENCES `planetSchematics` (`schematicID`);
ALTER TABLE `planetSchematicsTypeMap` ADD FOREIGN KEY (`typeID`) REFERENCES `invTypes` (`typeID`);

ALTER TABLE `ramAssemblyLineStations` ADD FOREIGN KEY (`stationID`) REFERENCES `staStations` (`stationID`);
ALTER TABLE `ramAssemblyLineStations` ADD FOREIGN KEY (`assemblyLineTypeID`) REFERENCES `ramAssemblyLineTypes` (`assemblyLineTypeID`);
ALTER TABLE `ramAssemblyLineStations` ADD FOREIGN KEY (`stationTypeID`) REFERENCES `invTypes` (`typeID`);
ALTER TABLE `ramAssemblyLineStations` ADD FOREIGN KEY (`ownerID`) REFERENCES `crpNPCCorporations` (`corporationID`);
ALTER TABLE `ramAssemblyLineStations` ADD FOREIGN KEY (`solarSystemID`) REFERENCES `mapSolarSystems` (`solarSystemID`);
ALTER TABLE `ramAssemblyLineStations` ADD FOREIGN KEY (`regionID`) REFERENCES `mapRegions` (`regionID`);

ALTER TABLE `ramAssemblyLineTypeDetailPerCategory` ADD FOREIGN KEY (`assemblyLineTypeID`) REFERENCES `ramAssemblyLineTypes` (`assemblyLineTypeID`);
ALTER TABLE `ramAssemblyLineTypeDetailPerCategory` ADD FOREIGN KEY (`categoryID`) REFERENCES `invCategories` (`categoryID`);

ALTER TABLE `ramAssemblyLineTypeDetailPerGroup` ADD FOREIGN KEY (`assemblyLineTypeID`) REFERENCES `ramAssemblyLineTypes` (`assemblyLineTypeID`);
ALTER TABLE `ramAssemblyLineTypeDetailPerGroup` ADD FOREIGN KEY (`groupID`) REFERENCES `invGroups` (`groupID`);

ALTER TABLE `ramAssemblyLineTypes` ADD FOREIGN KEY (`activityID`) REFERENCES `ramActivities` (`activityID`);

ALTER TABLE `ramAssemblyLines` ADD FOREIGN KEY (`assemblyLineTypeID`) REFERENCES `ramAssemblyLineTypes` (`assemblyLineTypeID`);
ALTER TABLE `ramAssemblyLines` ADD FOREIGN KEY (`activityID`) REFERENCES `ramActivities` (`activityID`);
ALTER TABLE `ramAssemblyLines` ADD FOREIGN KEY (`ownerID`) REFERENCES `crpNPCCorporations` (`corporationID`);
ALTER TABLE `ramAssemblyLines` ADD FOREIGN KEY (`containerID`) REFERENCES `staStations` (`stationID`);

ALTER TABLE `ramInstallationTypeContents` ADD FOREIGN KEY (`assemblyLineTypeID`) REFERENCES `ramAssemblyLineTypes` (`assemblyLineTypeID`);
ALTER TABLE `ramInstallationTypeContents` ADD FOREIGN KEY (`installationTypeID`) REFERENCES `invTypes` (`typeID`);

ALTER TABLE `ramTypeRequirements` ADD FOREIGN KEY (`typeID`) REFERENCES `invTypes` (`typeID`);
ALTER TABLE `ramTypeRequirements` ADD FOREIGN KEY (`requiredTypeID`) REFERENCES `invTypes` (`typeID`);
ALTER TABLE `ramTypeRequirements` ADD FOREIGN KEY (`activityID`) REFERENCES `ramActivities` (`activityID`);

ALTER TABLE `staOperationServices` ADD FOREIGN KEY (`operationID`) REFERENCES `staOperations` (`operationID`);
ALTER TABLE `staOperationServices` ADD FOREIGN KEY (`serviceID`) REFERENCES `staServices` (`serviceID`);

ALTER TABLE `staOperations` ADD FOREIGN KEY (`activityID`) REFERENCES `crpActivities` (`activityID`);
ALTER TABLE `staOperations` ADD FOREIGN KEY (`caldariStationTypeID`) REFERENCES `staStationTypes` (`stationTypeID`);
ALTER TABLE `staOperations` ADD FOREIGN KEY (`minmatarStationTypeID`) REFERENCES `staStationTypes` (`stationTypeID`);
ALTER TABLE `staOperations` ADD FOREIGN KEY (`amarrStationTypeID`) REFERENCES `staStationTypes` (`stationTypeID`);
ALTER TABLE `staOperations` ADD FOREIGN KEY (`gallenteStationTypeID`) REFERENCES `staStationTypes` (`stationTypeID`);
ALTER TABLE `staOperations` ADD FOREIGN KEY (`joveStationTypeID`) REFERENCES `staStationTypes` (`stationTypeID`);

ALTER TABLE `staOperationServices` ADD FOREIGN KEY (`operationID`) REFERENCES `staOperations` (`operationID`);
ALTER TABLE `staOperationServices` ADD FOREIGN KEY (`serviceID`) REFERENCES `staServices` (`serviceID`);

ALTER TABLE `staStationTypes` ADD FOREIGN KEY (`stationTypeID`) REFERENCES `invTypes` (`typeID`);
-- ALTER TABLE `staStationTypes` ADD FOREIGN KEY (`dockingBayGraphicID`) REFERENCES `eveGraphics` (`graphicID`);
-- ALTER TABLE `staStationTypes` ADD FOREIGN KEY (`hangarGraphicID`) REFERENCES `eveGraphics` (`graphicID`);
ALTER TABLE `staStationTypes` ADD FOREIGN KEY (`operationID`) REFERENCES `staOperations` (`operationID`);

ALTER TABLE `staStations` ADD FOREIGN KEY (`operationID`) REFERENCES `staOperations` (`operationID`);
ALTER TABLE `staStations` ADD FOREIGN KEY (`stationTypeID`) REFERENCES `staStationTypes` (`stationTypeID`);
ALTER TABLE `staStations` ADD FOREIGN KEY (`corporationID`) REFERENCES `crpNPCCorporations` (`corporationID`);
ALTER TABLE `staStations` ADD FOREIGN KEY (`solarSystemID`, `constellationID`, `regionID`) REFERENCES `mapSolarSystems` (`solarSystemID`, `constellationID`, `regionID`);

ALTER TABLE `trnTranslations` ADD FOREIGN KEY (`tcID`) REFERENCES `trnTranslationColumns` (`tcID`);


