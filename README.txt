Helper functions for working with batch analysis programs in python. This is
NOT functions of DOS or BASH.

Instead, here are some functions to easier read a configuration text file,
resulting a configuration dict structure, one can use to tune a script. A
Plot() in matplotlib to integrate some functionality into one command, makind
the script simpler lookging, some tools to save data tables (text) and binary
pickle files easier, and a simple reporting facility, but not so complex as a
system log would be.

It is also python3 compatible

As of 0.9e, it is only python 3 compatible.
2022-03-25: Change to setuptools from distutils.

ver 0.11:
The report writing is not like print, taking every argument to be printed, except
the color= to define text color on the terminal.

The ReadConf now has an option to strip the configuration variables from
lists to their last values. This is good when no lists are needed.

I have ensured that the SaveData can also append ignoring the header if
the file exists but writing it if not. And moved as much as possible to use
the with... statement for file handling.
