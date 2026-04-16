"""
Hook para PyInstaller para incluir archivos de datos de LiteLLM
"""
import os
from PyInstaller.utils.hooks import collect_data_files

# Incluir archivos de datos de LiteLLM
datas = collect_data_files('litellm')

# Específicamente incluir el archivo de costos del modelo
try:
    import litellm
    import os
    cost_map_path = os.path.join(os.path.dirname(litellm.__file__), 'model_prices_and_context_window_backup.json')
    if os.path.exists(cost_map_path):
        datas.append((cost_map_path, 'litellm'))
except ImportError:
    pass
