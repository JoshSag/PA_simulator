import Simulator

class Command():
    def __init__(self, cmd):
        self.cmd = cmd
        self._validate()
        self._parse()

    @staticmethod
    def _class_operation():
        pass

    def _validate(self):
        """
        validates that cmd is indeed belong to this specific class
        """
        assert type(self.cmd) is dict
        assert self.cmd.keys() == {"operation","data"}
        assert self.cmd["operation"] == self._class_operation()

    def _parse(self):
        pass

    def execute(self, simulator):
        pass

class command_ADD_USER(Command):
    @staticmethod
    def _class_operation():
        return "add_user"
    def _validate(self):
        super()._validate()

        assert self.cmd["data"].keys() == {"user_id"}

    def _parse(self):
        data = self.cmd["data"]
        self.user_id = data["user_id"]

    def execute(self, simulator):
        simulator.add_user(self.user_id)

class command_SET_USER_SESSION(Command):
    @staticmethod
    def _class_operation():
        return "set_session"

    def _validate(self):
        super()._validate()
        assert self.cmd["data"].keys() == {"user_id", "session_id"}

    def _parse(self):
        data = self.cmd["data"]
        self.user_id = data["user_id"]
        self.session_id = data["session_id"]
    def execute(self, simulator):
        simulator.set_session(user_id = self.user_id,
                                   session_id=self.session_id)

class command_ADD_LOGICAL_OPERATION(Command):
    @staticmethod
    def _class_operation():
        return "add_logical_operation"

    def _validate(self):
        super()._validate()
        data = self.cmd["data"]
        assert data.keys() == {"user_id", "logical_operation", "score"}
        assert type(data["logical_operation"]) is tuple
        assert type(data["score"]) is float

    def _parse(self):
        data = self.cmd["data"]
        self.user_id = data["user_id"]
        self.logical_operation= tuple(data["logical_operation"])
        self.score = float(data["score"])

    def execute(self, simulator):
        simulator.add_logical_opration_to_user(user_id = self.user_id,
                                               logical_operation=self.logical_operation,
                                               score=self.score)

class command_ADD_LOGICAL_OPERATIONS(Command):
    @staticmethod
    def _class_operation():
        return "add_logical_operations"

    def _validate(self):
        super()._validate()
        data = self.cmd["data"]
        assert data.keys() == {"user_id", "logical_operations", "score"}
        assert type(data["logical_operations"]) is list # list of tuples, one tuple for one logical operation
        assert all(type(lo) is tuple for lo in data["logical_operations"])
        assert type(data["score"]) is float

    def _parse(self):
        data = self.cmd["data"]
        self.user_id = data["user_id"]
        self.logical_operations = list(data["logical_operations"])
        self.logical_operations = [tuple(l) for l in self.logical_operations]
        self.score = float(data["score"])

    def execute(self, simulator):
        for logical_operation in self.logical_operations:
            simulator.add_logical_opration_to_user(user_id = self.user_id,
                                                   logical_operation=logical_operation,
                                                   score=self.score)

class command_DELETE_LOGICAL_OPERATION(Command):
    @staticmethod
    def _class_operation():
        return "delete_logical_operation"

    def _validate(self):
        super()._validate()

        data = self.cmd["data"]
        assert data.keys() == {"user_id", "logical_operation"}
        assert type(data["logical_operation"]) is tuple

    def _parse(self):
        data = self.cmd["data"]
        self.user_id = data["user_id"]
        self.logical_operation = data["logical_operation"]

    def execute(self, simulator):
        simulator.del_logical_operation_from_user(user_id=self.user_id,
                                                  logical_operation=self.logical_operation)

class command_DELETE_LOGICAL_OPERATIONS(Command):
    @staticmethod
    def _class_operation():
        return "delete_logical_operations"

    def _validate(self):
        super()._validate()

        data = self.cmd["data"]
        assert data.keys() == {"user_id", "logical_operations"}
        assert type(data["logical_operations"]) is list # list of tuples, one tuple for one logical operation
        assert all(type(lo) is tuple for lo in data["logical_operations"])

    def _parse(self):
        data = self.cmd["data"]
        self.user_id = data["user_id"]
        self.logical_operations = list(data["logical_operations"])
        self.logical_operations = [tuple(l) for l in self.logical_operations]

    def execute(self, simulator):
        for logical_operation in self.logical_operations:
            simulator.del_logical_operation_from_user(user_id=self.user_id,
                                                      logical_operation=logical_operation)

class command_GENERATE_TEXT_FOR_USER(Command):
    @staticmethod
    def _class_operation():
        return "generate_text"
    def _validate(self):
        super()._validate()

        data = self.cmd["data"]
        assert data.keys() == {"user_id", "text_size"}

    def _parse(self):
        data = self.cmd["data"]
        self.user_id = data["user_id"]
        self.text_size_logical_operations = data["text_size"]

    def execute(self, simulator):
        simulator.generate_text_for_user(user_id=self.user_id,
                                         text_size_logical_operations=self.text_size_logical_operations)

class Parser():
    def __init__(self):
        # map operation field to a command object
        commands_objects = [command_ADD_USER,
                            command_SET_USER_SESSION,
                            command_ADD_LOGICAL_OPERATION,
                            command_ADD_LOGICAL_OPERATIONS,
                            command_DELETE_LOGICAL_OPERATION,
                            command_DELETE_LOGICAL_OPERATIONS,
                            command_GENERATE_TEXT_FOR_USER
                            ]
        self.handlers = {command_obj._class_operation() : command_obj \
                    for command_obj in commands_objects}

        self.commands = list()

        # import pprint
        # pprint.pprint(self.handlers)

    def parse(self, command_dict):
        # print(command_dict)
        assert type(command_dict) is dict
        assert "operation" in command_dict.keys()
        assert command_dict["operation"] in self.handlers.keys()

        command_obj = self.handlers[command_dict["operation"]]
        command = command_obj(command_dict)
        self.commands.append(command)

    def read_file(self, filepath):
        print("reading commands from file: ", filepath)
        content_str = open(filepath).read()
        content_str = content_str.replace("\n","")
        content = eval(content_str)
        for command_dict in content:
            self.parse(command_dict)

    def get_commands(self):
        return self.commands