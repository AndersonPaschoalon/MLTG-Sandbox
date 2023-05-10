import os
import sqlite3
import argparse
import traceback
from prettytable import PrettyTable
from Utils import Utils
from Database.RandomData import RandomData
from Database.TraceDatabase import TraceDatabase
from Plotter import Plotter


#
# Constants
#
TRACE_DATABASE = "db/TraceDatabase.db"
PLOT_MAIN_DIR = "plots"
VERSION_STRING = """
trace-plot.py
License        MIT
Author         Anderson Paschoalon 
Version        0.0.0.1
"""
VALID_COLORS = [
    'blue',
    'green',
    'red',
    'cyan',
    'magenta',
    'yellow',
    'black',
    'tab:blue',
    'tab:orange',
    'tab:green',
    'tab:red',
    'tab:purple',
    'tab:brown',
    'tab:pink',
    'tab:gray',
    'tab:olive',
    'tab:cyan',
    'xkcd:azure',
    'xkcd:beige',
    'xkcd:black',
    'xkcd:blue',
    'xkcd:brown',
    'xkcd:coral',
    'xkcd:cyan',
    'xkcd:gold',
    'xkcd:green',
    'xkcd:grey',
    'xkcd:lavender',
    'xkcd:light blue',
    'xkcd:light green',
    'xkcd:orange',
    'xkcd:pink',
    'xkcd:purple',
    'xkcd:red',
    'xkcd:salmon',
    'xkcd:teal',
    'xkcd:white',
    'xkcd:yellow'
]

def show_version():
    print(VERSION_STRING)
    return 0


def list_trace_database():
    ret_val = 0
    try:
        # connect to the database
        conn = sqlite3.connect(TRACE_DATABASE)
        # create a cursor object
        cur = conn.cursor()
        # execute a SELECT query to fetch all rows from the Trace table
        cur.execute('SELECT * FROM Trace')
        # fetch all rows as a list of tuples
        rows = cur.fetchall()
        # create a PrettyTable object to display the data as a table
        table = PrettyTable(['ID', 'Trace Name', 'Trace Source', 'Trace Type', 'Comment', 'nPackets', 'nFlows', 'Duration'])
        # add rows to the table
        for row in rows:
            table.add_row(row)
        # print the table
        print(table)
        # close the cursor and connection
        cur.close()
        conn.close()
    except Exception as e:
        traceback.print_exc()
        print(f"Message: {str(e)}")
        ret_val = -1

    return ret_val


def clean_trace_name_list(list_trace_names, database_file):
    # Open a connection to the database file
    conn = sqlite3.connect(database_file)
    c = conn.cursor()

    # Query the Trace table to get a list of valid trace names
    c.execute("SELECT traceName FROM Trace")
    valid_trace_names = [row[0] for row in c.fetchall()]

    # Check each trace name in the input list and keep only the valid ones
    clean_trace_names = []
    for trace_name in list_trace_names:
        if trace_name in valid_trace_names:
            clean_trace_names.append(trace_name)
        else:
            print(f"Warning: Trace name '{trace_name}' not found in the database.")

    # Close the database connection and return the list of valid trace names
    conn.close()
    return clean_trace_names


def valid_flow_databases(clean_trace_names):
    valid_flow_dbs = []
    for trace_name in clean_trace_names:
        flow_db_file = f"db/{trace_name}_Flow.db"

        if os.path.isfile(flow_db_file):
            valid_flow_dbs.append(flow_db_file)
        else:
            print(f"Warning: Flow database '{flow_db_file}' not found.")
    return valid_flow_dbs


def execute_analysis(list_trace_names, output_dir, nickname):
    clean_trace_names = clean_trace_name_list(list_trace_names, TRACE_DATABASE)
    if len(clean_trace_names) == 0:
        print("**ERROR** No valid traceName was provided. Use --list to show all valid traceNames.")
        return -3
    valid_flow_dbs = valid_flow_databases(clean_trace_names)
    if len(clean_trace_names):
        print("**ERROR** no valid flow database was found.")
        return -4
    flow_databases_objs = []
    i = 0
    for database_file in valid_flow_dbs:
        if len(VALID_COLORS) >= i:
            print("Warning: no more colors available, the remaining traces will be ignored.")
            break
        fdb = TraceDatabase(database_file, VALID_COLORS[i])
        flow_databases_objs.append(fdb)
        i += 1
    Plotter.plot_all_stable(plot_data_list=flow_databases_objs, out_dir=output_dir, nickname=nickname)
    return 0


def execute_test_analysis(output_dir, nickname):
    # APENAS COLAR AQUI O CONTEUDO DO SCRIPT DE TESTES
    print("TODO")
    return 0


def main():
    # Create argument parser object
    parser = argparse.ArgumentParser(description="trace-plot.py is a script to help execute a set of analysis to " + \
    "compare the stochastics similarities between traces captured by the sniffer, and stored in the TraceDatabase.")

    parser.add_argument('-l', '--list', action='store_true', help='List the contents of the TraceDatabase.')
    parser.add_argument('-p', '--plot', nargs='+', type=str, help='Execute the analysis  in the listed traceNames.The traces should be specified in a csv format. If, instead of a list of trace names, ou use the keywork test, it will execute the analyssis with some random data to check if everithing is working fine.')
    parser.add_argument('-o', '--out', nargs='+', type=str, help='The name of the output folder the plots will be stored. This directory will be created inside plots directory.')
    parser.add_argument('-v', '--version', action='store_true',  help='Show the trace-plot.py version.')

    # Parse arguments
    args = parser.parse_args()

    # Store arguments in variables
    version_flag = args.version
    list_flag = args.list
    trace_names = ""
    out_dir_name = ""
    if args.plot is not None:
        trace_names = args.plot[0]
    if args.out is not None:
        out_dir_name = args.out[0]

    ret_val = 0
    if version_flag:
        ret_val = show_version()
    elif list_flag:
        ret_val = list_trace_database()
    elif trace_names is None or out_dir_name is None or trace_names == "" or out_dir_name == "":
        if trace_names is None or trace_names == "":
            print("**ERROR** you must provide the list of trace names to execute the analysis. Use --list to show the available nammes.")
        else:
            print("**ERROR** you must provide the output directory to execute the analysis.")
        ret_val = -1
    else:
        Utils.mkdir(PLOT_MAIN_DIR)
        out_path = os.path.join(PLOT_MAIN_DIR, out_dir_name)
        if os.path.exists(out_path):
            print(f"**ERROR** output path {out_path} already exists. Use another --out parameter, or delete manually the folder {out_path}.")
            ret_val = -2
        elif trace_names == "test":
            print("Executing the analysis with random data...")
            print(f"Output directory: {out_path}")
            ret_val = execute_test_analysis(output_dir=out_path, nickname=out_dir_name)
        else:

            list_trace_names = trace_names.split(",")
            print(f"Executing analysis on the following traces: {list_trace_names}")
            print(f"Output directory: {out_path}")
            ret_val = execute_analysis(list_trace_names=list_trace_names, output_dir=out_path, nickname=out_dir_name)
    return ret_val


if __name__ == '__main__':
    main()
