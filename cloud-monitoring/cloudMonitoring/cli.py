"""
Main entry point when package is called with python -m my_package
"""

import sys
from typing import Dict, Callable


def dispatch_command():
    from cloudMonitoring.collect_vm_stats import main as vm_stats_main
    from cloudMonitoring.limits_to_influx import main as project_stats_main
    from cloudMonitoring.slottifier import main as slottifier_main
    from cloudMonitoring.service_status_to_influx import main as service_stats_main

    # Command registry - maps command names to their main functions
    commands: Dict[str, Callable] = {
        "vm-states": vm_stats_main,
        "project-stats": project_stats_main,
        "slottifier": slottifier_main,
        "service-stats": service_stats_main,
    }

    # Check that mandatory args passed - package and command
    if len(sys.argv) < 2:
        print("Usage: monitoring <command> <config-filpath> [args...]", file=sys.stderr)
        print(f"Available commands: {', '.join(commands.keys())}", file=sys.stderr)
        return 1

    command_name = sys.argv[1]

    # Check if command exists
    if command_name not in commands:
        print(f"Error: Unknown command '{command_name}'", file=sys.stderr)
        print(f"Available commands: {', '.join(commands.keys())}", file=sys.stderr)
        return 1

    # Remove the package name and command name from sys.argv
    # So the command's parser sees only its arguments
    user_args = sys.argv[2:]
    return commands[command_name](user_args)
