import fabric
import paramiko
from . import commands
import os
from stat import S_ISDIR, S_ISREG

class SFTP:
    def __init__ (self, host, user, password = None, key_file = None, port = 22):
        self._host = host
        self._user = user
        self._port = port
        self._key_file = key_file
        self._password = password
        self._ssh, self._sftp = None, None

    def __getattr__ (self, attr):
        return getattr (self._sftp, attr)

    def __enter__ (self):
        self._ssh = paramiko.SSHClient ()
        self._ssh.set_missing_host_key_policy (paramiko.AutoAddPolicy())
        self._ssh.connect (self._host, username = self._user, password = self._password, key_filename = self._key_file, port = self._port)
        self._sftp = self._ssh.open_sftp ()
        return self

    def __exit__ (self, *args):
        self._sftp.close()
        self._ssh.close()
        self._ssh, self._sftp = None, None

    def isdir (self, path):
        try:
            return S_ISDIR (self._sftp.stat (path).st_mode)
        except IOError:
            return False

    def isfile (self, path):
        try:
            return S_ISREG (self._sftp.stat (path).st_mode)
        except IOError:
            return False

    def rmdir (self, path, recursive = False):
        if not recursive:
            self._sftp.rmdir (path)
        else:
            files = self._sftp.listdir (path)
            for f in files:
                filepath = os.path.join (path, f)
                try:
                    self._sftp.remove (filepath)
                except IOError:
                    self.rmdir (filepath, True)
            self._sftp.rmdir (path)


class Connection (fabric.Connection):
    def __init__ (self, host, user, port = 22, connect_kwargs = None):
        super ().__init__ (host, user, port = port, connect_kwargs = connect_kwargs)
        self.identify_system ()

    def sftp_client (self):
        return SFTP (self.host, self.user, self.connect_kwargs.get ('key_file'), self.connect_kwargs.get ('password'), self.port)

    def identify_system (self):
        r = self.run ('uname -a')
        if r.stdout.find ('Ubuntu') != -1:
            self.os = 'ubuntu'
        else:
            self.os = 'centos'

    def install (self, *apps):
        try:
            r = self.sudo ('apt install -y chkrootkit'.format (" ".join (apps)))
        except Exception as e:
            if e.result.return_code != 1:
                print ('  - error: ' + e.result.stderr)
            return False
        return True

    def run (self, cmd, *args, **kargs):
        x = super ().run (cmd, hide = True, *args, **kargs)
        pcmd = cmd.split ()[0]
        try:
            rclass = getattr (commands, pcmd)
        except AttributeError:
            rclass = commands.default

        r = rclass.Result (x.stdout, pcmd)
        x.command = cmd
        x.header = r.header
        x.meta = r.meta
        x.data = r.data
        return x

    def sudo (self, cmd):
        if 'password' in self.connect_kwargs:
            r = self.run ('echo "{}" | sudo -S {}'.format (self.connect_kwargs ['password'], cmd))
        else:
            r = self.run ('sudo {}'.format (cmd))
        return r


def connect (host, user = 'ubuntu', password = None, key_file = None, port = 22):
    if hasattr (host, 'public_dns_name'):
        host = host.public_dns_name
    if key_file:
        connect_kwargs = dict (key_filename = key_file)
    else:
        connect_kwargs = dict (password = password)
    return Connection (host, user, port, connect_kwargs = connect_kwargs)

