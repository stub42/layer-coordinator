# Coordinator Layer for Juju Charms

The Coordinator layer is for charm-tools and 'charm build', making it
easier for layered charms to coordinate operations between units in
a service. The most common example is rolling restarts, where only
one unit at a time is restarted to ensure availability of the overall
service.

This layer wraps the [coordinator module from charm-helpers
](http://pythonhosted.org/charmhelpers/api/charmhelpers.coordinator.html).
The coordinator module implements locking within a Juju service. The
layer maintains charms.reactive states, allowing you to allowing you to
write handlers that will be activated when requested locks are granted.

```python
import charms.coordinator
from charmhelpers.core.hookenv import status_set


@hook('config-changed')
def config_changed():
    reconfigure()
    charms.coordinator.acquire('restart')


@when('coordinator.granted.restart')
def restart():
    status_set('maintenance', 'Rolling restart')
    restart()
    status_set('active', 'Live')
```

By default, locks will only be granted to a single unit in the service
at any time. All locks requested by this unit will be granted, and no
other locks held by any other units. This means only one unit may perform
guarded operations at a time, and the lock name used is irrelevant. See
the Customization section on how to change this behaviour.


## API

The `charms.coordinator` module exposes a single method:

* acquire(lockname)

  Requests a lock. Returns True if the lock could be immediately granted.

  If the lock cannot be granted immediately, the
  `coordinator.requested.{lockname}` state is set.

  Once the lock is granted, the `coordinator.requested.{lockname}` state
  will be removed and the `coordinator.granted.{lockname}` state set.

  The `coordinator.granted.{lockname}` state will only remain set for
  the duration of the hook. 


The actual BaseCoordinator instance is available as
`charms.coordinator.coordinator` if you need to interrogate it,
but the reactive states make this unnecessary for most needs.


## States

* `coordinator.requested.{lockname}

  A request for the named lock has been made, but has not yet been granted.
  This request may have been made in a previous hook.

* `coordinator.granted.{lockname}

  The named lock has been granted. The lock will only be held until
  the end of the hook, even if more requests to reacquire it are
  made. You cannot maintain hold on a lock across multiple hooks - other
  units will always be given the opportunity to acquire it.


## Customization

The `charmhelpers.coordinator` module lets you customize the rules on how
and when locks are granted, by subclassing the
`charmhelpers.coordinator.BaseCoordinator` class. You could, for example,
grant `restart` locks to N/2-1 units at a time. Or only grant locks when
a particular config item has been set, blocking charm operations until
the operator has given the go ahead.

The default `charms.coordinator.SimpleCoordinator` implementation only
grants locks to a single unit at a time, and the lock names are
irrelevant. Another implementation is `charmhelpers.coordinator.Serial`,
which grants the named lock to a single unit at a time but allows for
different units to hold different locks.

To plugin a different BaseCoordinator implementation, specify the
absolute dotted path to your class in your `layer.yaml` file:

```yaml
includes:
    - layer:basic
    - layer:coordinator
options:
    coordinator:
        class: charmhelpers.coordinator.Serial
        log_level: debug
```


## Support

This layer is maintained on Launchpad by
Stuart Bishop (stuart.bishop@canonical.com).

Code is available using git at git+ssh://git.launchpad.net/layer-coordinator.

Bug reports can be made at https://bugs.launchpad.net/layer-coordinator.

Queries and comments can be made on the Juju mailing list, Juju IRC
channels, or at https://answers.launchpad.net/layer-coordinator.
