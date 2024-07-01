#!/usr/bin/env python
""" Helper functions for batch analysis programs running in python.
    It is always useful to have something to pick up a config file and
    parse it, or to have a -not system level- logging object at hand.
    A simplified plotting command is also included.

    Author:     Tomio
    Date:       2011. Sept. -
    Warranty:   None
    License:    MIT
"""
from matplotlib import pyplot as pl
#pl.ion()
import os

#Pickle is getting difficult on complex dicts... (as of 2016)
#python3 has no cPickle anymore
try:
    from cPickle import dump
except ImportError:
    from pickle import dump

from time import time, ctime

__all__=[ "ReadConf", "Report", "ReadTable", "SaveData", "DumpData", "Plot",\
        "colortext"]

################################################################
class Report:
    def __init__(self, pathname="./", filename="report.rep",\
                sep=" ", timesep="\t", add_time=True,\
                header="Report file is opened"):
        """ Initialize and open the report, add the header info
            and go on.

            This is a report object, which deals with writing into
            the report file, adding time stamps etc.

            fp:         holds the file pointer
            timesep:    a separator between the time stamp and text
            add_time:   add a time stamp to each line
            sep:        separator to bind list elements to a text
            pathname:   of the report file
            filename:   name of the report file

            parameters
            pathname, filename: file path
            sep:            set the separator (default is space)
            timesep:        set the time separator
            add_time:       bool
            header:         first line to dump when opening the report file
        """
        self.header = header
        self.fp = None
        self.add_time = add_time
        self.timesep = timesep
        self.sep = sep

        self.pathname = pathname
        self.filename = filename

        self.open()
    #end __init__

    def open(self):
        """ Open the log file, and add the header """

        if not os.path.isdir(self.pathname):
            print("Invalid pathname, falling back to local dir")

        self.fp = open(os.path.join(self.pathname, self.filename),"at")

        if len(self.header) > 0:
            self.write(self.header, withtime=True)

        self.fp.write("\n\n")

    #end open

    def opened(self):
        if self.fp != None:
            return self.fp.opened
        else :
            return False
    #end of opened

    def close(self):
        """ close the file """
        self.fp.write("\n\n")
        self.fp.close()
    #end close

    def write(self, *args, withtime=False, color= ''):
        """ Dump a list of text into the report file,
            separated by the specified separator (report.sep)
            If txtlist is a list, generate a text string,
            if it is a string, just write it out.

            parameters:
            *args:      content to print / dump
            withtime:   force a timestamp if add_time is not set
            color:      text color for the print, based onf colortext

            Return:
                there is no return value
        """

        if self.fp == None or self.fp.closed:
            self.open()


        if self.add_time or withtime:
            timetxt = f'{ctime()}:'
            args = ('',timetxt)+args

        strarray = [str(i) for i in args]

        res = ' '.join(strarray)
        print(colortext(res, color=color))
        self.fp.write(res)
        self.fp.write('\n')
        self.fp.flush()
    #end of write
#end class Report

def ReadConf(filename,
             default={},
             simplify= False,
             strict= False,
             verbose=False):
    """ A simple config parser.
        Takes a text file, where each line contains a definition
        '#' is a remark sign: anything behind it is ignored
        Leading and trailing white spaces are stripped.

        If there is a = sign, then the first word of the left side
        is a key, the right side is a value, which is added to a list.
        Otherwise the whole line is used as a key, value is 'Unknown'

        If a key is found multiple times, the list of values is appended.

        Parameters:
        filename:   file to read
        default:    is a list, which values must be present if
                    not found in the config file
                    The syntax of default is not tested!
        simplify:   if set, keep only the last element of the lists, and
                    remove the lists
        strict:     Boolean. If set, only single elment lists are converted
                    to single elements in simplify. Else everything gets
                    converted.
        verbose:    dump the resulted dict to the screen

        Returns a dict of definitions.
    """
    res = dict()

    if os.path.isfile(filename):
        fp = open(filename, 'rt')

        alltxt = fp.readlines()
        fp.close()

        #now the fun: analyze the text line-by-line
        #each line is one unit
        #each line starts with a key word, which is separated by =


        for i in alltxt:
            #drop leading and trailing white chars...
            # this is still python 2.7 compatible:
            # i = (i.strip()).rstrip()
            i = i.strip()

            #deal with remarks, cut them off
            if '#' in i:
                i = i.split('#', 1)[0]

            if '=' in i:
                txt = i.split('=', 1)
                #remove trailing whitespaces:
                key = txt[0].rstrip()
                val = txt[1].split('"')[1] if '\"' in txt[1] \
                                            else txt[1].strip()
                #val = txt[1].split()[0]

                #text or number?
                #isdigit is not reliable
                if val.lower() == 'false':
                    val = False;
                elif val.lower() == 'true':
                    val = True;
                else:
                    try:
                        val = float(val)
                    except ValueError:
                        pass

                if key in res:
                    res[key].append(val)
                else:
                    #do not accept empty key:
                    if key != "":
                        res[key] = [val]
                #end if
            else:
                if i != "":
                    res[i] = [1]
            #end if =
        #end for

    else :
        print("Config file does not exists")
        #return default

    #make sure the default is included:
    #if default does not conform to the limitations above,
    #that is up to the user...
    for i in default.keys():
        if not i in res:

            if type(default[i]) != list:
                res[i] = [default[i]]
            else:
                res[i] = default[i]

    if simplify:
        if strict:
            # only simplify those having one value
            for k,v in res.items():
                if len(v) == 1:
                    res[k] = v[0]
        else:
            res = {k:v[-1] for k,v in res.items()}

    if verbose:
        a = res.keys()
        a.sort()
        for i in a:
            print(i,":",res[i])

    return res
#end ReadConf

def ReadTable(filename, sep="", cols=[], keys=[], DefaultValue=0.0):
    """ take a filename and import a table from it.
        The routine reads a tabulated text file and returns only
        the required columns from it. If the columns do not exist,
        returns an empty array.

        Parameters:
        filename:       the path of the file. If not found,
                        None is returned
        sep:            separator to be used (passed to the string
                        split as a parameter)

        cols:           a list indicating the columns (0,...) to be
                        picked if empty, all data is returned
        keys:           use these keys instead of numbers in the
                        returned keys
        DefaultValue:   what to put in the place of an empty entry
                        (separator is there, but no value is given)

        return:
        A dict containing keys of the column indices,
        and lists of data as values

        The routine skips missing data points, thus either use n/a
        in the text file, or you may get some misalignement in the
        tables. Shorter columns are no problem.
    """
    if os.path.isfile(filename):
        fp = open(filename, "rt")
    else:
        print( "File not found: %s" %filename)
        return None
    #end if

    txtlist = fp.readlines()
    fp.close()

    #start the loading/numerical conversion
    res = []
    for t in txtlist:
        resline = []
        t = t.strip()
        if '#' in t:
            t = t.split('#',1)[0]

        if t == "":
            #print( "Empty line, skipping")
            continue

        #split up the remaining line:
        ilist = t.split(sep) if sep != "" else t.split()

        for i in ilist:
            if i == "":
                resline.append(DefaultValue)
            else:
                try :
                    n = float(i)
                except ValueError:
                    resline.append(i)
                else:
                    resline.append(n)
            #end if i==""
        #end for i
        res.append(resline)
    #end for

    #now get the desired columns:
    if cols == []:
        # range is now an iterator, list makes it a list
        cols = list(range(len(res[0])))

    #fast way would be using zip(*res), but
    #if one column is shorter, it drops that one
    #the slow and solid way is: go through as much
    #as you can. If a point is missing, skip it
    #broken tables is the user's responsibility
    N = len(cols)

    if len(keys) == 0:
        keys = cols
    elif len(keys) < N:
        keys.extend(cols[len(keys):])

    retres = {}
    for j in range(N):
        jc = cols[j]
        k = keys[j]

        c = []
        for i in res:
            try:
                #we take the ones specified in cols:
                c.append(i[jc])
            except:
                pass
            #end try
        #end for i
        #add the next key to the dict:
        retres[k] = c
    #end j

    return retres
#end of ReadTable

def SaveData( header, data, filename, remark='', append= False, report=None):
    """ Dump a data set (list of lists) to a tabulated text file

        Parameters:
        header:     a list of headers: this many columns should be
                    in the text file
        data:       a list of lists: containing lists of the rows
        filename:   name of output. If 'table' is not included, then
                    it is appended to the filename. Extension is forced
                    to .txt

        remark:     any text to add
        append:     if True, append to end
        report:     dump a report using a report object and on screen
    """

    fn, ext = os.path.splitext(filename)

    if "table" not in fn:
        fn = "%s-table.txt" %fn
    else:
        fn = "%s.txt" %fn
    #end if

    mode = 'wt' if append == False else 'at'
    fp = open(fn, mode, encoding='UTF-8')

    fp.write('#')
    fp.write(remark)
    fp.write('\n#\n')

    # txt = '\t'.join(map(repr,header))
    txt = '\t'.join([str(i) for i in header])
    fp.write('#')
    fp.write(txt)
    fp.write('\n')

    for l in data:
        # txt = '\t'.join(map(repr, l))
        txt = '\t'.join([str(i) for i in l])
        fp.write(txt)
        fp.write('\n')
    #end for

    fp.close()
    if report != None:
        report.write("Saving data to", fn)
        report.write("Remark:", remark)
#end SaveData


def DumpData(data, filename, report=None):
    """ use pickle to dump a file. If the file exists, it is
        overwriten!

        It tries to make sure the extension is .dat.

        Parameters:
        data:       object to be dumped
        filename:   target filename (with path)
        report:     a report object to dump information
    """

    #Cut the extension, and put it back
    fn, ext = os.path.splitext(filename)
    fn = "%s.dat" %fn

    #do the dumping:
    try:
        fp = open(fn, 'wb')

    except IOError:
        print("Unable to open output file!")
        return

    else:
        dump(data, fp, 2)
        fp.close()

    if report != None:
        report.write("Data dumped to:", fn)
#end of DumpData


def Plot( x, y, xerr=[], yerr=[],
        fN= 1, fmt="+",
        markersize=8, alpha= 1.0,
        xlim = [], ylim=[],
        xlabel='', ylabel='',
        title='', dpi= 150,
        log= '', ext=".png", filename='',
        outpath='./', newplot= True,
        legend= [],
        **args):
    """ Generalized plot function using matplotlib
        It is meant as a simple interface to all kinds of
        matplotlib functionality, such as log and lin scale,
        and saving the plot as well.

        Parameters:
        x,y             the data set to be plotted
        xerr, yerr:     if present then errorbars to be added
        fN:             figure number (1-10)
        fmt:            format text, typical 'r+' or similar
        markersize:     the size of the symbol, default is 8 points
        xlim, ylim      a list of [min, max] to set the axis limits;
        xlabel, ylabel: axis labels, with LaTeX type math is possible
        title:          plot title (if specified)
        dpi:            if filename specified, the resolution of the exported
                        image
        log:            a string specifying which axis to set to log-scale
                        if set to '-', force linear scale on both axis
        ext:            extension of the output
        filename:       if not empty, then save the plot into this file
                        if loplot specified, then loglog has to be in the
                        filename, or is appended
        outpath:        path of the output
        legend:         a list of strings to be added to legend
        newplot:        erase the plot before plotting, or just add the
                        data to an existing figure

        any further named arguments are passed to plot() or errorbar().
        For now, do not change figure until you are done with the current one.
    """

    if len(x) != len(y):
        print("X and Y lenght differ!")
        return
    #end if

    #figure(1) is the default
    if fN < 1 or fN > 10:
        fN = 1

    fig1 = pl.figure(fN)
    #global plt1

    #for a new plot:
    if newplot:
        pl.clf()
        plt1 = pl.subplot(1,1,1)
    else:
        # get back the subplot:
        plt1 = fig1.get_axes()[0]

    if xlim != []:
        if len(xlim) == 2:
            plt1.set_xlim(xlim)
    #end if xlim

    if ylim != []:
        if len(ylim) == 2:
            plt1.set_ylim(ylim)
    #end if xlim

    if log == '-':
        plt1.set_xscale('linear')
        plt1.set_yscale('linear')
    elif log != '':
        if 'x' in log:
            plt1.set_xscale('log')
        if 'y' in log:
            plt1.set_yscale('log')


    if len(y) > 0:
        if len(xerr) == 0 or len(yerr)== 0:
            plt1.plot(x,y, fmt,\
                markersize=markersize, alpha= alpha, **args)

        else:
            plt1.errorbar(x,y, yerr, xerr, fmt=fmt,\
                markersize=markersize, alpha= alpha, **args)
    #do not plot anything for empty data
    #we still can export the figure though 8)

    #label the axis:
    if xlabel != "":
        plt1.set_xlabel( xlabel )
    if ylabel != "":
        plt1.set_ylabel( ylabel )

    if title != "":
        plt1.set_title( title )


    if legend != []:
        pl.legend(legend)

    if filename != "":
        if log != ''  and "log" not in filename:
            filename = "%s-log" %filename
        #end if logplot

        fn,oldext = os.path.splitext(filename)
        #the filename may contain '.' and not an extension
        #do  a crude test:
        if len(oldext) != 3:
            fn = filename

        if "." in ext:
            fn = "%s%s" %(fn, ext)
        else:
            fn = "%s.%s" %(fn, ext)
        #end if ext
        print('saving file', fn)
        pl.savefig( os.path.join(outpath, fn), dpi=dpi,
                bbox_inches= 'tight',
                pad_inches= 0)
    #end if filename
    pl.draw()

#end of Plot

def colortext(txt, color='cyan', reset=True):
    """ convert a text string to colored text using ANSI terminal
        escape characters.
        Possible colors:
        bold, underline, blink, invert, conceald, strike, grey30, grey40,
        grey65, grey70, bggrey20, bggrey33, bggrey80, bggrey93, darkred,
        red, bgdarkred, bgred, darkyellow,yellow, bgyellow, bglightyellow,
        darkblue, blue, bgdarkblue, bgblue, darkmagenta, purple, bgmagenta,
        bglightpurple, darkcyan, cyan, bgcyan, bgcyan, darkgreen, green,
        bggreen, bglightgreen.
        'bg' meaning background, bold, underline, ... are stiles.

        reset:  if set, add the reseting sequence to the end.

        return: converted text

        Many thanks to 'unutbu' at stackoverflow:
        http://stackoverflow.com/questions/3696430/print-colorful-string-out-to-console-with-python

    """
    Colors={ 'reset':0,  # RESET COLOR
    'bold':1,
    'underline':4,
    'blink':5,
    'invert':7,
    'conceald':8,
    'strike':9,
    'grey30':90,
    'grey40':2,
    'grey65':37,
    'grey70':97,
    'bggrey20':40,
    'bggrey33':100,
    'bggrey80':47,
    'bggrey93':107,
    'darkred':31,
    'red':91,
    'bgdarkred':41,
    'bgred':101,
    'darkyellow':33,
    'yellow':93,
    'bgyellow':43,
    'bglightyellow':103,
    'darkblue':34,
    'blue':94,
    'bgdarkblue':44,
    'bgblue':104,
    'darkmagenta':35,
    'purple':95,
    'bgmagenta':45,
    'bglightpurple':105,
    'darkcyan':36,
    'cyan':96,
    'bgcyan':46,
    'bgcyan':106,
    'darkgreen':32,
    'green':92,
    'bggreen':42,
    'bglightgreen':102,
    'black':30    }

    if color in Colors:
        txt = "\33[%sm%s" %(Colors[color],txt)
        if reset:
            txt = "%s\33[%sm" %(txt, Colors['reset'])


    return txt
#end colortext
