# Copyright 2015-2016 Canonical Ltd.
#
# This file is part of the Coordinator Layer for Juju.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import importlib

from charmhelpers.coordinator import BaseCoordinator
from charmhelpers.core import hookenv
import charms.layer
import charms.reactive

import reactive.coordinator


def _instantiate():
    default_name = 'reactive.coordinator.SimpleCoordinator'
    full_name = charms.layer.options('coordinator').get('class',
                                                        default_name)
    components = full_name.split('.')
    module = '.'.join(components[:-1])
    name = components[-1]

    if not module:
        module = 'reactive.coordinator'

    class_ = getattr(importlib.import_module(module), name)

    assert issubclass(class_, BaseCoordinator), \
        '{} is not a BaseCoordinator'.format(full_name)

    return class_(peer_relation_name='coordinator')


# Instantiate the BaseCoordinator singleton, which installs
# its charmhelpers.core.atstart() hooks.
coordinator = _instantiate()
reactive.coordinator.coordinator = coordinator


def initialize_coordinator_state():
    '''
    The coordinator.granted.{lockname} state will be set and the
    coordinator.requested.{lockname} state removed for every lock
    granted to the currently running hook.

    The coordinator.requested.{lockname} state will remain set for locks
    not yet granted
    '''
    global coordinator
    hookenv.log('Initializing coordinator layer')
    # Remove reactive state for locks that have been released.
    granted = set(coordinator.grants.get(hookenv.local_unit(), {}).keys())
    previously_granted = set(state.split('.', 2)[2]
                             for state in charms.reactive.bus.get_states()
                             if state.startswith('coordinator.granted.'))
    for released in (previously_granted - granted):
        charms.reactive.remove_state('coordinator.granted.{}'.format(released))
    for state in granted:
        charms.reactive.set_state('coordinator.granted.{}'.format(state))

    requested = set(coordinator.requests.get(hookenv.local_unit(), {}).keys())
    previously_requested = set(state.split('.', 2)[2]
                               for state in charms.reactive.bus.get_states()
                               if state.startswith('coordinator.requested.'))
    for dropped in (previously_requested - requested):
        charms.reactive.remove_state('coordinator.requested.{}'
                                     ''.format(dropped))
    for state in requested:
        charms.reactive.set_state('coordinator.requested.{}'.format(state))


# Per https://github.com/juju-solutions/charms.reactive/issues/33,
# this module may be imported multiple times so ensure the
# initialization hook is only registered once. I have to piggy back
# onto the namespace of a module imported before reactive discovery
# to do this.
if not hasattr(charms.reactive, '_coordinator_registered'):
    hookenv.atstart(initialize_coordinator_state)
    charms.reactive._coordinator_registered = True
