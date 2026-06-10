"""
Versión anterior del simulador.

Para ejecutar la aplicación completa, usar simulador_grupo12.pyw o EJECUTAR_WINDOWS.bat
"""

import os
import runpy

if __name__ == '__main__':
    runpy.run_path(
        os.path.join(os.path.dirname(__file__), 'simulador_grupo12.pyw'),
        run_name='__main__',
    )
