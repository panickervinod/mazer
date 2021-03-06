
# if this looks a lot like reimplement 'logging', that is
# true...

import logging

log = logging.getLogger(__name__)

INFO_LEVEL = {
    'prefix': '',
    'log_level': logging.INFO
}

DISPLAY_LEVEL_MAP = {
    'warning': {
        'prefix': 'WARNING',
        'log_level': logging.WARNING
    },
    'info': INFO_LEVEL
}


def stdout_display_callback(*args, **kwargs):
    level_arg = kwargs.pop('level', None)
    level_prefix = DISPLAY_LEVEL_MAP.get(level_arg, INFO_LEVEL)['prefix']

    print('%s' % level_prefix, args)


# will log whatever is display with display callback to the ansible_galaxy.display logger
def log_display_callback(*args, **kwargs):
    level_arg = kwargs.pop('level', None)
    log_level = DISPLAY_LEVEL_MAP.get(level_arg, INFO_LEVEL)['log_level']
    log.log(log_level, ''.join(args), extra={'display_args': args})


def display_callback(*args, **kwargs):
    stdout_display_callback(args, kwargs)
    log_display_callback(args, kwargs)


def null_display_callback(*args, **kwargs):
    pass
