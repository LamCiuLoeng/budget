# -*- coding: utf-8 -*-
"""WSGI environment setup for budget."""

from budget.config.app_cfg import base_config

__all__ = ['load_environment']

#Use base_config to setup the environment loader function
load_environment = base_config.make_load_environment()

from tg import response

_load_environment = load_environment

def load_environment(*args):
    _load_environment(*args)
    _render_genshi = base_config.render_functions.genshi

    def render_genshi(*args, **kwargs):
        if response.content_type == 'text/xml':
            kwargs['method'] = 'xml'
        return _render_genshi(*args, **kwargs)

    base_config.render_functions.genshi = render_genshi