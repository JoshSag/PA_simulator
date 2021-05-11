import Simulator
import Parser
import pandas as pd
import time
import os
import shutil

def time_wrapper(func, msg, end = " "):
    def w_func(*args, **kargs):
        b = time.time()
        res = func(*args, **kargs)
        e = time.time()
        print("<{} {}>".format(msg, round(e-b,3)) , end = end)
        return res
    return w_func

class Executer():
    def __init__(self):
        self.simulator = Simulator.Simulator()

    def execute_commands(self, commands):
        """
        :param commands: a list of commands objects
        :return: execute all commands via simulator
        """
        assert type(commands) is list
        assert all([isinstance(command, Parser.Command) for command in commands])
        print("executing {} commands".format(len(commands)))

        for command in commands:
            command.execute(simulator = self.simulator)

    def execute_from_file(self, filepath):
        parser = Parser.Parser()
        parser.read_file(filepath)
        commands = parser.get_commands()
        self.execute_commands(commands)

    @staticmethod
    def execute(filepath_in, dirout):

        executer = __class__()
        executer.execute_from_file(filepath_in)

        os.makedirs(dirout,exist_ok=True)
        shutil.copy(filepath_in, os.path.join(dirout, "simulation.txt"))

        Data.make(simulator=executer.simulator,
                  dirout=dirout)
Executer.execute = time_wrapper(Executer.execute,  msg = "Exec")

class Data():
    def __init__(self, simulator):
        self.text_entries = simulator.get_text_entries()
        self.histogram = simulator.get_histogram()
        self._set_df()

    def _set_df(self):
        if len(self.text_entries) == 0:
            return pd.DataFrame([])

        locations = list()
        dfs = list()
        for text_entry in self.text_entries:
            size = text_entry["size"]
            cur_df = pd.DataFrame(index=range(size)) # setting size to duplicate user_id and session_id
            cur_df["ACCESS_ID"] = text_entry["user_id"]
            cur_df["SESSION_ID"] = text_entry["session_id"]
            cur_df["CONSTRUCT_ID"] = pd.Series(text_entry["text"], dtype=str)

            dfs.append(cur_df)

            locations.append(text_entry["locations_full"])

        df = pd.concat(dfs, ignore_index=True)
        df = df[["ACCESS_ID", "SESSION_ID", "CONSTRUCT_ID"]]
        df = __class__._add_fake_columns(df)
        self.df = df

        self.df_locations = pd.concat(locations, ignore_index=True)
        self.df_locations["text_index"] = self.df_locations.index

    @staticmethod
    def _add_fake_columns(df):
        datetime_format = "%Y-%m-%d %H:%M:%S"
        gen_time = lambda i: time.strftime(datetime_format, time.localtime(time.time() + i))
        gen_full_sql_id = lambda i : i
        gen_unix_timestamp = lambda i : "unix_timestamp{}".format(i)

        def series(gen_function, n, dtype):
            return pd.Series([gen_function(i) for i in range(n)], dtype = dtype)

        df["TIMESTAMP"] = series(gen_time, len(df), dtype=str)
        df["full_sql_id"] = series(gen_full_sql_id, len(df), dtype=int)
        df["unix_timestamp"] = series(gen_unix_timestamp, len(df), dtype=str)
        df["RECORD_TYPE"] = "PA"
        df["tenant_id"] = "1"
        df["config_id"] = "2"
        df["global_id"] = "3"
        df["full_sql"] = "4"

        # adjust columns order
        columns = ["RECORD_TYPE","SESSION_ID","CONSTRUCT_ID","TIMESTAMP","full_sql_id","unix_timestamp","ACCESS_ID","tenant_id","config_id","global_id","full_sql"]
        df = df[columns]
        return df

    def write(self, dirout):
        print("writing data ({} lines) to directory {}".format(len(self.df), dirout))
        os.makedirs(dirout, exist_ok=True)

        self.df.to_csv(          os.path.join(dirout, "data.csv"), index=False,header=False)
        self.df_locations.to_csv(os.path.join(dirout, "info.csv".format(dirout)))
        self.histogram.to_csv(   os.path.join(dirout, "hist.csv".format(dirout)))

    @staticmethod
    def make(simulator, dirout):
        data_obj = __class__(simulator=simulator)
        data_obj.write(dirout=dirout)
        # print(data_obj.df)