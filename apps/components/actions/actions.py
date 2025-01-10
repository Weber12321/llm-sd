from typing import Dict, List

import requests
from components.actions.interfaces import Action
from components.data.base import PromptItem
from settings.configs.prompts import prompt_placeholder


class QueryAction(Action):
    
    def resonpse_parser(self, response):
        return response.json().get('results', [])

    def function(self, query_api_path, request_data, timeout):
        """
        Construct a number input slider with the given label and value.
        """
        response = requests.post(
            url=query_api_path,
            json=request_data,
            timeout=timeout
        )
        if response.status_code != 200:
            response.raise_for_status()
        
        return self.resonpse_parser(response)


class BuildPromptAction(Action):

    def _prompt_with_placeholder(
        self, 
        ordered_prompt_list: List[PromptItem],
        separator: str = "\n\n"
    ) -> str:
        prompt_ = ""
        for item in ordered_prompt_list:
            if item.placehold:
                placehold = prompt_placeholder[item.name]
                prompt_ = prompt_ + separator + placehold
            else:
                prompt_ = prompt_ + separator + item.content

        return prompt_

    def _prompt(
        self, ordered_prompt_list: List[PromptItem]
    ) -> List[Dict[str, int | str]]:
        prompt_items = []
        for item in ordered_prompt_list:
            if item.need_parse:
                item.name = "document"
            prompt_items.append({
                "name": item.name,
                "content": item.content,
                "order": item.order,
            })

        if not prompt_items:
            raise ValueError('No prompt items selected...')
        
        return prompt_items
    
    def function(
        self, 
        build_prompt_api: str, 
        ordered_prompt_list: List[PromptItem], 
    ) -> Dict[str, str]:
        
        if build_prompt_api is None:
            raise ValueError(
                "build_prompt_api cannot be set to None "
                "if if_parse_search_output is True"
            ) 
       
        prompt_with_placeholder = self._prompt_with_placeholder(
            ordered_prompt_list
        )

        response = requests.post(
            url=build_prompt_api,
            json={
                "items": self._prompt(ordered_prompt_list)
            },
            timeout=120
        )

        if response.status_code != 200:
            response.raise_for_status()

        prompt = response.json().get('prompt', '')

        return {
            "prompt": prompt, 
            "prompt_with_placeholder": prompt_with_placeholder
        }

        