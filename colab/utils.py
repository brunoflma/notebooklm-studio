TIMEOUTS = {
    'generate': 600,   # até 10 min — geração de relatórios e podcasts
    'artifact': 600,   # artifact wait pode demorar
    'ask':      120,   # perguntas respondem rápido
    'default':  180,   # outros comandos
}

def get_timeout(cmd):
    for prefix, seconds in TIMEOUTS.items():
        if cmd.strip().startswith(prefix):
            return seconds
    return TIMEOUTS['default']
