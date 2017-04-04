from sys import exit
from thread import start_new_thread

from winappdbg import win32, Debug, HexDump, Crash, thread
from threading import Thread

import radamsa_proxy

try:
    from winappdbg import CrashDAO
except ImportError:
    raise ImportError("Error: SQLAlchemy is not installed!")
_server_flag = False

def my_event_handler( event ):

    # Get the event name.
    name = event.get_event_name()

    # Get the event code.
    code = event.get_event_code()

    # Get the process ID where the event occured.
    pid = event.get_pid()

    # Get the thread ID where the event occured.
    tid = event.get_tid()

    # Get the value of EIP at the thread.
    pc = event.get_thread().get_pc()

    # Show something to the user.
    bits = event.get_process().get_bits()
    format_string = "%s (%s) at address %s, process %d, thread %d"
    message = format_string % ( name,
                                HexDump.integer(code, bits),
                                HexDump.address(pc, bits),
                                pid,
                                tid )
    print message

    # If the event is a crash...
    if code == win32.EXCEPTION_DEBUG_EVENT and event.is_last_chance():
        print "Crash detected, storing crash dump in database..."

        # Generate a minimal crash dump.
        crash = Crash( event )
        if (_server_flag):
            print "Crash_data_start"
            print radamsa_proxy.crash_data
            print "Crash_data_end"

        # You can turn it into a full crash dump (recommended).
        crash.fetch_extra_data( event, takeMemorySnapshot = 2 ) # no memory dump
        # crash.fetch_extra_data( event, takeMemorySnapshot = 1 ) # small memory dump
        # crash.fetch_extra_data( event, takeMemorySnapshot = 2 ) # full memory dump

        # Connect to the database. You can use any URL supported by SQLAlchemy.
        # For more details see the reference documentation.
        dao = CrashDAO( "sqlite:///crashes.sqlite" )
        #dao = CrashDAO( "mysql+MySQLdb://root:toor@localhost/crashes" )

        # Store the crash dump in the database.
        dao.add( crash )

        # If you do this instead, heuristics are used to detect duplicated
        # crashes so they aren't added to the database.
        # dao.add( crash, allow_duplicates = False )

        # You can also launch the interactive debugger from here. Try it! :)
        # event.debug.interactive()

        # Kill the process.
        event.get_process().kill()

def simple_debugger( argv="" ):
    print radamsa_proxy.crash_data

    # Instance a Debug object, passing it the event handler callback.
    debug = Debug( my_event_handler, bKillOnExit = True )
    try:

        # Start a new process for debugging.
        debug.system.scan_processes()
        for (process, name) in debug.system.find_processes_by_filename(path_exe):
            _pid = process.get_pid()

        debug.attach(int(_pid))

        # Wait for the debugee to finish.
        debug.loop()


    # Stop the debugger.
    finally:
        debug.stop()

#def simple_server():
# When invoked from the command line,
# the first argument is an executable file,
# and the remaining arguments are passed to the newly created process.
if __name__ == "__main__":
    import sys

    if (_server_flag):
        th = start_new_thread(radamsa_proxy.main, ())
    simple_debugger()
