"""Rasa-related utils"""
import sys

from ai_replica.utils.files import get_main_dir_path
from ai_replica.utils.system import (
    set_environmental_variable,
    execute_command,
    kill_processes,
    install_dependencies,
)


main_server_command = "run -i localhost -p 8002"
actions_server_command = "run actions -p 8004"


def get_paths():
    """Returns various paths that are used during the Rasa launch"""
    main_dir_abs = get_main_dir_path()
    rasa_dir_abs = main_dir_abs + "/rasa"
    venv_path_abs = rasa_dir_abs + "/venv"
    working_dir_abs = rasa_dir_abs + "/bot"
    requirements_path_abs = rasa_dir_abs + "/requirements.txt"
    rasa_exec_path_abs = venv_path_abs + "/bin/rasa"
    pip_exec_path_abs = venv_path_abs + "/bin/pip3"
    return {
        "main_dir_abs": main_dir_abs,
        "venv_path_abs": venv_path_abs,
        "working_dir_abs": working_dir_abs,
        "requirements_path_abs": requirements_path_abs,
        "rasa_exec_path_abs": rasa_exec_path_abs,
        "pip_exec_path_abs": pip_exec_path_abs,
    }


def install_rasa_dependencies(required_python):
    main_dir, venv_dir, work_dir, requirements, rasa_exec, pip_exec = get_paths()
    install_dependencies(pip_exec, venv_dir, requirements, required_python, "rasa")
    return rasa_exec, work_dir


def start_rasa_main_server(rasa_exec, working_dir):
    """Starts the main Rasa server by executing a command like this: `rasa run -i localhost -p 8002`."""
    execute_command(
        rasa_exec, main_server_command, working_dir, run_in_another_terminal7=True
    )


def start_rasa_actions_server(rasa_exec, working_dir):
    """Starts the Rasa server for actions"""
    set_environmental_variable(key="SANIC_HOST", value="localhost")
    execute_command(
        rasa_exec, actions_server_command, working_dir, run_in_another_terminal7=True
    )


def stop_a_rasa_server(rasa_exec, server_name):
    if server_name == "main":
        command = main_server_command
    elif server_name == "actions":
        command = actions_server_command
    else:
        print(f"Unsupported rasa server_name: '{server_name}' . Exiting")
        sys.exit()
    kill_processes(expected_command_line_part=f"{rasa_exec} {command}")
    print(f"Stopped the {server_name} rasa server")


def train_model(rasa_exec, work_dir):
    """Executes `rasa train --domain domain` to train your model.

    The trained model will appear in the `models` folder."""
    execute_command(
        rasa_exec, "train --domain domain", work_dir, wait_till_finished7=True
    )
