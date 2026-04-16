from rich.console import Console

def clear_console():
    from os import system, name
    """Limpia la consola"""
    console = Console()
    console.clear()
    system('cls' if name == 'nt' else 'clear')
