#!/usr/bin/env python3
import os
import fnmatch
#import logging
from smolagents import Tool
from .utils import write_log, safe_path
from rich.console import Console
from rich.tree import Tree
from rich.text import Text

# Configurar logging para errores
# logging.basicConfig(
#     filename='.antflow/errors.log',
#     level=logging.ERROR,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

def load_ignore_file():
    """Carga exclusiones desde .antflow/antflow.ignore con soporte para patrones tipo gitignore"""
    ignore_file = safe_path(".antflow/antflow.ignore")
    exclude_set = set()
    
    if os.path.exists(ignore_file):
        with open(ignore_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Quitar trailing slash para consistencia
                    clean_name = line.rstrip('/')
                    
                    # Manejar patrones especiales
                    if '**/' in clean_name:
                        # Patrones recursivos como **/__pycache__/
                        pattern = clean_name.replace('**/', '*')
                        exclude_set.add(('pattern', pattern))
                    elif '*' in clean_name:
                        # Patrones con wildcards
                        exclude_set.add(('pattern', clean_name))
                    else:
                        # Nombres de directorios/archivos simples
                        exclude_set.add(('simple', clean_name))
    
    return exclude_set

def get_development_file_extensions():
    """Retorna una tupla con todas las extensiones de archivos de desarrollo"""
    return (
        # Web Development
        '.php', '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte', '.html', '.css', '.scss', '.sass', '.less',
        # Python & Data Science
        '.py', '.pyx', '.pyi', '.ipynb', '.r', '.R', '.Rmd',
        # Java & JVM
        '.java', '.kt', '.scala', '.groovy', '.clj', '.gradle', '.maven', '.pom',
        # C/C++/C#/.NET
        '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.cs', '.vb', '.fs', '.go', '.rs',
        # Mobile Development
        '.swift', '.m', '.mm', '.kt', '.dart', '.java',
        # Configuration & Data
        '.json', '.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf', '.env', '.xml',
        # Documentation & Text
        '.md', '.rst', '.txt', '.tex', '.adoc', '.doc', '.docx',
        # Build & Package
        '.dockerfile', 'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml', 
        '.makefile', 'Makefile', 'CMakeLists.txt', 'build.gradle',
        '.package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
        'requirements.txt', 'Pipfile', 'poetry.lock', 'pyproject.toml',
        'Gemfile', 'Gemfile.lock', 'Podfile', 'Podfile.lock',
        'composer.json', 'composer.lock',
        'Cargo.toml', 'Cargo.lock',
        'go.mod', 'go.sum',
        # Database & Migrations
        '.sql', '.db', '.sqlite', '.migration', '.seed',
        # Testing
        '.test.js', '.spec.js', '.test.ts', '.spec.ts', '.test.py', '_test.rb',
        '.feature', '.stories.js', '.stories.tsx',
        # CI/CD & DevOps
        '.yml', '.yaml', '.gitlab-ci.yml', '.github', 'Jenkinsfile',
        # Other Development Files
        '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
        '.rb', '.rbw', '.pl', '.pm', '.t', '.pl6',
        '.lua', '.vim', '.el', '.lisp', '.hs', '.ml', '.mli'
    )

def should_exclude(path, exclude_set, relative_to_base=""):
    """Determina si una ruta debe ser excluida basada en los patrones"""
    # Obtener el nombre base de la ruta
    basename = os.path.basename(path)
    
    for exclude_type, exclude_value in exclude_set:
        if exclude_type == 'simple':
            # Exclusión simple de nombre
            if basename == exclude_value:
                return True
        elif exclude_type == 'pattern':
            # Exclusión con patrones fnmatch
            if fnmatch.fnmatch(basename, exclude_value):
                return True
            # Para patrones como **/__pycache__/ verificar en cualquier subdirectorio
            if '**/' in exclude_value and fnmatch.fnmatch(path, exclude_value):
                return True
    
    return False

def build_tree_recursive(target, exclude_set, valid_exts, project_base, tree=None, relative_path=""):
    """Construye el árbol recursivamente manteniendo la estructura jerárquica"""
    if tree is None:
        if relative_path == ".":
            tree = Tree(f"[bold blue] Current directory[/bold blue]")
        else:
            tree = Tree(f"[bold blue] {relative_path}[/bold blue]")
    
    try:
        # Obtener todos los items en el directorio actual
        items = []
        try:
            items = os.listdir(target)
        except PermissionError:
            return tree
            
        # Separar directorios y archivos
        dirs = []
        files = []
        
        for item in items:
            item_path = os.path.join(target, item)
            if os.path.isdir(item_path):
                if not should_exclude(item_path, exclude_set):
                    dirs.append(item)
            elif os.path.isfile(item_path):
                if item.endswith(valid_exts) and not should_exclude(item_path, exclude_set):
                    files.append(item)
        
        # Ordenar: directorios primero, luego archivos
        dirs.sort()
        files.sort()
        
        # Agregar directorios recursivamente
        for d in dirs:
            dir_path = os.path.join(target, d)
            if not should_exclude(dir_path, exclude_set):
                # Crear subárbol para este directorio
                subtree = tree.add(f"[cyan]{d}/[/cyan]")
                # Llamada recursiva para construir el contenido del subdirectorio
                build_tree_recursive(dir_path, exclude_set, valid_exts, project_base, subtree, os.path.join(relative_path, d) if relative_path else d)
        
        # Agregar archivos del directorio actual
        for f in files:
            tree.add(f"[dim]{f}[/dim]")
            
    except Exception as e:
        #logging.error(f"Error building tree for {target}: {e}")
        write_log(self.name, "Error building tree", f"Error: {str(e)}")
    
    return tree

class RepoMapTool(Tool):
    name = "repo_mapper"
    description = "Shows project directory tree using Rich Console Tree. Maps current directory or a subfolder within the project (cannot access outside project)."
    inputs = {
        "subfolder": {
            "type": "string", 
            "description": "Subfolder path within the project (optional, e.g., 'src', 'utils', 'components'). Leave empty for current directory.",
            "nullable": True
        }
    }
    output_type = "string"
    
    def forward(self, subfolder: str = None):
        try:
            # Obtener el directorio base del proyecto
            from utils.tools.utils.common import PROJECT_BASE
            project_base = PROJECT_BASE
            
            # Determinar el directorio a mapear
            if subfolder and subfolder.strip():
                target = safe_path(subfolder)
            else:
                target = project_base
            
            # Validar que solo se pueda mapear dentro del proyecto actual
            
            # Verificar que la ruta esté dentro del proyecto
            if not target.startswith(project_base):
                error_msg = f" Error: The path '{subfolder}' is outside the project directory. Only mapping within '{project_base}' is allowed"
                #logging.error(f"RepoMapTool - Path outside project: {subfolder}")
                return error_msg
            
            # Cargar exclusiones por defecto y desde archivo
            default_exclude = {('.simple', '.git'), ('simple', 'vendor'), ('simple', 'node_modules'), ('simple', 'storage'), ('simple', 'bootstrap/cache'), ('pattern', '*__pycache__'), ('simple', 'venv')}
            file_exclude = load_ignore_file()
            exclude = default_exclude.union(file_exclude)
            
            # Obtener extensiones válidas
            valid_exts = get_development_file_extensions()
            
            # Construir el árbol con Rich Tree
            relative_path = os.path.relpath(target, project_base)
            tree = build_tree_recursive(target, exclude, valid_exts, project_base, None, relative_path)
            
            # Renderizar el árbol con Rich Console y capturar como texto
            from io import StringIO
            string_io = StringIO()
            capture_console = Console(file=string_io, width=80)
            
            # Imprimir el árbol al console capturado
            capture_console.print(tree)
            
            # Obtener el texto del árbol
            tree_text = string_io.getvalue()
            
            write_log(self.name, subfolder, "Tree generated with Rich Tree")
            
            # Devolver el texto del árbol en lugar de solo un mensaje
            return tree_text.strip()
            
        except Exception as e:
            # Loguear el error en errors.log
            error_msg = f"Error in RepoMapTool: {str(e)}"
            #logging.error(error_msg, exc_info=True)
            write_log(self.name, subfolder, f"Error: {str(e)}")
            return f" Error generating tree: {str(e)}"
