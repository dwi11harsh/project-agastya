import pytest
from agastya.shell.executor import ShellExecutor

@pytest.mark.asyncio
async def test_shell_execute_approved():
    # Callback simulates the UI returning the original command (User clicked "Run")
    async def approve_callback(cmd: str) -> str | None:
        return cmd
        
    executor = ShellExecutor(approve_callback)
    
    # Using 'echo' since it's a safe cross-platform built-in
    result = await executor.execute("echo 'hello agastya'")
    assert "hello agastya" in result

@pytest.mark.asyncio
async def test_shell_execute_denied():
    # Callback simulates the UI returning None (User clicked "Deny")
    async def deny_callback(cmd: str) -> str | None:
        return None
        
    executor = ShellExecutor(deny_callback)
    
    result = await executor.execute("echo 'hello agastya'")
    assert "Execution denied by user" in result

@pytest.mark.asyncio
async def test_shell_execute_edited():
    # Callback simulates the UI returning an edited command (User clicked "Edit" -> Typed new command -> "Run")
    async def edit_callback(cmd: str) -> str | None:
        return "echo 'hello edited'"
        
    executor = ShellExecutor(edit_callback)
    
    result = await executor.execute("echo 'hello agastya'")
    assert "hello edited" in result
    assert "hello agastya" not in result

@pytest.mark.asyncio
async def test_shell_execute_timeout():
    async def approve_callback(cmd: str) -> str | None:
        return cmd
        
    executor = ShellExecutor(approve_callback, timeout=0.1)
    
    # Sleep longer than the executor timeout
    result = await executor.execute("sleep 1")
    assert "Execution timed out" in result
