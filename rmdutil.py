
# Warning: supports IPv4 only
class IpAddress:
    def __init__(self, ip_addr_str: str):
        ip_addr_bytes = ip_addr_str.split(".")
        self.__ip_addr_str = ip_addr_str
        self.__ip_addr_u32 = 0
        for i in range(4):
            byte_val = int(ip_addr_bytes[i])
            leftshift = 8 * (3 - i)
            self.__ip_addr_u32 |= byte_val << leftshift
    
    def to_string(self) -> str:
        return self.__ip_addr_str
    
    def to_int(self) -> int:
        return self.__ip_addr_u32
    
    def equal(self, opponent: "IpAddress") -> bool:
        return self.__ip_addr_u32 == opponent.__ip_addr_u32
    
    def similar(self, opponent: "IpAddress", masklen: int) -> bool:
        if (masklen <= 0):
            return True
        if (masklen >= 32):
            return self.equal(opponent)
        
        my_addr = self.__ip_addr_u32
        op_addr = opponent.__ip_addr_u32
        
        for i in range(masklen):
            bitmask = 0x80000000
            if ((my_addr & bitmask) != (op_addr & bitmask)):
                return False
            my_addr <<= 1
            op_addr <<= 1
        
        return True

def ask_user(question: str) -> bool:
    while True:
        user_input = input(question)
        user_input = user_input.lower()
        if (user_input == "n"):
            return False
        if (user_input == "y"):
            return True
        print("Input not recognized. Please enter again.")

def remove_duplicates(raw_data: list) -> list:
    entries = {}
    result_list = []
    for entry in raw_data:
        entries[entry] = None
    for unique_entry in list(entries.keys()):
        result_list.append(unique_entry)
    return result_list

def serialize_list(l: list, sep: str = ", ") -> str:
    return sep.join(remove_duplicates(l))

# combine some rows into one row
# @param rows is a 2-D table, where rows[rowIndex][columnIndex] == cell
# @return a single row, where row[columnIndex] == aggregated_cell
def merge_rows(rows: list, sep: str = ", ") -> list:
    if (len(rows) == 0):
        # rows is empty
        return rows
    
    # the number of columns in the first row decides how many columns the resulting table has
    column_count = len(rows[0])
    result_table = []
    
    # create a new dict for every column
    for i in range(column_count):
        result_table.append({})
    
    for row in rows:
        for i in range(column_count):
            cell_val = row[i]
            result_table[i].update({cell_val: None})
    
    result_row = []
    for i in range(column_count):
        column_aggregated_dict = result_table[i]
        # remove empty strings from the result table
        column_aggregated_dict.pop("", None)
        column_aggregated_list = list(column_aggregated_dict.keys())
        result_row.append(serialize_list(column_aggregated_list, sep))
    return result_row

# the maximum width we can give to one column to print to the screen
MAX_COLUMN_WIDTH = 80

def print_row(cells: list, column_widths: list, leftmost_border: str, sep_border: str, rightmost_border: str, single_sep_char: str = " "):
    leftmost = True
    for i in range(len(column_widths)):
        if leftmost:
            print(leftmost_border + single_sep_char, end="")
            leftmost = False
        else:
            print(sep_border + single_sep_char, end="")
        
        content = cells[i]
        width = column_widths[i]
        
        # remove '\r' characters
        content.replace("\r", "")
        
        # if content is multi-line, we only show the first line
        if (content.find("\n") != -1):
            content = content[0 : content.find("\n")] + "..."
        
        content_length = len(content)
        
        # cap width by MAX_COLUMN_WIDTH
        if (width > MAX_COLUMN_WIDTH):
            width = MAX_COLUMN_WIDTH
        
        # cap content_length by width
        if (content_length > width):
            content = content[0 : width - 3] + "..."
            content_length = len(content)
        
        print(content, end="")
        
        while (content_length < width):
            print(" ", end="")
            content_length += 1
        
        print(single_sep_char, end="")
    
    print(rightmost_border, end="")
    
    print("") # newline

def print_border_row(column_widths: list, leftmost_border: str, horizontal_unit_border: str, sep_border: str, rightmost_border: str):
    horizontal_borders = []
    for column_width in column_widths:
        horizontal_border = ""
        for i in range(column_width):
            horizontal_border += horizontal_unit_border
        horizontal_borders.append(horizontal_border)
    print_row(horizontal_borders, column_widths, leftmost_border, sep_border, rightmost_border, horizontal_unit_border)

# @param rows is a 2-D table, where rows[rowIndex][columnIndex] == cell
def print_table(header: list, rows: list):
    if (len(rows) == 0):
        #rows is empty
        return rows
    
    # the number of columns in the header decides how many columns the resulting table has
    column_count = len(header)
    column_widths = []
    
    # initialize the column widths with 0
    # the value will increase if any cell needs a wider column for display
    for i in range(column_count):
        column_widths.append(0)
    
    
    for i in range(column_count):
        cell_val = header[i]
        cell_val = cell_val.replace("\r", "")
        cell_width = len(cell_val)
        if (cell_val.find("\n") != -1):
            cell_val = cell_val[0 : cell_val.find("\n")] + "..."
            cell_width = len(cell_val)
        if (cell_width > MAX_COLUMN_WIDTH):
            cell_val = cell_val[0 : MAX_COLUMN_WIDTH - 3] + "..."
            cell_width = len(cell_val)
        
        if (cell_width > column_widths[i]):
            column_widths[i] = cell_width
    
    for row in rows:
        for i in range(column_count):
            cell_val = row[i]
            cell_val = cell_val.replace("\r", "")
            cell_width = len(cell_val)
            if (cell_val.find("\n") != -1):
                cell_val = cell_val[0 : cell_val.find("\n")] + "..."
                cell_width = len(cell_val)
            if (cell_width > MAX_COLUMN_WIDTH):
                cell_val = cell_val[0 : MAX_COLUMN_WIDTH - 3] + "..."
                cell_width = len(cell_val)
            
            if (cell_width > column_widths[i]):
                column_widths[i] = cell_width
    
    # print table top bar
    print_border_row(column_widths, "╔", "═", "╤", "╗")
    
    # print header
    print_row(header, column_widths, "║", "│", "║")
    
    first_row = True
    # print data
    for row in rows:
        if first_row:
            # print header and data horizontal separation bar
            print_border_row(column_widths, "╠", "═", "╪", "╣")
            first_row = False
        else:
            # print row horizontal separation bar
            print_border_row(column_widths, "╟", "─", "┼", "╢")
        
        # print row data
        print_row(row, column_widths, "║", "│", "║")
    
    # print table bottom bar
    print_border_row(column_widths, "╚", "═", "╧", "╝")

def demo():
    header = ["Date", "Host", "Name"]
    row1 = ["20250813", "192.168.11.250", "Java < 1.1"]
    row2 = ["20250813", "192.168.11.250", "Java < 1.2"]
    row3 = ["20250813", "192.168.11.250", "Java < 1.3"]
    row4 = ["20250813", "192.168.11.238", "Java < 5"]
    rows = [row1, row2, row3, row4]
    merged_row = merge_rows(rows)
    print(merged_row)
    print_table(header, rows)
    print_table(header, [merged_row])
    if (ask_user("Are you feeling well? [Y/n]: ")):
        print("Nice to hear that.")
    else:
        print("I'll send you to the hospital.")

if (__name__ == "__main__"):
    demo()