import datetime
import csv
from glob import glob
import os
from tools import _number_or_string

def read_parameters(parameters_file='simulation_parameters.csv', delimiter='\t', quotechar='"'):
    """ reads a parameter file line by line and gives a list. Where each line
    contains all parameters for a particular run of the simulation.

    Args:

        parameters_file (optional):
            filename of the csv file. (default:`simulation_parameters.csv`)

        delimiter (optional):
            delimiter of the csv file. (default: tabs)

        quotechar (optional):
            for single entries that contain the delimiter. (default: ")
            See python csv lib http://docs.python.org/library/csv.html


    This code reads the file and runs a simulation for every line::

     for parameter in read_parameters('simulation_parameters.csv'):
        w = Simulation(parameter)
        w.build_agents(Agent, 'agent', 'num_agents')
        w.run()
    """
    start_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    parameter_array = []

    csvfile = open(parameters_file)
    dialect = csv.Sniffer().sniff(csvfile.read(1024))
    csvfile.seek(0)
    reader = csv.reader(csvfile, dialect)

    keys = [key.lower() for key in reader.next()]
    for line in reader:
        if line == []:
            continue
        cells = [_number_or_string(cell.lower()) for cell in line]
        parameter = dict(zip(keys, cells))
        if 'num_rounds' not in keys:
            raise SystemExit('No "num_rounds" column in ' + parameters_file)
        if 'name' not in parameter:
            try:
                parameter['name'] = parameter['Name']
            except KeyError:
                print("no 'name' (lowercase) column in " + parameters_file)
                parameter['name'] = 'abce'
        parameter['name'] = str(parameter['name']).strip("""\"""").strip("""\'""")
        try:
            if parameter['random_seed'] == 0:
                parameter['random_seed'] = None
        except KeyError:
            parameter['random_seed'] = None
        parameter['_path'] = os.path.abspath('./result/' + parameter['name'] + '_' + start_time)
        try:
            os.makedirs('./result/')
        except OSError:
            pass
        try:
            os.makedirs(parameter['_path'])
        except OSError:
            files = glob(parameter['_path'] + '/*')
            for f in files:
                os.remove(f)
        for key in parameter:
            if key == '' or key[0] == '#' or key[0] == '_':
                del key
        parameter_array.append(parameter)
    return parameter_array
    #TODO put the initialisation in the init so that it can eat a dict
