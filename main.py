#!/usr/bin/env python3
import logging
import datetime
import time
import json
import os
import sys
import uuid
from classes import *

logDir = "logs"
backupDir = "backup"

# Check and setup logging
logFileName = (
    "logFile_"
    + datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d-%H_%M_%S")
    + ".txt"
)
if not os.path.exists(logDir):
    os.mkdir(logDir)
    msg = str("Directory {} Created").format(logDir)
    print(msg)
else:
    msg = str("Directory {} already exists").format(logDir)
    print(msg)

logFileStr = str("{}/{}").format(logDir, logFileName)
logFileStr = os.path.normpath(logFileStr)
logging.basicConfig(
    filename=logFileStr,
    format="%(asctime)s : %(levelname)s : %(funcName)s : %(message)s",
)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# Backup Directory
if not os.path.exists(backupDir):
    os.mkdir(backupDir)
    msg = str("Directory {} Created").format(backupDir)
    logger.debug(msg)
    print(msg)
else:
    msg = str("Directory {} already exists").format(backupDir)
    logger.debug(msg)


# Working vars
device_list_raw = []
deleted_list_raw = []
entity_list_raw = []
entity_original_names = set()
entity_device_ids = set()
device_names = set()
device_ids = set()

deviceFileName = "core.device_registry"
entityFileName = "core.entity_registry"

sourceFilePath = f"{os.getcwd()}"

deviceFilePath = os.path.normpath(f"{sourceFilePath}/{deviceFileName}")
entityFilePath = os.path.normpath(f"{sourceFilePath}/{entityFileName}")


def ClearAllData():
    """
    Cleans up data between runs
    """
    device_list_raw.clear()
    entity_list_raw.clear()
    entity_original_names.clear()
    device_names.clear()
    entity_device_ids.clear()
    device_ids.clear()


# Creates backups of the files
def BackupData(*args):
    """
    Creates backups of our original files on each run.
    """
    ident = str(uuid.uuid4())
    for arg in args:
        fileName = f"{arg}_{datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H_%M_%S')}-{ident[-12:]}"
        f_source = open(f"{sourceFilePath}/{arg}", "r")
        f_source_data = f_source.read()
        f_dest = open(f"{os.getcwd()}/{backupDir}/{fileName}", "w")
        f_dest.write(f_source_data)

        f_source.close()
        f_dest.close()


def GetDevices(deviceFile):
    """
    Reads in the `core.device_registry` file
    """
    f = open(deviceFile)
    raw = json.load(f)
    devices = raw["data"].get("devices", [])
    deleted = raw["data"].get("deleted_devices", [])
    for device in devices:
        device_list_raw.append(Device(**device))
        device_names.add(device.get("name", ""))
        device_ids.add(device.get("id", ""))

    # Right now we do nothing with it, but need the data to put it back.
    # May add our own 'deleted' stuff in the future.
    for device in deleted:
        deleted_list_raw.append(DeletedDevice(**device))

    f.close
    logger.debug("Device file import complete.")


def GetEntities(entityFile):
    """
    Reads in the `core.entity_registry` file
    """
    f = open(entityFile)
    raw = json.load(f)
    entities = raw["data"]["entities"]
    for entity in entities:
        entity_list_raw.append(Entity(**entity))
        entity_original_names.add(entity["original_name"])
        entity_device_ids.add(entity["device_id"])
    f.close

    logger.debug("Entity file import complete.")


def CountFromEntity(field, criteria):
    """
    Used to count various items out of the list of entity objects
    """
    i = 0
    if field == "original_name":
        try:
            for item in entity_list_raw:
                if criteria == item.original_name:
                    i += 1
        except AttributeError:
            pass
    elif field == "device_id":
        try:
            for item in entity_list_raw:
                if criteria == item.device_id:
                    i += 1
        except AttributeError:
            pass

    return i


def CountDeviceName(name):
    i = 0
    try:
        for item in device_list_raw:
            if name == item.name:
                i += 1
    except AttributeError:
        pass
    return i


def DisabledEnforcement(setValue, checkValue, enforce):
    """
    Used as a way to modularly enforce "disabled_by" field and limit accidental deletion.  Modify at own risk.
    """
    if enforce == True:
        if setValue == checkValue:
            return True
        else:
            return False
    else:
        return True


# Filter data
def FilterSelection(filterCriteria, nameList=None, filter=None):
    """
    Used to actually perform the search on lists and objects where we can filter results
    """
    for i in nameList:
        try:
            if filterCriteria == "device":
                item_count = CountDeviceName(i)
            if filterCriteria == "entity":
                item_count = CountFromEntity("original_name", i)
            if type(filter) == str:
                if filter not in i:
                    logger.debug(
                        f"Result '{i}' does not match String Filter: '{filter}'."
                    )
                    continue
            elif type(filter) == int:
                if item_count <= filter:
                    logger.debug(
                        f"Result '{i}' does not match Count Filter: '{item_count}'."
                    )
                    continue
            else:
                logger.debug("No filter")
            print(f"QTY:({item_count}): {i}")
        except TypeError:
            logger.error("Device name is empty!")


def ListSelection(nameList, filter, filter_t, typeList="device"):
    """
    Initial search function that calls the filters
    """
    int_filter = 0
    # Used to setup our User input
    if filter == None and filter_t == None:
        logger.debug("No filter.  Showing all")
        FilterSelection(typeList, nameList, filter)
    else:
        logger.debug(f"Filter set. Filter: {filter}")
        if filter_t == "string" and type(filter) == str:
            logger.debug("Filter set to String.")
            FilterSelection(typeList, nameList, filter)
        elif filter_t == "number":
            try:
                int_filter = int(filter)
                FilterSelection(typeList, nameList, int_filter)
            except (TypeError, ValueError):
                logger.error("Expecting a number to filter by.  Please try again")
        else:
            logger.error("Something happend..")
            logger.error(f"{filter} is {type(filter)}")


def CleanupDBForward(name_removal=None):
    """
    This cleans devices with a correlation of Device -> Entity.
    """
    logger.debug(f"Cleanup of {name_removal}")
    temp_entity_device_id = set()
    for idxd, device in enumerate(device_list_raw):
        logger.debug(f"Checking {device.id}")
        if name_removal is not None and device.name == name_removal:
            logger.debug(f"Cleaning by name: {name_removal}")
            for idxe, entity in enumerate(entity_list_raw):
                try:
                    if entity.device_id == device.id:
                        if DisabledEnforcement(entity.disabled_by, "user", True):
                            logger.debug(f"Removing Entity: '{entity.entity_id}'")
                            entity_list_raw[idxe] = "!DELETED!"
                except AttributeError:
                    logger.debug(
                        f"Entity {entity} is marked as Removed so has no attribue.  Moving on..."
                    )
                    pass
        elif name_removal == None:
            logger.debug("Cleaning all entites markes as 'disabled_by=user'")
            for idxe, entity in enumerate(entity_list_raw):
                try:
                    if entity.device_id == device.id:
                        if entity.disabled_by == "user":
                            logger.debug(f"Removing Entity: '{entity.entity_id}'")
                            entity_list_raw[idxe] = "!DELETED!"
                except AttributeError:
                    logger.debug(
                        f"Entity {entity} is marked as Removed so has no attribue.  Moving on..."
                    )
                    pass
        else:
            logger.debug("Name filter set but did not match, moving on.")

        # Rebuild list of device_id's from Entities
        temp_entity_device_id.clear()
        for entity in entity_list_raw:
            try:
                temp_entity_device_id.add(entity.device_id)
            except AttributeError:
                pass

        # If our device has no more entities, we remove it.
        if device.id not in temp_entity_device_id:
            logger.debug(
                f"No entites left; Removing Device: '{device.name}':'{device.id}'"
            )
            device_list_raw[idxd] = "!DELETED!"

    # Cleanup lists where the element is simply "!DELETED!"
    FinalCleanup()


def CleanupDBBackward(deviceName):
    """
    This cleans devices with a correlation of Entity -> Device
    This happens because some discarded devices might contain an entity of "original_name",
    but not contain any actual Device name.
    """
    logger.debug(f"Cleanup of {deviceName}")
    for idxe, entity in enumerate(entity_list_raw):
        try:
            logger.debug(f"Checking {entity.device_id}")
            if entity.original_name == deviceName and entity.disabled_by == "user":
                entityCount = CountFromEntity("device_id", entity.device_id)
                logger.debug(f"Working on {entity.device_id}")
                if entityCount < 2:
                    try:
                        for idxd, device in enumerate(device_list_raw):
                            if device.id == entity.device_id:
                                device_list_raw[idxd] == "!DELETED!"
                            else:
                                logger.debug(
                                    f"Device {device.id} not disabled. Skipping"
                                )
                    except AttributeError:
                        pass

                logger.info(
                    f"Removing Entity: {entity.original_name}':'{entity.entity_id}'"
                )
                entity_list_raw[idxe] = "!DELETED!"
        except AttributeError:
            pass

    FinalCleanup()


def FinalCleanup():
    """
    Purges all the remaining removed items from the list.
    Not the most optimal method, but works.
    """
    try:
        while True:
            device_list_raw.remove("!DELETED!")
    except ValueError:
        pass

    try:
        while True:
            entity_list_raw.remove("!DELETED!")
    except ValueError:
        pass


def WriteFile(filePath, data):
    """
    Writes a file to disk
    """
    with open(filePath, "w") as f:
        f.write(data)
        f.close()


def SetupDeviceOutput():
    """
    We tee-up the Device information to write back out to file.
    """
    logger.info("Setting up Device data for write...")

    deviceRaw = []
    deletedRaw = []
    for device in device_list_raw:
        deviceRaw.append(device.ToDict())

    for device in deleted_list_raw:
        deletedRaw.append(device.ToDict())

    deviceData = {}
    deviceData["version"] = 1
    deviceData["key"] = "core.device_registry"
    deviceData["data"] = {}
    deviceData["data"]["devices"] = deviceRaw
    deviceData["data"]["deleted_devices"] = deletedRaw
    return deviceData


def SetupEntityOutput():
    """
    We tee-up the Device information to write back out to file.
    """
    logger.info("Setting up Entity data for write...")

    entityRaw = []
    for device in entity_list_raw:
        entityRaw.append(device.ToDict())

    entityData = {}
    entityData["version"] = 1
    entityData["key"] = "core.entity_registry"
    entityData["data"] = {}
    entityData["data"]["entities"] = entityRaw
    return entityData


def WriteChanges():
    """
    Write our data back to file
    """
    logger.info("Setting up data...")
    data_d = SetupDeviceOutput()
    data_e = SetupEntityOutput()
    logger.info("Writing new data to file")
    WriteFile(deviceFilePath, json.dumps(data_d, indent=4))
    WriteFile(entityFilePath, json.dumps(data_e, indent=4))


# Remove data from device and entity file
def CleanDevice(deviceName):
    """
    Inform, confirm, execute the cleanup.
    """
    print(f"You selected '{deviceName}'")
    print(
        f"We will remove all disabled entities for '{deviceName}' and remove the device if no entities remain"
    )
    confirm = input("Enter 'Y' to confirm: ")
    try:
        if confirm.lower() == "y":
            print(f"Removing '{deviceName}'")
            BackupData(deviceFileName, entityFileName)
            CleanupDBForward(deviceName)
            CleanupDBBackward(deviceName)
            WriteChanges()
        else:
            print("Aboring delete.")
    except (TypeError, ValueError) as e:
        print("Invalid Selection")
        logger.error(e)


def LoadData():
    """
    Cleans up and loads the data.
    """
    ClearAllData()
    GetDevices(deviceFilePath)
    GetEntities(entityFilePath)


if __name__ == "__main__":

    while True:
        menu_string = """
        Please make a selection:
        (1) Devices: Show All
        (2) Devices: Search by Name
        (3) Devices: Search by Quantity
        (4) Entites: Show All
        (5) Clean Device by name
        (6) Repair devices DB
        (7) Exit\r\n
        """
        print(menu_string)
        searchSelection = input("Selection: ")
        if searchSelection == "1":
            LoadData()
            ListSelection(device_names, None, None)
        elif searchSelection == "2":
            LoadData()
            filterString = input("Please enter a search filter (string): ")
            ListSelection(device_names, filterString, "string")
        elif searchSelection == "3":
            LoadData()
            filterNumber = input("Show where greater than (number): ")
            ListSelection(device_names, filterNumber, "string")
        elif searchSelection == "4":
            LoadData()
            ListSelection(entity_original_names, None, None, typeList="entity")
        elif searchSelection == "5":
            LoadData()
            removalString = input("Enter name of device to Clean: ")
            CleanDevice(removalString)
        elif searchSelection == "6":
            LoadData()
            CleanDevice("None")
        elif searchSelection == "7":
            sys.exit(0)
        else:
            logger.info("Invalid selection.\r\n")
