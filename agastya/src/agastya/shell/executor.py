import asyncio
from typing import Callable, Awaitable, Optional

class ShellExecutor:
    """
    Executes shell commands asynchronously, wrapping them in a mandatory user confirmation flow.
    """
    def __init__(self, confirmation_callback: Callable[[str], Awaitable[Optional[str]]], timeout: float = 30.0):
        self.confirmation_callback = confirmation_callback
        self.timeout = timeout

    async def execute(self, command: str) -> str:
        """
        Requests permission via callback, and if approved, runs the command.
        Returns the stdout/stderr payload.
        """
        # Resolve user intent asynchronously
        final_command = await self.confirmation_callback(command)
        
        if final_command is None:
            return "Error: Execution denied by user."
            
        try:
            # Create isolated subprocess running the approved command
            process = await asyncio.create_subprocess_shell(
                final_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for execution or timeout
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=self.timeout)
            
            output = ""
            if stdout:
                output += stdout.decode().strip()
            if stderr:
                output += ("\n[STDERR]: " if output else "") + stderr.decode().strip()
                
            return output if output else "Command executed successfully with no output."
            
        except asyncio.TimeoutError:
            try:
                process.terminate()
            except Exception:
                pass
            return f"Error: Execution timed out after {self.timeout} seconds."
        except Exception as e:
            return f"Error executing shell command: {e}"
