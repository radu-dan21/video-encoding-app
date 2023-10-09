import logging
import subprocess


logger = logging.getLogger(__file__)


class ShellOperations:
    @staticmethod
    def call_bash_cmd(cmd: str) -> str:
        """
        Calls a bash command
        Returns stdout if the command ran successfully
        Raises an exception if the command did not run successfully
        :param cmd: bash command as string
        :return: stdout as string
        """
        popen = subprocess.Popen(
            ["/bin/bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info(f"Running command: {cmd}")
        out, err = popen.communicate(cmd.encode())
        popen.wait()
        if not (rc := popen.returncode) == 0:
            raise Exception(
                f'Could not run command "{cmd}"! '
                f'Return code: {rc}, stderr: "{err}".'
            )
        return out.decode("utf-8")
