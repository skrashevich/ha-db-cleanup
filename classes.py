from six import iteritems


class Device:
    """
    Device Attributes:
    config_entries (list)
    connections (list)
    identifiers (list)
    manufacturer (string)
    model (string)
    name (string)
    sw_version (string)
    entry_type (string)
    id (string)
    via_device_id (string)
    area_id (string)
    name_by_user (string)
    disabled_by (string)
    configuration_url (string)
    """

    def __iter__(self):
        for attr, value in iteritems(self.__dict__):
            yield attr, value

    def ToDict(self):
        return {key: value for (key, value) in self}

    def __init__(self, **args):
        self.config_entries = args["config_entries"] if args["config_entries"] else []
        self.connections = args["connections"] if args["connections"] else []
        self.identifiers = args["identifiers"] if args["identifiers"] else []
        self.manufacturer = args["manufacturer"] if args["manufacturer"] else None
        self.model = args["model"] if args["model"] else None
        self.name = args["name"] if args["name"] else None
        self.sw_version = args["sw_version"] if args["sw_version"] else None
        self.entry_type = args["entry_type"] if args["entry_type"] else None
        self.id = args["id"] if args["id"] else None
        self.via_device_id = args["via_device_id"] if args["via_device_id"] else None
        self.area_id = args["area_id"] if args["area_id"] else None
        self.name_by_user = args["name_by_user"] if args["name_by_user"] else None
        self.disabled_by = args["disabled_by"] if args["disabled_by"] else None
        self.configuration_url = (
            args["configuration_url"] if args["configuration_url"] else None
        )


class DeletedDevice:
    """
    DeletedDevice Attributes:
    config_entries (list)
    connections (list)
    identifiers (list)
    id (string)
    orphaned_timestamp (timestamp)
    """

    def __iter__(self):
        for attr, value in iteritems(self.__dict__):
            yield attr, value

    def ToDict(self):
        return {key: value for (key, value) in self}

    def __init__(self, **args):
        self.config_entries = args["config_entries"] if args["config_entries"] else []
        self.connections = args["connections"] if args["connections"] else []
        self.identifiers = args["identifiers"] if args["identifiers"] else []
        self.id = args["id"] if args["id"] else None
        self.orphaned_timestamp = (
            args["orphaned_timestamp"] if args["orphaned_timestamp"] else None
        )


class Entity:
    """
    Entity Attributes:
    entity_id (string)
    config_entry_id (string)
    device_id (string)
    area_id (string)
    unique_id (string)
    platform (string)
    name (string)
    icon (string)
    disabled_by (string)
    capabilities (dict)
    supported_features (int)
    device_class (string)
    unit_of_measurement (string)
    original_name (string)
    original_icon (string)
    entity_category (string)
    """

    def __iter__(self):
        for attr, value in iteritems(self.__dict__):
            yield attr, value

    def ToDict(self):
        return {key: value for (key, value) in self}

    def __init__(self, **args):
        self.entity_id = args["entity_id"] if ["entity_id"] else None
        self.config_entry_id = args["config_entry_id"] if ["config_entry_id"] else None
        self.device_id = args["device_id"] if ["device_id"] else None
        self.area_id = args["area_id"] if ["area_id"] else None
        self.unique_id = args["unique_id"] if ["unique_id"] else None
        self.platform = args["platform"] if ["platform"] else None
        self.name = args["name"] if ["name"] else None
        self.icon = args["icon"] if ["icon"] else None
        self.disabled_by = args["disabled_by"] if ["disabled_by"] else None
        self.capabilities = args["capabilities"] if ["capabilities"] else None
        self.supported_features = (
            args["supported_features"] if ["supported_features"] else None
        )
        self.device_class = args["device_class"] if ["device_class"] else None
        self.unit_of_measurement = (
            args["unit_of_measurement"] if ["unit_of_measurement"] else None
        )
        self.original_name = args["original_name"] if ["original_name"] else None
        self.original_icon = args["original_icon"] if ["original_icon"] else None
        self.entity_category = args["entity_category"] if ["entity_category"] else None
