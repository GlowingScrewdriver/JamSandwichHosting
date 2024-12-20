## package_managers/

Each file here (i.e. package_managers/&lt;package_manager&gt;) is
the definition of a package manager.

### Package manager definition
Each `package_managers/&lt;package_manager&gt;` is an executable program
that implements functionality to manage services. The program is invoked
with two arguments: an action, which is one of `bringup`, `start` and
`stop`; and and a package name, the exact meaning of which varies between
package managers. For instance, the package name for `pip` could be the
name of the package on PyPi.

Additional information is passed through environment variables:
* `JSH_INSTALL`: the directory in which the service should be installed;
  the package manager script is called with this directory as the working
  directory
* `JSH_DATA`: the directory which the service must use to store user data
* `JSH_CONFIG`: the directory which holds site-specific configuration for
  the service
* `JSH_ARGS`: command-line arguments to be supplied to the service
* `JSH_ENV_*`: arbitrary environment variables supplied by the package
  definition; these might be used for package managers that need certain
  information that is not relevant for other package managers
