#!/bin/env python3

from sys import stdout, argv
from os import set_inheritable, getcwd, makedirs, path, kill, remove, environ, symlink
from subprocess import Popen
import yaml
from signal import SIGINT
from shutil import make_archive
import shlex


## Default constants and macros

ROOTDIR = getcwd ()  # TODO: More robust path handling
SERVICES_FILE = f"{ROOTDIR}/services.yaml"
PACKAGE_MANAGER = lambda pm: f"{ROOTDIR}/package_managers/{pm}"
PERSIST_DIR = lambda srv: f"{ROOTDIR}/install/{srv}/"
CONFIG_DIR = lambda srv: f"{ROOTDIR}/config/{srv}"
DATA_DIR = lambda srv: f"{ROOTDIR}/data/{srv}"
EXPORT_DIR = f"{ROOTDIR}/export/"
LOG_FILE = lambda srv: f"{ROOTDIR}/log/{srv}"
PID_FILE = lambda srv: f"{ROOTDIR}/pid/{srv}"
SKELETON_FILES = (
    PERSIST_DIR (""),
    DATA_DIR (""),
    LOG_FILE (""),
    PID_FILE (""),
    EXPORT_DIR,
)
REQUIRED_FILES = (
    CONFIG_DIR (""),
    PACKAGE_MANAGER (""),
    SERVICES_FILE,
)

## Program execution

def cmd_run (cmd, workdir, *, pidfile = None, logfile = None, wait = False, env = {}):
    """
    Wrapper around `subprocess.Popen`.

    This is the only point in this program where
    `Popen` is directly interfaced with.
    """
    if logfile is None:
        out = stdout
    else:
        out = open (logfile, "a")
        set_inheritable (out.fileno (), True)

    proc = Popen (
        cmd,
        cwd = workdir,
        stdout = out,
        stderr = out,
        env = {**env, "PATH": environ ["PATH"]},
    )
    if wait:
        proc.wait ()

    if pidfile is not None:
        with open (pidfile, "w") as pf:
            pf.write (str(proc.pid))

def env_setup (srv):
    """
    Populate and return a dictionary with environment variables
    from service definition `srv` (dict).
    These variables are consumed by package manager scripts.
    """
    env = srv ["env"]
    name = srv ["name"]

    config = CONFIG_DIR (name)
    persist = PERSIST_DIR (name)
    data = DATA_DIR (name)
    return {
        "JSH_INSTALL": persist,
        "JSH_DATA": data,
        "JSH_CONFIG": config,
        "JSH_ARGS": srv ["args"].format (**format_args (srv)),
        **{
            f"JSH_ENV_{var}": val
            for var, val in env.items ()
        },
    }

def format_args (srv):
    srv_name = srv ["name"]
    return {
        "persist": PERSIST_DIR (srv_name),
        "config": CONFIG_DIR (srv_name),
        "data": DATA_DIR (srv_name),
        "export": EXPORT_DIR,
    }


## Service management

service_key_shapes = {
    # Mapping: key name -> shape
    # All valid keys are listed here
    "pm": "",
    "package": "",
    "args": "",
    "env": {"": ""},
    "export": [["", ""]],
    "periodic": "",
}
service_key_defaults = {
    # Mapping: key name -> default value
    # Only optional keys are listed here
    "args": "",
    "env": {},
    "export": [],
    "periodic": "",
}

def verify_shape (obj, shape):
    """
    Recursively verify the shape of `obj`
    against `shape`.
    """
    if type (obj) != type (shape):
        return False

    if isinstance (obj, list) or isinstance (obj, tuple):
        if len (obj) != len (shape):
            return False
        for o, s in zip (obj, shape):
            if not verify_shape (o, s):
                return False

    elif isinstance (obj, dict):
        if not verify_shape (obj.items (), shape.items ()):
            return False

    return True

def parse_services (srv_filename: str):
    """
    Parse and preprocess service definitions
    from a file (typically `services.yaml`).

    The shape of each service is verified using
    `service_key_shapes` and default values
    plugged from `service_key_defaults`.

    The returned dict is a mapping from service
    name to service defintion; the service
    definitions themselves are dicts.
    """
    with open (srv_filename) as srv_file:
        services = yaml.safe_load (srv_file)

    for name, srv in services.items ():
        # Shape validation
        for key, val in srv.items ():
            shape = service_key_shapes.get (key)
            if shape is None:
                raise Exception (f"Service {name}: Invalid key: {key}")
            if not verify_shape (val, shape):
                raise Exception (f"Service {name}: Invalid value for key {key}")

        # Default and missing values
        for key in service_key_shapes:
            if key in srv:
                continue
            dflt = service_key_defaults.get (key)
            if dflt is None:
                raise Exception (f"Service {name}: Key {key} is missing")
            else:
                srv [key] = dflt.copy ()

        srv ["name"] = name

    return services

def bringup (srv: dict):
    """
    Bring up (i.e. install and minimally
    configure) service `srv`.

    `srv` is a value in the dict returned
    by `parse_services`).
    """
    srv_name = srv ["name"]
    pm_script = PACKAGE_MANAGER (srv ["pm"])
    persist_dir = PERSIST_DIR (srv_name)
    data_dir = DATA_DIR (srv_name)
    config_dir = CONFIG_DIR (srv_name)

    for diry in (persist_dir, data_dir):
        try: makedirs (diry)
        except FileExistsError: pass

    export_dirs = srv ["export"]
    for src, name in export_dirs:
        try:
            symlink (
                src.format (**format_args (srv)),
                f"{EXPORT_DIR}/{name}"
            )
        except FileExistsError:
            pass

    cmd_run (
        (pm_script, "bringup", srv ["package"]),
        persist_dir,
        wait = True,
        env = env_setup (srv)
    )

def start (srv):
    """
    Start service `srv`.

    `srv` is a value in the dict returned
    by `parse_services`.
    """
    srv_name = srv ["name"]
    logfile = LOG_FILE (srv_name)
    persist_dir = PERSIST_DIR (srv_name)
    pm_script = PACKAGE_MANAGER (srv ["pm"])

    if not path.exists (persist_dir):
        raise Exception (f"{srv_name}: not installed")

    if srv.get ("static"):
        pidfile_opt = {}
    else:
        pidfile = PID_FILE (srv_name)
        if path.exists (pidfile):
            raise Exception (f"{srv_name}: already running")
        pidfile_opt = {"pidfile": pidfile}

    cmd_run (
        (pm_script, "start", srv ["package"]),
        persist_dir,
        logfile = logfile,
        env = env_setup (srv),
        **pidfile_opt,
    )

def stop (srv):
    """
    Stop service `srv`.

    `srv` is a value in the dict returned
    by `parse_services`).
    """
    srv_name = srv ["name"]
    if srv.get ("static"):
        print (f"Service {srv_name} is a static service")
        return

    pidfile = PID_FILE (srv_name)
    if not path.exists (pidfile):
        raise Exception (f"{srv_name}: not running")

    with open (pidfile) as pf:
        pid = pf.read ()
    remove (pidfile)
    kill (int (pid), SIGINT)


## Backup and periodic maintenance

def backup ():
    make_archive ("./backup", format = "tar", base_dir = DATA_DIR(""))

def periodic (srv: dict):
    """
    Run periodic maintenance jobs:
    * Service bringup
    * Periodic actions defined by services
    """
    srv_name = srv ["name"]
    pm_script = PACKAGE_MANAGER (srv ["pm"])
    persist_dir = PERSIST_DIR (srv_name)

    if not path.exists (persist_dir):
        raise Exception (f"{srv_name}: not installed")

    cmd = srv ["periodic"]
    if cmd:
        cmd_run (
            shlex.split (cmd.format (**format_args (srv))),
            persist_dir,
            env = env_setup (srv),
            wait = True
        )


## Entry point

def main ():
    services = parse_services (SERVICES_FILE)
    cmd_args = argv [1:]

    for diry in REQUIRED_FILES:
        if not path.exists (diry):
            raise Exception (f"{diry} is missing")

    for diry in SKELETON_FILES:
        try:
            makedirs (diry)
        except FileExistsError:
            pass

    service_actions = {
        # Per-service actions and their handler functions
        "bringup": bringup,
        "start": start,
        "stop": stop,
        "periodic": periodic,
    }

    action = cmd_args.pop (0)

    if action in service_actions:
        srv = services [cmd_args.pop (0)]
        service_actions [action](srv)

    elif action == "foreach":
        # Iterate over each service and run the specified action
        handler = service_actions [cmd_args.pop (0)]
        for srv in services.values ():
            try:
                handler (srv)
            except Exception as e:
                print (f"{srv ["name"]}: {e}")

    elif action == "backup":
        backup ()
    elif action == "dump-config":
        print (yaml.dump (services))

    else:
        raise Exception (f"Invalid action: {action}")

if __name__ == "__main__":
    main ()
