
import os
import Executer
if __name__ == "__main__":

    root_dirout = r"out"
    dirin_scenarios = "scenarios"
    
    exclude = []
    include = ["s1","s2","s3","s4"]
    scenarios = os.listdir(dirin_scenarios)
    scenarios = [s for s in scenarios if s not in exclude]
    scenarios = [s for s in scenarios if s in include]

    for scenario_name in scenarios:
        print(scenario_name)
    
        dirout = os.path.join(root_dirout, "case_{}".format(scenario_name))
        Executer.Executer.execute(filepath_in=os.path.join(dirin_scenarios, scenario_name),
                                  dirout=dirout)
        print()
