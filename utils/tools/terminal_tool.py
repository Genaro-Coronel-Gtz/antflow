"""
Enhanced Terminal Tool for SmolagentsAPI
=========================================

A robust command execution tool that supports:
- Simple string commands
- JSON-structured commands with arguments
- Complex commands with pipes, redirections, and chaining
- Mixed-content parsing (text with embedded JSON)
- Security validation and sanitization
- Timeout protection

Usage Examples:
--------------
1. Simple command:
   tool.forward("ls -la")

2. JSON command:
   tool.forward('{"command": "docker-compose up", "args": ["-d"]}')

3. Mixed content:
   tool.forward('Running: {"command": "npm install"} now')

4. Complex command with pipes:
   tool.forward("cat file.txt | grep 'pattern' | wc -l")

Security Features:
-----------------
- Blocks destructive operations (rm -rf /, dd, mkfs, etc.)
- Prevents system control commands (shutdown, reboot, halt)
- Blocks permission manipulation on critical paths
- Prevents disk device writes
- Detects command injection patterns
- 5-minute timeout for long-running commands
"""

import subprocess
import json
import re
import shlex
from typing import Dict, Any, Optional, List
from smolagents import Tool
from .utils import write_log, PROJECT_BASE


class TerminalTool(Tool):
    """
    Execute shell commands in the project directory with enhanced parsing and security.
    
    Attributes:
        name: Tool identifier for the agent system
        description: Human-readable description
        inputs: Input schema definition
        output_type: Expected output type
    """
    
    name = "terminal"
    description = (
        "Ejecuta comandos DENTRO de la carpeta del proyecto. "
        "Soporta comandos simples, JSON estructurado y comandos complejos "
        "con pipes, redirecciones y argumentos."
    )
    inputs = {
        "command": {
            "type": "string",
            "description": "Comando a ejecutar (string simple o JSON)",
            "nullable": True
        }
    }
    output_type = "string"
    
    def forward(self, command: str = None) -> str:
        """
        Execute a command in the project directory.
        
        Args:
            command: Command to execute (string or JSON)
            
        Returns:
            Command output (stdout/stderr) or error message
            
        Examples:
            >>> tool.forward("echo 'Hello World'")
            "STDOUT:\nHello World\n"
            
            >>> tool.forward('{"command": "ls", "args": ["-la"]}')
            "STDOUT:\ntotal 24\ndrwxr-xr-x..."
        """
        if not command: 
            return "❌ Error: No hay comando."
        
        # Parse and extract the actual command
        parsed_command = self._parse_command_input(command)
        if not parsed_command:
            return "❌ Error: Comando inválido o vacío."
        
        # Validate and sanitize for security
        sanitized_command = self._validate_and_sanitize_command(parsed_command)
        if not sanitized_command:
            return "❌ Error: Comando no permitido por seguridad."
        
        try:
            result = subprocess.run(
                sanitized_command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=300,  # 5 minutes timeout
                cwd=PROJECT_BASE,
                env=None  # Inherit environment variables
            )
            
            write_log(self.name, sanitized_command, "Ejecutado.")
            
            # Format output for clarity
            output_parts = []
            if result.stdout:
                output_parts.append(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                output_parts.append(f"STDERR:\n{result.stderr}")
            if result.returncode != 0:
                output_parts.append(f"EXIT CODE: {result.returncode}")
            
            return "\n".join(output_parts) if output_parts else "✅ Comando ejecutado (sin output)."
            
        except subprocess.TimeoutExpired:
            error_msg = "❌ Error: Comando excedió el tiempo límite de 5 minutos."
            write_log(self.name, sanitized_command, error_msg)
            return error_msg
        except Exception as e: 
            error_msg = f"❌ Error ejecutando comando: {str(e)}"
            write_log(self.name, sanitized_command, error_msg)
            return error_msg
    
    def _parse_command_input(self, command_input: str) -> Optional[str]:
        """
        Parse command input from various formats.
        
        Supported formats:
        - Simple string: "ls -la"
        - JSON object: {"command": "ls -la"}
        - Complex JSON: {"command": "docker", "args": ["ps", "-a"]}
        - Mixed content: "Text before {"command": "ls"} text after"
        
        Args:
            command_input: Raw command input
            
        Returns:
            Parsed command string or None if invalid
        """
        command_input = command_input.strip()
        
        # Handle empty input
        if not command_input:
            return None
        
        # Try to extract JSON from mixed content first
        extracted_json = self._extract_json_from_text(command_input)
        if extracted_json:
            try:
                parsed = json.loads(extracted_json)
                if isinstance(parsed, dict):
                    cmd = self._build_command_from_dict(parsed)
                    if cmd:
                        return cmd
            except json.JSONDecodeError:
                pass
        
        # Try to parse as pure JSON
        if command_input.startswith('{') and command_input.endswith('}'):
            try:
                parsed = json.loads(command_input)
                if isinstance(parsed, dict):
                    cmd = self._build_command_from_dict(parsed)
                    if cmd:
                        return cmd
            except json.JSONDecodeError:
                # Invalid JSON format - reject it
                return None
        
        # Fallback: treat as simple string command
        # But only if it doesn't look like broken JSON
        if command_input.startswith('{') and not command_input.endswith('}'):
            # Looks like incomplete JSON
            return None
        
        return command_input
    
    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """
        Extract JSON object from text that may contain it.
        
        Uses brace matching to handle nested JSON properly.
        Only returns JSON objects with 'command' or 'cmd' keys.
        
        Args:
            text: Input text that may contain JSON
            
        Returns:
            Extracted JSON string or None
            
        Example:
            >>> self._extract_json_from_text('Run: {"command": "ls"} now')
            '{"command": "ls"}'
        """
        stack = []
        start_idx = -1
        
        for i, char in enumerate(text):
            if char == '{':
                if not stack:
                    start_idx = i
                stack.append(char)
            elif char == '}':
                if stack:
                    stack.pop()
                    if not stack and start_idx != -1:
                        # Found a complete JSON object
                        potential_json = text[start_idx:i+1]
                        try:
                            # Validate it's actually JSON
                            parsed = json.loads(potential_json)
                            # Only accept if it has command or cmd key
                            if isinstance(parsed, dict) and ('command' in parsed or 'cmd' in parsed):
                                return potential_json
                        except json.JSONDecodeError:
                            # Not valid JSON, keep looking
                            start_idx = -1
                            continue
        
        return None
    
    def _build_command_from_dict(self, cmd_dict: Dict[str, Any]) -> Optional[str]:
        """
        Build a command string from a dictionary specification.
        
        Supported keys:
        - command/cmd: Base command (required)
        - args: List or string of arguments (optional)
        - flags: Additional flags (optional)
        - env: Environment variables (logged, not applied)
        - cwd: Working directory (logged, not applied)
        
        Args:
            cmd_dict: Command specification dictionary
            
        Returns:
            Constructed command string or None
            
        Example:
            >>> self._build_command_from_dict({
            ...     "command": "docker",
            ...     "args": ["ps", "-a"],
            ...     "flags": ["--format", "json"]
            ... })
            'docker ps -a --format json'
        """
        # Get base command
        base_cmd = None
        if 'command' in cmd_dict:
            base_cmd = str(cmd_dict['command']).strip()
        elif 'cmd' in cmd_dict:
            base_cmd = str(cmd_dict['cmd']).strip()
        
        if not base_cmd:
            return None
        
        # Build full command with args
        command_parts = [base_cmd]
        
        # Add arguments
        if 'args' in cmd_dict:
            args = cmd_dict['args']
            if isinstance(args, list):
                for arg in args:
                    arg_str = str(arg).strip()
                    if arg_str:
                        # Quote arguments that contain spaces and aren't already quoted
                        if ' ' in arg_str and not self._is_quoted(arg_str):
                            command_parts.append(shlex.quote(arg_str))
                        else:
                            command_parts.append(arg_str)
            elif isinstance(args, str):
                command_parts.append(args.strip())
        
        # Add flags (if provided as separate parameter)
        if 'flags' in cmd_dict:
            flags = cmd_dict['flags']
            if isinstance(flags, list):
                command_parts.extend(str(f).strip() for f in flags if str(f).strip())
            elif isinstance(flags, str):
                command_parts.append(flags.strip())
        
        # Log additional metadata (env, cwd) but don't apply them
        # (for security and simplicity, we execute in PROJECT_BASE)
        if 'env' in cmd_dict and isinstance(cmd_dict['env'], dict):
            write_log(self.name, base_cmd, 
                     f"Variables de entorno solicitadas: {list(cmd_dict['env'].keys())}")
        
        if 'cwd' in cmd_dict:
            write_log(self.name, base_cmd, 
                     f"Directorio de trabajo solicitado: {cmd_dict['cwd']}")
        
        return ' '.join(command_parts)
    
    def _is_quoted(self, text: str) -> bool:
        """
        Check if text is already quoted.
        
        Args:
            text: Text to check
            
        Returns:
            True if text is wrapped in quotes
        """
        return ((text.startswith('"') and text.endswith('"')) or 
                (text.startswith("'") and text.endswith("'")))
    
    def _validate_and_sanitize_command(self, command: str) -> Optional[str]:
        """
        Validate and sanitize command for security.
        
        Blocks dangerous operations while allowing normal commands.
        
        Blocked patterns:
        - Destructive filesystem operations (rm -rf /, etc.)
        - Disk operations (dd, mkfs, fdisk)
        - System control (shutdown, reboot, halt)
        - Permission changes on critical paths
        - User/password management
        - Direct device writes
        - Command injection patterns
        
        Args:
            command: Command to validate
            
        Returns:
            Sanitized command or None if dangerous
        """
        if not command or not command.strip():
            return None
        
        # Limit command length to prevent abuse
        if len(command) > 4000:
            write_log(self.name, command[:100], "Comando demasiado largo")
            return None
        
        # Dangerous patterns that should be blocked
        dangerous_patterns = [
            # Destructive filesystem operations
            (r'\brm\s+-rf\s+/', "rm -rf /"),
            (r'\brm\s+-rf\s+\*', "rm -rf *"),
            (r'\brm\s+--no-preserve-root', "rm --no-preserve-root"),
            
            # Disk operations
            (r'\bdd\s+if=', "dd if="),
            (r'\bmkfs\.', "mkfs."),
            (r'\bformat\s+', "format"),
            (r'\bfdisk\s+', "fdisk"),
            
            # Dangerous sudo operations
            (r'\bsudo\s+rm\s+-rf', "sudo rm -rf"),
            (r'\bsudo\s+dd\s+', "sudo dd"),
            
            # Permission changes on critical files
            (r'\bchmod\s+777\s+/etc', "chmod 777 /etc"),
            (r'\bchmod\s+777\s+/bin', "chmod 777 /bin"),
            (r'\bchmod\s+777\s+/usr', "chmod 777 /usr"),
            (r'\bchown\s+root\s+/', "chown root /"),
            
            # User/password changes
            (r'\bsu\s+-', "su -"),
            (r'\bsu\s+root', "su root"),
            (r'\bpasswd\s+', "passwd"),
            (r'\buseradd\s+', "useradd"),
            (r'\buserdel\s+', "userdel"),
            
            # System control
            (r'\bshutdown\s+', "shutdown"),
            (r'\breboot\b', "reboot"),
            (r'\bhalt\b', "halt"),
            (r'\bpoweroff\b', "poweroff"),
            (r'\binit\s+0', "init 0"),
            (r'\binit\s+6', "init 6"),
            (r'\bsystemctl\s+(poweroff|reboot|halt)', "systemctl poweroff/reboot/halt"),
            
            # Cron manipulation
            (r'\bcrontab\s+-r', "crontab -r"),
            
            # Direct device writes
            (r'>\s*/dev/sd[a-z]', "> /dev/sd*"),
            (r'>>\s*/dev/sd[a-z]', ">> /dev/sd*"),
            (r'echo.*>\s*/dev/sd[a-z]', "echo > /dev/sd*"),
            
            # Kernel operations
            (r'\bkill\s+-9\s+1\b', "kill -9 1"),
            (r'\bkillall\s+-9\s+init', "killall -9 init"),
        ]
        
        # Check for dangerous patterns
        for pattern, description in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                write_log(self.name, command[:100], 
                         f"Comando bloqueado por patrón peligroso: {description}")
                return None
        
        # Additional validation: check for suspicious nested command execution
        # Allow normal command substitution but block obvious injection attempts
        nested_cmd_patterns = [
            (r';\s*rm\s+-rf', "; rm -rf"),
            (r'\|\s*rm\s+-rf', "| rm -rf"),
            (r'&&\s*rm\s+-rf', "&& rm -rf"),
            (r'`\s*rm\s+-rf', "` rm -rf"),
            (r'\$\(\s*rm\s+-rf', "$( rm -rf"),
        ]
        
        for pattern, description in nested_cmd_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                write_log(self.name, command[:100], 
                         f"Comando bloqueado por inyección sospechosa: {description}")
                return None
        
        return command.strip()
    
    def _escape_shell_arg(self, arg: str) -> str:
        """
        Safely escape a shell argument using shlex.
        
        Args:
            arg: Argument to escape
            
        Returns:
            Shell-safe escaped argument
        """
        return shlex.quote(arg)


# Export for easier imports
__all__ = ['TerminalTool']