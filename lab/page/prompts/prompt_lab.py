from builders.constructors import PromptLabConstructor
from settings.configs.components import (generate_param_action_config,
                                         generate_param_layout_config,
                                         inference_action_config,
                                         query_template_config,
                                         response_template_config)


def get_config():
    return {
        'session_name': 'prompt_lab',
        'inference_action_config': inference_action_config,
        'generate_param_action_config': generate_param_action_config,
        'generate_param_layout_config': generate_param_layout_config,
        'query_template_config': query_template_config,
        'response_template_config': response_template_config
    }


def main():
    mapping = get_config()
    prompt_lab = PromptLabConstructor()
    prompt_lab(**mapping)


main()