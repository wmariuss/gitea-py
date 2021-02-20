import yaml
from cerberus import Validator

from giteapy.exceptions import ConfigValidationExceptions


class ConfigValidation(object):
    def __init__(self):
        pass

    def _parse_config(self, file):
        configs = None
        with open(file, 'r') as cfg:
            try:
                content = yaml.load(cfg, Loader=yaml.FullLoader)
                configs = content
            except yaml.YAMLError as exc:
                raise ConfigValidationExceptions(exc)
        return configs

    def data_validation(self, data={}):
        schema_config = '''
        gitea:
          type: dict
          schema:
            add:
              type: dict
              schema:
                organizations:
                    type: list
                teams:
                    type: dict
                permissions:
                    type: dict
                repos:
                    type: dict
            remove:
              type: dict
              schema:
                repos:
                    type: dict
                members:
                    type: dict
                teams:
                    type: dict
                organizations:
                    type: list
        '''

        schema_config_load = yaml.load(schema_config, Loader=yaml.FullLoader)
        content = data
        v = Validator(schema_config_load)
        status = v.validate(content)

        if not status:
            raise ConfigValidationExceptions("Invalid syntax: {0}".format(str((v.errors))))
        else:
            return status
