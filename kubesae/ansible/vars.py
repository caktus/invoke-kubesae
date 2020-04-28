"""Ansible vars module.

Provides utilities to load host and group vars from Ansible.

Adoped from Ansible's Python API:
    https://docs.ansible.com/ansible/latest/dev_guide/developing_api.html
"""

import json
import shutil

import ansible.constants as C
import invoke
from ansible import context
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.inventory.manager import InventoryManager
from ansible.module_utils._text import to_bytes
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.parsing.vault import VaultSecret
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from ansible.vars.manager import VariableManager


class ResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """

    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json representation of the result

        This method could store the result in an instance attribute for retrieval later
        """
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))


# since the API is constructed for CLI it expects certain options to always
# be set in the context object
context.CLIARGS = ImmutableDict(
    connection="local",
    module_path=["/to/mymodules"],
    forks=10,
    become=None,
    become_method=None,
    become_user=None,
    check=False,
    diff=False,
)

loader = DataLoader()
# Instantiate our ResultCallback for handling results as they come in. Ansible
# expects this to be one of its main display outlets
results_callback = ResultCallback()


@invoke.task
def play_vars(ctx):
    # create inventory, use path to host config file as source or hosts in a comma
    # separated string
    inventory = InventoryManager(loader=loader, sources="inventory")
    # variable manager takes care of merging all the different sources to give you
    # a unified view of variables available in each context
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    # create data structure that represents our play, including tasks, this is basically
    # what our YAML loader does internally.
    play_source = dict(name="Ansible Play", hosts="all", gather_facts="no", tasks=[])
    loader.set_vault_secrets([("default", VaultSecret(_bytes=to_bytes("TBD")))])
    # Create play object, playbook objects use .load instead of init or new methods,
    # this will also automatically create the task objects from the info provided
    # in play_source
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
    tqm = None
    try:
        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            passwords=dict(),
            # Use our custom callback instead of the ``default`` callback
            # plugin, which prints to stdout
            stdout_callback=results_callback,
        )
        # most interesting data for a play is actually
        # sent to the callback's methods
        tqm.run(play)
    finally:
        # we always need to cleanup child procs and the structures we use to
        # communicate with them
        if tqm is not None:
            tqm.cleanup()
        # Remove ansible tmpdir
        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)
    ctx.hostvars = variable_manager.get_vars()["hostvars"]
