from __future__ import print_function
from plenopticam.misc.type_checks import isfloat
import threading

class PlenopticamStatus(object):

    def __init__(self):

        # initialize member variables
        self._prog_var = 0
        self._stat_var = ''
        self._interrupt = threading.Event()
        self._error = False

        # observer lists to bind to
        self._prog_observers = []
        self._stat_observers = []
        self._interrupt_observers = []

    def progress(self, x, opt=False):

        if isfloat(x) and not self.interrupt:
            # only update if there is a significant (1.0%) change to prevent time-consuming re-prints
            curr_prog_var = round(x, 0)
            if curr_prog_var != self.prog_var:
                self.prog_var = int(round(x, 0))
                if x == 100:
                    self.prog_var = 'Finished'

            # console print (if option set)
            if opt:
                print('\r Progress: {:2.0f}%'.format(float(x)), end='')

                if x == 100:
                    print('\r Progress: Finished \n')
        elif self.interrupt:
            self.prog_var = ''
        elif x is None:
            self.prog_var = 'Processing ...'
        else:
            self.prog_var = str(x)

        return True

    def status_msg(self, msg='', opt=False):

        if not self.interrupt:
            self.stat_var = msg

            # reset progress bar
            self.progress(None, opt=False)

            # console print (if option set)
            if opt:
                print('\n', msg)
        else:
            self.stat_var = 'Stopped' if self._error is False else self.stat_var
            self.progress('', opt=False)

            return True

    def validate(self, checklist=None, msg=None):

        checklist = checklist if checklist is not None else list()

        for el in checklist:
            if el:
                return True

        # list elements are all "None" or empty
        self.status_msg('\r ' + msg, msg is not None)
        self.interrupt = True

        return False

    # event trigger on parameter change (according to observer pattern)
    @property
    def stat_var(self):
        return self._stat_var

    @stat_var.setter
    def stat_var(self, msg):
        self._stat_var = msg
        for callback in self._stat_observers:
           callback(self._stat_var)

    @property
    def prog_var(self):
        return self._prog_var

    @prog_var.setter
    def prog_var(self, val):
        self._prog_var = val
        for callback in self._prog_observers:
           callback(self._prog_var)

    def bind_to_prog(self, callback):
        self._prog_observers.append(callback)

    def bind_to_stat(self, callback):
        self._stat_observers.append(callback)

    # interrupt getter
    @property
    def interrupt(self):
        return self._interrupt.is_set()

    # interrupt change detection
    @interrupt.setter
    def interrupt(self, val):
        if val:

            # set interrupt
            self._interrupt.set()

            for callback in self._interrupt_observers:
                callback()

            # display stop message and reset progress bar
            self.status_msg()

        elif not val:
            # reset interrupt status
            self._interrupt.clear()

    def bind_to_interrupt(self, callback):
        self._interrupt_observers.append(callback)

    # error getter
    @property
    def error(self):
        return self._error

    # error setter
    @interrupt.setter
    def error(self, val):
        if val:
            self._error = True
            self.interrupt = True
        else:
            self._error = False
