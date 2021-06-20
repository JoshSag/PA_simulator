# PA_simulator

## usage:
python -m main.py
see the output in out/
The column "construct id" in the "data.csv" file contains the sequential data. 

## Creating a scenario:
There are several command files under scenarios.  
A scenario file is a sequence of commands to simulate data.  
The main commands are add_logical_operations and generate_test.   
  
A text is a sequence of logical operations.  
Each logical operation has a "score". At the moment of text generation, we calculate the frequency of logical operation according to their score.  
You can add a random "anomaly" by adding a logical operation with a very low score. 

