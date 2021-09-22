import os, sys
try:
    from setproctitle import setproctitle
except ImportError:
    setproctitle = None

from . import daemon
import time
from .. import pathtool
from ..termcolor import tc
if os.name == "nt":
    import win32serviceutil

class Service:
    def __init__ (self, name, working_dir, lockpath = None, win32service = None):
        self.name = name
        self.working_dir = os.path.normpath (working_dir)
        self.lockpath = lockpath or working_dir
        self.win32service = win32service
        setproctitle and setproctitle (name)
        pathtool.mkdir (working_dir)
        if lockpath:
            pathtool.mkdir (lockpath)
        os.chdir (working_dir)

    def start (self):
        if os.name == "nt":
            self.set_service_config (['start'])
        else:
            from . import Daemonizer
            if not Daemonizer (self.working_dir, self.name, lockpath = self.lockpath).runAsDaemon ():
                pid = daemon.status (self.lockpath, self.name)
                print ("{} {}".format (tc.debug (self.name), tc.error ("[already running:{}]".format (pid))))
                sys.exit ()

    def stop (self):
        if os.name == "nt":
            self.set_service_config (['stop'])
        else:
            daemon.kill (self.lockpath, self.name, True)

    def status (self, verbose = True):
        pid = daemon.status (self.lockpath, self.name)
        if verbose:
            if pid:
                print ("{} {}".format (tc.debug (self.name), tc.warn ("[running:{}]".format (pid))))
            else:
                print ("{} {}".format (tc.debug (self.name), tc.secondary ("[stopped]")))
        return pid

    def execute (self, cmd, user = None, group = None):
        if cmd == "stop":
            self.stop ()
            return False
        elif cmd == "status":
            self.status ()
            return False
        elif cmd == "start":
            self.start ()
        elif cmd == "restart":
            self.stop ()
            time.sleep (2)
            self.start ()
        elif cmd == "install":
            self.install (user, group)
            return False
        elif cmd == "update":
            self.update (user, group)
            return False
        elif cmd == "remove":
            self.remove ()
            return False
        else:
            raise AssertionError ('unknown command: %s' % cmd)

        if os.name == "nt":
            return False
        return True

    if os.name == "nt":
        def set_service_config (self, argv = []):
            argv.insert (0, "")
            script = os.path.join (os.getcwd (), sys.argv [0])
            win32serviceutil.HandleCommandLine (self.win32service, "%s.%s" % (script [:-3], self.win32service.__name__), argv)

        def install (self, *args, **kargs):
            self.set_service_config (['--startup', 'auto', 'install'])

        def update (self, *args, **kargs):
            self.set_service_config (['update'])

        def remove (self):
            self.set_service_config (['remove'])

    else:
        def install (self, fallback_user, fallback_group, update = False):
            import pwd, grp

            name = self.name.split ('/')[-1]
            service_script = '/etc/systemd/system/{}.service'.format (name)
            if not update and os.path.exists (service_script):
                raise SystemError ('service {} is already exists. use update command'.format (name))

            if fallback_user:
                user = 'root'
                group = 'root'
            else:
                user = os.getenv("SUDO_USER") or os.getenv ("LOGNAME")
                if fallback_group:
                    group = fallback_group
                else:
                    pwnam = pwd.getpwnam(user)
                    group = grp.getgrgid (pwnam.pw_gid).gr_name

            args = sys.argv [1:]
            if args and hasattr (self, args [-1]):
                args = args [:-1]

            if self.name == 'skitai/smtpda':
                import skitai
                serve = os.path.join (os.path.dirname (skitai.__file__), 'scripts', 'commands', 'smtpda.py')
            else:
                serve = os.path.abspath (sys.argv [0])

            script = SERVICE_TEMPLATE.format (
                name = name.title (),
                user = user,
                group = group,
                executable = sys.executable,
                serve = serve,
                working_dir = self.working_dir,
                pidfile = name,
                args = " ".join (['"{}"'.format (each) for each in args]),
                sub_command = hasattr (sys, "sub_command") and sys.sub_command + ' ' or ''
            )

            print ('# {}.service =========================================\n'.format (name))
            print (script)
            print ('# end of {}.service ==================================\n'.format (name))

            try:
                with open (service_script, 'w') as f:
                    f.write (script)

            except PermissionError:
                service_script = os.path.join (os.getcwd (), '{}.service'.format (name))
                with open (service_script, 'w') as f:
                    f.write (script)
                os.system ('sudo mv {} /etc/systemd/system'.format (service_script))

            sudo = ''
            if os.getuid() != 0:
                sudo = 'sudo '
            os.system ("{}systemctl daemon-reload".format (sudo))
            os.system ("{}systemctl enable {}".format (sudo, name))

            print ("service {} installed, to start service,".format (name))
            print ("  sudo systemctl start {}".format (name))

        def update (self, fallback_user, fallback_group):
            self.install (fallback_user, fallback_group, True)

        def remove (self):
            name = self.name.split ('/')[-1]
            service_script = '/etc/systemd/system/{}.service'.format (name)
            if not os.path.exists (service_script):
                return
            os.remove (service_script)

    uninstall = remove

SERVICE_TEMPLATE = '''[Unit]
Description=Skitai {name} Service
After=syslog.target network.target

[Service]
Type=simple
WorkingDirectory={working_dir}
User={user}
Group={group}
StandardOutput=syslog
StandardError=syslog
Restart=on-failure
ExecStart={executable} {serve} {sub_command}{args}
ExecReload=/bin/kill -s HUP $MAINPID
RestartSec=2s
TimeoutStopSec=5
KillMode=mixed
Environment="DAEMONIZER=systemd"

[Install]
WantedBy=multi-user.target
'''

