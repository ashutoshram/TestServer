from .. import pathtool, logger
import os, signal
import time, sys
import tempfile

class ExitNow (Exception):
    pass

class DaemonClass:
    NAME = None
    def __init__ (self, logpath, varpath, consol):        
        assert self.NAME, "Daemon NAME is not defined"
        self.logpath = logpath
        self.varpath = varpath
        self.consol = consol        
        self.active = True
        self._signal_bound = False
        
        logpath and pathtool.mkdir (logpath)
        varpath and pathtool.mkdir (varpath)
            
        if not self.consol: # service mode
            sys.stderr = open (os.path.join (varpath, "stderr.log"), "a")
        self.make_logger ()
        self.setup ()
    
    def log (self, msg, type = "info", name = ""):
        self.logger (msg, type, name)
    
    def trace (self, name = ""):
        self.logger.trace (name or self.NAME)    

    def newfile (self, name, mode = 'w'):
        if name is None:
            name = next (tempfile._get_candidate_names ())
        return open (os.path.join (self.varpath, name), mode)

    def make_logger (self):        
        self.logger = logger.multi_logger ()
        if self.consol:
            self.logger.add_logger (logger.screen_logger ())
        if self.logpath:
            self.logger.add_logger (logger.rotate_logger (self.logpath, self.NAME, "weekly"))
            self.log ("{} log path: {}".format (self.NAME, self.logpath), "info")        
        self.log ("{} tmp path: {}".format (self.NAME, self.varpath), "info")
            
    def bind_signal (self, term = None, hup = None):
        def hTERM (signum, frame):
            self.shutdown (signum)
        
        if term is None:
            term = hTERM
        if hup is None:
            hup = hTERM
        
        if os.name == "nt":
            signal.signal(signal.SIGBREAK, term)
        else:    
            def hUSR1 (signum, frame):    
                self.logger.rotate ()
            signal.signal(signal.SIGUSR1, hUSR1)
            term and signal.signal(signal.SIGTERM, term)            
            term and signal.signal(signal.SIGINT, term)
            hup and signal.signal(signal.SIGHUP, hup)
        self._signal_bound = True
    
    def start (self):
        self.log ("service %s started" % self.NAME)
        if not self._signal_bound:
            self.bind_signal ()

        try:
            self.run ()
        except (ExitNow, KeyboardInterrupt):
            pass
        except:
            self.trace ()            
        self.close ()

    # overridable methods -------------------------------------------------
    def close (self):
        self.log ("service %s stopped" % self.NAME)

    def setup (self):
        pass
    
    def shutdown (self, signum):
        # default signal handler
        self.log ("got signal {}".format (signum))        
        self.active = False

    def run (self):
        while self.active:
            raise NotImplementedError
    
def make_service (service_class, logpath, varpath, consol, *args, **kargs):
    pathtool.mkdir (varpath)
    if logpath:
        pathtool.mkdir (logpath)
    return service_class (logpath, varpath, consol, *args, **kargs)
