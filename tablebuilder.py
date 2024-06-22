import csv

class Table:
    def __init__(self, header=[], max_widths=[], delim=None, shorten=True, line_num=False, start_line_num=1, default_width=10, csvfile=None, csvfile_min_width=5, csvfile_max_width=10):
        self.header = header
        self.max_widths = max_widths
        self.delim = delim
        self.shorten = shorten
        self.line_num = line_num
        self.row_len = len(header)
        self.rows = []
        self.csvfile = csvfile
        self.start_line_num = int(start_line_num)
        self.line_counter = int(start_line_num)
        self.csvfile_min_width = csvfile_min_width
        self.csvfile_max_width = csvfile_max_width

        if csvfile:
            with open(self.csvfile, 'r') as file:
                csvreader = csv.reader(file)
                linecount = 0
                for row in csvreader:
                    if linecount == 0:
                        self.header = self.header + row
                        self.row_len = len(self.header)
                    else:
                        self.add_row(row)
                    linecount += 1
            self.max_widths = [csvfile_min_width for i in range(len(self.header))]

        if len(self.max_widths) == 0:
            self.max_widths = [default_width for i in range(len(self.header))]

        if self.line_num:
            self.header = ['#'] + self.header
            self.max_widths = [len(str(self.line_counter))] + self.max_widths

    def __adjust_max_widths(self):
        for row in self.rows:
            for i in range(self.row_len):
                if self.csvfile:
                    if len(str(row[i])) >= self.csvfile_max_width:
                        self.max_widths[i] = self.csvfile_max_width
                    elif len(str(row[i])) < self.csvfile_min_width:
                        self.max_widths[i] = self.csvfile_min_width
                    else:
                        self.max_widths[i] = len(str(row[i]))
                elif len(str(row[i])) > self.max_widths[i]:
                    self.max_widths[i] = len(str(row[i]))
        
    def __pad_string(self, s, width, pad_char=" "):
        l = len(str(s))
        if l > width and self.shorten and not self.delim:
            return str(s[0:width - 3]) + "..."
        elif l < width and (not self.delim):
            return str(s) + pad_char*(width - l)
        else:
            return str(s)

    def set_field_width(self, field_name, width):
        fields_list = []
        if isinstance(field_name, (int, float, str)):
            fields_list.append(field_name)
        elif isinstance(field_name, (list)):
            fields_list = field_name

        for f in fields_list:
            try:
                idx = self.header.index(f)
                self.max_widths[idx] = width
            except ValueError:
                continue

    def add_row(self, row):
        self.rows.append(row) if not self.line_num else self.rows.append([str(self.line_counter)] + row)
        self.line_counter += 1
        if self.line_num and len(str(self.line_counter)) > self.max_widths[0]:
            self.max_widths[0] = len(str(self.line_counter))
    
    def sort_rows(self, sort_by):
        sort_by_index = None
        for i in range(len(self.header)):
            if sort_by.lower == self.header[i].lower:
                sort_by_index = i
                break
        
        if sort_by_index:
            temp_dict = {}
            new_rows = []
            id = 0
            for r in self.rows:
                temp_dict[str(r[sort_by_index]) + "_" + str(id)] = r
                id += 1

            sorted_temp_dict = dict(sorted(temp_dict.items()))

            iter = 0
            for k,v in sorted_temp_dict.items():
                new_rows.append(v)
                if self.line_num: new_rows[iter][0] = iter + 1
                iter += 1

            self.rows = new_rows

    def print_table(self):
        if not self.delim and not self.shorten: self.__adjust_max_widths()
        if self.csvfile: self.__adjust_max_widths()
        
        d = self.delim if self.delim else " | "
        linebreak = "+" + "+".join(["-"*(self.max_widths[i]+2) for i in range(len(self.header))]) + "+"
        
        # print the headers
        h = d.join([self.__pad_string(self.header[i], self.max_widths[i]) for i in range(len(self.header))])
        if not self.delim: print (linebreak)
        print (h if self.delim else "| " + h + " |")
        if not self.delim: print (linebreak)
        
        # print the rows
        for row in self.rows:
            r = d.join([self.__pad_string(row[i], self.max_widths[i]) for i in range(len(row))])
            print (r if self.delim else "| " + r + " |")
        if not self.delim: print (linebreak)

    def print_csv_format(self, file=None):
        fd = open(file, 'w', newline='') if file else sys.stdout
        writer = csv.writer(fd)
        writer.writerow(self.header)
        for i in self.rows:
            writer.writerow(i)