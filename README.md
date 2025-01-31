## Jam Sandwich Hosting

Service manager and configuration for my personal server

## The Service Manager
At the core of this project is the service manager, implemented
at [jam_sandwich_hosting.py](./jam_sandwich_hosting.py). It is
written with a very specific usecase in mind, and adopts an
extremely simplified model to approach the problem of service
management. The design principles and decisions are as follows:

* **Minimal assumptions about service nature**  
  As described in "The Service Model", a service is simply a
  package that can optionally provide a start command and a periodic
  action. No assumptions are made about the nature of functionality,
  implementation language/platform and so on.
* **Separation of package manager logic**  
  The logic to install and manage packages is separate from the
  core of the service manager, and is implemented in _package manager scripts_.
  Because of this, new package managers can be plugged in and leveraged
  with minimal effort.  
  Since most software is available through some
  mature package manager (e.g. `pip` for Python software, `npm` for
  NodeJS software), there is no need to re-define the functionality
  they provide.
* **Declarative service definitions**  
  Service definitions are TOML tables. The only imperative parts
  of a service definition are the commands for starting the service
  and periodic action.  
  The logic for handling services (installation, start-up,
  environment setup, and so on) is defined in the package
  managers scripts, so that service definitions can be kept as
  declarative as possible.

### The Service Model
Each service is a single _package_ as provided by a 
_package manager_. Each package manager provides some packages,
and is responsible for installing and updating those packages. A
thin wrapper, the _package manager script_, must be written for each
package manager to implement the interface to `jam_sandwich_hosting.py`.
The package manager script wraps the install/update functionality
of the package manager and defines how to run programs provided
by the package manager.

Each service can be started and stopped once it is installed;
additionally, it can specify an action that is to be run periodically.

### Directory Layout
The service manager maintains the following files and directories:

* `install/<srv>/`: Service installation directory
* `data/<srv>/`: Service data
* `export/`: Common space that services can use to share data
* `log/<srv>`: Log output from a service
* `pid/<srv>`: The PID of a running service

These directories are created in the current working directory,
regardless of where `jam_sandwich_hosting.py` is installed.

Additionally, the following files and directories are recognized:

* `config/<srv>/`: Site-specific and sensitive configuration
* [`services.toml`](./services.toml): Service definitions
* `services.toml.d`: Additional service definition fragements.  
  These are parsed after `services.toml`, in lexicographic order of
  filename; definitions parsed later override earlier definitions.

_Note: `<srv>` is the name of a service_

### Package Manager Scripts
Each package manager script wraps the functionality of one package
manager -- for instance [package_managers/pip](./package_managers/pip)
wraps Python's package manager, [pip](https://pip.pypa.io/en/stable/).

The package manager script is expected to support the following command
forms:

* `<pm> bringup <pkg>`  
  This is used to install the service.
* `<pm> start <pkg> <cmd> [<arg1> ... ]`  
  This is used to execute the service. `<cmd> <arg1> ...` is a command
  that is executed by the package manager script.

_Note: `<pkg>` is a package name and `<pm>` is the name of a package manager script_

The package manager script is always invoked with `install/<srv>` as
the working directory. The following environment variables are made
available:

* `JSH_INSTALL`: Full path to the installation directory, `install/<srv>`
* `JSH_DATA`: Full path to the data directory, `data/<srv>`
* `JSH_CONFIG`: Full path to the config directory, `config/<srv>`
* `JSH_ENV_*`: Arbitrary extra properties that can be supplied in
  service definitions and used by package managers (see the `env`
  key under "Service Definitions").

_Note: `<srv>` is the name of a service_

### Service Definitions
Services are defined as tables in [services.toml](./services.toml).
Each service must define the following keys:

* `package` (string): The name of the package that provides this service
* `pm` (string): The name of the package manager script that provides this package  
  There must be a package manager script by the same name.

Additionally, the following keys may be defined:

* `start-cmd` (string, shell-formatted): The command that must be run to
  start the service.  
  This command is passed to the package manager script, which handles
  setting up the environment and actually passing over control. The
  command specified is treated as a line of shell script.  
  The process started by this command must block.
* `periodic-cmd` (string, shell-formatted): Similar to `start-cmd`, but
  to be run at regular intervals.
* `export` (list of string pairs): Directories to "export", i.e. to expose in
  the `export/` directory. The value is of the form

      export = [ ["dir1", "dest1"], ... ]

  with the effect that `export/dest1` is symlinked to `dir1`.
* `env` (dictionary, mapping of string to string): Arbitrary, non-standard
  properties to pass to the package manager script. The value is of the form

      env = [ {"name1" = "val1", ... } ]

  with the effect that the environment variable `JSH_ENV_name1` is set to `val`
  in the package manager script's execution environment.

The strings used in `start-cmd`, `periodic-cmd` and `export` are
parametrised. Before being evaluated, the following substitutions
are applied to the strings:

* `{persist}` -> Full path to `install/<srv>`
* `{data}` -> Full path to `data/<srv>`
* `{config}` -> Full path to `config/<srv>`
* `{export}` -> Full path to `export/`

_Note: `<srv>` is the name of a service_
