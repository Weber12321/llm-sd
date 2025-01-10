from components.templates.templates import NumberParameterTemplate
from components.layouts.interfaces import Layout


class GenerateParamLayout(Layout):

    def __init__(self):
        self.top_p_template = NumberParameterTemplate()
        self.top_k_template = NumberParameterTemplate()
        self.temperature_template = NumberParameterTemplate()
        self.max_token_template = NumberParameterTemplate()

    def __call__(
        self, top_p_config, top_k_config, temperature_config, max_token_config
    ):
        """
        Render the layout for generating parameters.
        """
        top_p = self.top_p_template(**top_p_config)
        top_k = self.top_k_template(**top_k_config)
        temperature = self.temperature_template(**temperature_config)
        max_token = self.max_token_template(**max_token_config)

        return {
            "top_p": top_p,
            "top_k": top_k,
            "temperature": temperature,
            "max_token": max_token
        }
        
        


        
        
