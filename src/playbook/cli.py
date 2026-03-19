import click

from playbook import __version__

from playbook.commands.init import init_cmd

# Commands registered in tasks 004-006
# from playbook.commands.task import task_group
# from playbook.commands.status import status_cmd
# from playbook.commands.relay import relay_cmd


@click.group()
@click.version_option(version=__version__)
def cli():
    """Project Playbook CLI — plan, task, execute, verify."""
    pass


cli.add_command(init_cmd, "init")
# cli.add_command(task_group, "task")
# cli.add_command(status_cmd, "status")
# cli.add_command(relay_cmd, "relay")


if __name__ == "__main__":
    cli()
