# @file rm_csv_dup.py
# @brief Removes duplicated (and possibly duplicated entries) in a CSV file.
# @author David Choi <david.choi@pentastic.hk>
# @version 2025.08.13 15:31
PROGRAM_NAME = "rm_csv_dup.py"
PROGRAM_BRIEF = "Removes duplicated (and possibly duplicated entries) in a CSV file."
AUTHORS_STRING = "David Choi <david.choi@pentastic.hk>"
VERSION_STRING = "2025.08.13 15:31"

import platform # to obtain OS platform
import sys # to retrieve command line arguments
import os  # to handle file I/O operations
import csv # to read and write CSV files
import tempfile # to create temporary files
import shutil # to copy files
import xml.etree.ElementTree as ET # to read XML files

import rmdutil # import our own modules

# how to use: python3 rm_csv_dup.py ${src_csv_path} ${dest_csv_path}

IS_WINDOWS = (platform.system() == "Windows")

def print_help():
    print("")
    print("Command Line Interface - " + PROGRAM_NAME)
    print("")
    print("How to use:")
    print(">" if IS_WINDOWS else "$", "python3", "\"" + sys.argv[0] + "\"", "${src_csv_path} ${dest_csv_path}")
    if IS_WINDOWS:
        option_flags_usage = """
╔════════════════════╦═════════════╗
║ Option Flag(s)     ║ Usage       ║
╠════════════════════╬═════════════╣
║ -h or --help       ║ For Manual  ║
║ -v or --version    ║ For Version ║
╚════════════════════╩═════════════╝"""
    else:
        option_flags_usage = """
╭────────────────────┬─────────────╮
│ Option Flag(s)     │ Usage       │
├────────────────────┼─────────────┤
│ -h or --help       │ For Manual  │
│ -v or --version    │ For Version │
╰────────────────────┴─────────────╯"""
    print(option_flags_usage)
    print("")
    print("Param src_csv_path:")
    print("The path to the CSV file to be processed.")
    src_csv_path_example = "C:\\" if IS_WINDOWS else "/"
    src_csv_path_example += os.path.join("Users", "Dave CH", "Documents", "proj", "Pentast", "ness", "scan_results.csv")
    print("e.g. \"" + src_csv_path_example + "\"")
    print("")
    print("Param dest_csv_path:")
    print("The path to the CSV output file.")
    dest_csv_path_example = "C:\\" if IS_WINDOWS else "/"
    dest_csv_path_example += os.path.join("Users", "Dave CH", "Documents", "proj", "Pentast", "ness", "scan_results_no_dup.csv")
    print("e.g. \"" + dest_csv_path_example + "\"")
    print("")

# @return true if option flag is detected, false otherwise.
def check_option_flags():
    if (len(sys.argv) >= 2):
        arg = sys.argv[1]
        if (arg.startswith("-")):
            if (arg == "-v" or arg == "--version"):
                print("Script:  " + PROGRAM_NAME)
                print("Brief:   " + PROGRAM_BRIEF)
                print("Author:  " + AUTHORS_STRING)
                print("Version: " + VERSION_STRING)
            else:
                if not(arg == "-h" or arg == "--help"):
                    print("")
                    print("Option flag " + arg + " not recognized.")
                print_help()
            return True
    return False

# @param comparator_function The function (primary_key_str: str, row_key_str: str) -> bool, which returns true if both rows are mergable, false otherwise. The function is only called upon different rows.
def merge_by_column_with_comparator(header: list, raw_table: list, column_name: str, comparator_function) -> list:
    try:
        column_index = header.index(column_name)
    except ValueError:
        return raw_table
    
    # create result table to hold the results
    result_table = []
    
    primary_row_index = 0
    
    while len(raw_table) > primary_row_index:
        # the primary row will be used to find similar rows
        primary_row = raw_table[primary_row_index]
        primary_key_column_value = primary_row[column_index]
        
        # collects the rows similar to the primary row
        # note that primary_row is always collected to the similar_rows
        similar_rows = [primary_row]
        
        # scan all remaining rows in the raw table, starting from the row right after the primary row
        for i in range(primary_row_index + 1, len(raw_table)):
            row = raw_table[i]
            key_column_value = row[column_index]
            
            # compare both keys
            if (comparator_function(primary_key_column_value, key_column_value)):
                # this row is similar to the primary row
                # save this row to later ask the user to merge it or not
                similar_rows.append(row)
        
        if (len(similar_rows) == 0):
            pass # similar_rows should always include the primary row itself
        elif (len(similar_rows) == 1):
            # this row is very unique: only this row itself is similar to itself
            # no need to ask the user for merging permission then
            # because we aren't actually merging anything
            # skip using this row as primary row for future scans
            primary_row_index += 1
        else:
            # get the rows to be merged
            rows_to_be_merged = similar_rows
            
            print("\n\n")
            
            # prints the table before merging
            rmdutil.print_table(header, rows_to_be_merged)
            
            print("\n\n/\\ Table BEFORE merging. /\\")
            print("")
            print("\\/ Table AFTER merging. \\/\n\n")
            
            # generates a merged row for preview only
            merged_row = rmdutil.merge_rows(rows_to_be_merged)
            
            # creates a table with only the merged row
            # only for easier printing to the console
            merged_table = [merged_row]
            
            # prints the table after merging
            rmdutil.print_table(header, merged_table)
            
            # ask the user for merging permission
            user_wants_to_merge = rmdutil.ask_user("Do you want to merge? [Y/n]: ")
            
            if (user_wants_to_merge):
                # remove all the similar rows from the raw table
                #for similar_row in similar_rows:
                #    raw_table.remove(similar_row)
                raw_table = [row for row in raw_table if row not in similar_rows]
                
                # add the merged row to the result table
                result_table.append(merged_row)
            else:
                # don't do the merge
                print("This merge is cancelled.")
                
                # skip using this row as primary row for future scans
                primary_row_index += 1
    
    # move the remaining "very unique" rows to the result table
    while (len(raw_table) > 0):
        result_table.append(raw_table.pop(0))
    
    return result_table

def merge_by_column_with_matching_pair(header: list, raw_table: list, column_name: str, ignore_case: bool, words_matching_pair: tuple) -> list:
    
    def matching_pair_comparator(primary_key_str: str, row_key_str: str) -> bool:
        if (primary_key_str == ""):
            # we should not merge 2 rows when both of their key columns are empty...
            return False
        
        if (ignore_case):
            # convert key value to lowercase for compare without case
            primary_key_str = primary_key_str.lower()
            row_key_str = row_key_str.lower()
        
        KEY_SPLITTER = " "
        # key words
        primary_key_words = primary_key_str.split(KEY_SPLITTER)
        primary_key_words_count = len(primary_key_words)
        
        # beginning words matching count
        beginning_words_matching_count = words_matching_pair[0]
        # cap it to the length of primary key words
        if (beginning_words_matching_count > primary_key_words_count):
            beginning_words_matching_count = primary_key_words_count
        
        # ending words matching count
        ending_words_matching_count = words_matching_pair[1]
        # cap it to the length of primary key words
        if (ending_words_matching_count > primary_key_words_count):
            ending_words_matching_count = primary_key_words_count
        
        # get the beginning and ending of the primary key string to be matched with the row key string
        begin_str = KEY_SPLITTER.join(primary_key_words[0 : beginning_words_matching_count])
        end_str = KEY_SPLITTER.join(primary_key_words[primary_key_words_count - ending_words_matching_count : primary_key_words_count])
        
        return row_key_str.startswith(begin_str) and row_key_str.endswith(end_str)
    
    return merge_by_column_with_comparator(header, raw_table, column_name, matching_pair_comparator)

def merge_by_column(header: list, raw_table: list, column_name: str, ignore_case: bool = True) -> list:
    try:
        column_index = header.index(column_name)
    except ValueError:
        return raw_table
    
    # the number of words to be matched at the begin and end of both keys
    words_matching_pairs = [(3, 3), (3, 2), (2, 3), (2, 2), (3, 1), (1, 3), (3, 0), (0, 3), (2, 1), (1, 2), (2, 0), (0, 2), (1, 0), (0, 1)]
    
    for words_matching_pair in words_matching_pairs:
        raw_table = merge_by_column_with_matching_pair(header, raw_table, column_name, ignore_case, words_matching_pair)
    
    return raw_table

def rm_dup(src_csv_path: str, dest_csv_path: str):
    ENCODING = "utf-8"
    
    # opens a temporary destination file
    with tempfile.NamedTemporaryFile(mode='w+t', encoding=ENCODING, newline='', delete=False) as temp_file:
        # creates a CSV writer
        csv_writer = csv.writer(temp_file)
        
        # parses the source CSV file
        with open(src_csv_path, 'r', encoding=ENCODING) as src_csv_file:
            # creates a CSV reader
            csv_reader = csv.reader(src_csv_file)
            
            # reads the header
            header = next(csv_reader)
            
            # copies the header
            csv_writer.writerow(header)
            
            # use the keys of a dictionary to remove complete duplicates
            rows = {}
            
            for row in csv_reader:
                row_tuple = tuple(row)
                rows[row_tuple] = None
            
            unique_rows = []
            for tup in list(rows.keys()):
                unique_row = list(tup)
                unique_rows.append(unique_row)
            
            unique_rows = merge_by_column(header, unique_rows, "Name")
            unique_rows = merge_by_column(header, unique_rows, "Solution")
            
            for unique_row in unique_rows:
                # copies this row to the destination CSV file
                csv_writer.writerow(unique_row)
    
    # copy the temp file to the destination CSV file
    shutil.copyfile(temp_file.name, dest_csv_path)
    
    # delete the temp file
    os.remove(temp_file.name)

def main():
    # the working directory is the default source dir
    src_dir_path = "."
    
    if (check_option_flags()):
        return
    
    if (len(sys.argv) < 3):
        print_help()
        return
    
    # user passed designated source folder from command line
    src_csv_path = sys.argv[1]
    # removes double-quotes at beginning and end of src_csv_path
    if (src_csv_path.startswith("\"")):
        src_csv_path = src_csv_path[1]
    if (src_csv_path.endswith("\"")):
        src_csv_path = src_csv_path[0 : len(src_csv_path) - 1]
    if (not os.path.exists(src_csv_path)):
        print("Error: src_csv_path = \"" + src_csv_path + "\" does not exist.")
        return
    if (not os.path.isfile(src_csv_path)):
        print("Error: src_csv_path = \"" + src_csv_path + "\" is not a file.")
        return
    if (not src_csv_path.lower().endswith(".csv")):
        print("Error: src_csv_path = \"" + src_csv_path + "\" is not a CSV file.")
        return
    
    # user passed destination CSV file path from command line
    dest_csv_path = sys.argv[2]
    # removes double-quotes at beginning and end of dest_csv_path
    if (dest_csv_path.startswith("\"")):
        dest_csv_path = dest_csv_path[1]
    if (dest_csv_path.endswith("\"")):
        dest_csv_path = dest_csv_path[0 : len(dest_csv_path) - 1]
    dest_csv_dir_path = os.path.dirname(dest_csv_path)
    if (dest_csv_dir_path != ""):
        if (not os.path.exists(dest_csv_dir_path)):
            print("Error: dest_csv_path is under \"" + dest_csv_dir_path + "\", which does not exist.")
            return
        if (not os.path.isdir(dest_csv_dir_path)):
            print("Error: dest_csv_path is under \"" + dest_csv_dir_path + "\", which is not a directory.")
            return
    if (not dest_csv_path.lower().endswith(".csv")):
        print("Error: dest_csv_path = \"" + dest_csv_path + "\" does not ends with \".csv\".")
        return
    if (os.path.exists(dest_csv_path)):
        if (os.path.isdir(dest_csv_path)):
            print("Error: dest_csv_path = \"" + dest_csv_path + "\" already exists as a directory.")
            return
        elif (os.path.isfile(dest_csv_path)):
            if (os.path.samefile(src_csv_path, dest_csv_path)):
                print("Error: src_csv_path and dest_csv_path cannot be the same file.")
                return
            else:
                print("Warning: dest_csv_path = \"" + dest_csv_path + "\" already exists.")
                while (True):
                    isOverwrite = input("Are you sure you want to overwrite this file? [y/N]: ")
                    isOverwrite = isOverwrite.lower()
                    if (isOverwrite == "n"):
                        print("Program is exiting, no changes are made.")
                        return
                    if (isOverwrite == "y"):
                        print("User requested to overwrite this file.  Program continues.")
                        break
                    print("Input not recognized. Please enter again.")
        else:
            print("Error: dest_csv_path = \"" + dest_csv_path + "\" already exists.")
            return
    
    rm_dup(src_csv_path, dest_csv_path)

if __name__ == "__main__":
    main()