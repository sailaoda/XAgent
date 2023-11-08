import asyncio
import os
import uuid
from datetime import datetime
from typing import List

from colorama import Fore

from XAgentIO.BaseIO import XAgentIO
from XAgentIO.input.CommandLineInput import CommandLineInput
from XAgentIO.output.CommandLineOutput import CommandLineOutput
from XAgentServer.envs import XAgentServerEnv
from XAgentServer.interaction import XAgentInteraction
from XAgentServer.loggers.logs import Logger
from XAgentServer.models.interaction import InteractionBase
from XAgentServer.models.parameter import InteractionParameter
from XAgentServer.server import XAgentServer


class CommandLine():
    """
    A command-line interface for interacting with XAgentServer.

    Attributes:
        env: An instance of the XAgentServer environment.
        client_id: A unique identifier for the client, generated as a hexadecimal UUID.
        date_str: The current date as a string in YYYY-MM-DD format.
        log_dir: The directory where the logs are stored.
        logger: An instance of the Logger used for logging interactions.
        interactionDB: A database interface for interacting with either a persistent
            database (SQLite, MySQL, PostgreSQL) or a local storage file, depending
            on the configuration of `env`.
    """
    def __init__(self, env: XAgentServerEnv):
        """
        Initialize the CommandLine instance.

        Args:
            env: An instance of the XAgentServer environment.
        """
        self.env = env
        self.client_id = uuid.uuid4().hex
        self.date_str = datetime.now().strftime("%Y-%m-%d")
        self.log_dir = os.path.join(os.path.join(XAgentServerEnv.base_dir, "localstorage",
                                    "interact_records"), self.date_str, self.client_id)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.logger = Logger(log_dir=self.log_dir, log_file=f"interact.log")

        self.logger.typewriter_log(
            title=f"XAgentServer is running on cmd mode",
            title_color=Fore.RED)
        self.logger.info(title=f"XAgentServer log:", title_color=Fore.RED, message=f"{self.log_dir}")

        if env.DB.db_type in ["sqlite", "mysql", "postgresql"]:
            from XAgentServer.database.connect import DBConnection
            from XAgentServer.database.dbi import InteractionDBInterface

            connection = DBConnection(env)
            self.logger.info("init db connection")

            self.interactionDB = InteractionDBInterface(env)
            self.logger.info("init interaction db")
            self.interactionDB.register_db(connection)

        else:
            from XAgentServer.database.lsi import \
                InteractionLocalStorageInterface
            self.logger.info(
                "init localstorage connection: interaction.json")
            self.interactionDB = InteractionLocalStorageInterface(env)

    def run(self, args: dict):
        """
        Runs the interaction with the XAgentServer with the provided arguments.

        Args:
            args: A dictionary of arguments for the interaction.

        Raises:
            ValueError: If `args` is not a dictionary.
            Exception: If there is already a running interaction for the user.
        """
        if args is None or not isinstance(args, dict):
            raise ValueError("args must be a dict")

        # omitted for brevity

        asyncio.run(server.interact(interaction=interaction))

    def start(self,
              task,
              role="Assistant",
              plan=[],
              upload_files: List[str] = [],
              download_files: List[str] = [],
              record_dir: str = None,
              mode: str = "auto",
              max_wait_seconds: int = 600,
              description: str = "XAgent-Test",):
        """
        Start an interaction with the XAgentServer.

        Args:
            task: Task description.
            role: Role name (default is "Assistant").
            plan: List of steps to perform (default is empty list).
            upload_files: List of files to upload (default is empty list).
            download_files: List of files to download (default is empty list).
            record_dir: Directory to store records (default is `None`).
            mode: Run mode. Can be "auto" or "manual" (default is "auto").
            max_wait_seconds: Maximum wait time in seconds (default is 600).
            description: Description of the interaction (default is "XAgent-Test").
        """
        print("-=-=--=-=-=-=-=-=-= Current Instruction =-=-=-=-=-=-=-=-=-=-=-=-=-=-")
        print(task)

        self.run({
            "description": description,
            "role_name": role,
            "download_files": download_files,
            "file_list": upload_files,
            "record_dir": record_dir,
            "goal": task,
            "mode": mode,
            "plan": plan,
            "max_wait_seconds": max_wait_seconds
        })


if __name__ == "__main__":
    cmd = CommandLine(XAgentServerEnv)
    import sys
    if len(sys.argv) >= 2:
        print(sys.argv[1])
        if len(sys.argv) >= 3:
            original_stdout = sys.stdout
            from XAgent.running_recorder import recorder
            sys.stdout = open(os.path.join(recorder.record_root_dir,"command_line.ansi"),"w",encoding="utf-8")
            
        cmd.start(
            sys.argv[1],
            role="Assistant",
            mode="auto",
        )
        if len(sys.argv) >= 3:
            sys.stdout.close()
            sys.stdout = original_stdout
        
    else:
        cmd.start(
            "I will have five friends coming to visit me this weekend, please find and recommend some restaurants for us.",
            role="Assistant",
            mode="auto",
        )
