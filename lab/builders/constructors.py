import logging
from typing import Dict, List

import streamlit as st
from builders.interfaces import Constructor
from components.actions.actions import BuildPromptAction
from components.actions.callback_actions import (
    EnableGenerateParamPopUpCallBackAction,
    GenerateParamDescriptionCallBackAction, InferenceCallBackAction,
    SavePromptCallBackAction)
from components.data.base import PromptItem
from components.layouts.layouts import GenerateParamLayout
from components.templates.templates import (ResponseTemplate,
                                            SelectBarTemplate,
                                            TextPromptTemplate)


class PromptLabConstructor(Constructor):

    def __init__(self):
        super().__init__()
        self.generate_param_action = GenerateParamDescriptionCallBackAction()
        self.generate_param_layout = GenerateParamLayout()
        self.query_template = TextPromptTemplate()
        self.inference_action = InferenceCallBackAction()
        self.response_template = ResponseTemplate()
        
    def __call__(
        self, 
        session_name,
        inference_action_config, 
        generate_param_action_config,
        generate_param_layout_config, 
        query_template_config,
        response_template_config
    ):
        """
        Render the block for the prompt lab.
        """

        response_key = "response"

        self.setup_title_and_description(
            "提示詞實驗室",
            "用來測試大語言模型的回覆能力"
        )

        self.setup_key(session_name, response_key, "")

        with st.sidebar:
            st.markdown("#### 選擇模型參數")
            self.generate_param_action(**generate_param_action_config)
            params = self.generate_param_layout(
                **generate_param_layout_config
            )

        query = self.query_template(**query_template_config)
        
        kwargs = inference_action_config
        kwargs.update({
            "prompt": query, **params
        })
        
        response = self.inference_action(**kwargs)
        self.update_key(session_name, response_key, response)

        response_template_config.update({
            "key": self.get_key_name(session_name, response_key)
        })
        self.response_template(**response_template_config)


class AskPromptConstructor(Constructor):

    prompt_tags = [
        "詢問問題",
        "問題答案",
        "引導規則"
    ]

    def __init__(self):
        super().__init__()
        self.enable_param_action = EnableGenerateParamPopUpCallBackAction()
        self.generate_param_action = GenerateParamDescriptionCallBackAction()
        self.generate_param_layout = GenerateParamLayout()
        self.selectbar_template = SelectBarTemplate()
        self.query_template = TextPromptTemplate()
        self.answer_template = TextPromptTemplate()
        self.instructions_template = TextPromptTemplate()
        self.build_prompt_action = BuildPromptAction()
        self.inference_action = InferenceCallBackAction()
        self.response_template = ResponseTemplate()
        self.save_prompt_action = SavePromptCallBackAction()
        self.total_prompt_template = ResponseTemplate()

    def _update_disable_key(self, data: Dict[str, Dict[str, str]]):
        # disable the template 
        return {
            key: {**val, "disabled": True} 
            for key, val in data.items()
        }

    def _prepare_prompt_items(
        self, options: List[str], mapping: Dict[str, str]
    ) -> List[PromptItem]:
        
        return [
            PromptItem(
                name=option, 
                content=mapping[option],
                order=i + 1,
                need_parse=False,
                placehold=False if option == self.prompt_tags[2] else True
            )
            for i, option in enumerate(options)
        ]
            
    def __call__(
        self, 
        session_name,
        enable_param_action_config,
        inference_action_config, 
        generate_param_action_config,
        generate_param_layout_config,
        selectbar_template_config,
        query_template_config,
        answer_template_config,
        build_prompt_action_config,
        instructions_template_config,
        response_template_config,
        save_prompt_action_config,
        total_prompt_template_config
    ):
        """
        Render the block for the ask prompt.
        """

        response_key = "response"
        enable_param_key = "enable_params_adjustment"
        ask_total_prompt = "ask_total_prompt"

        self.setup_title_and_description(
            "猜你想問 Prompt 測試",
            "生成追問問題。"
        )

        self.setup_key(session_name, response_key, "")
        self.setup_key(session_name, enable_param_key, False)
        self.setup_key(session_name, ask_total_prompt, "")

        with st.sidebar:
            st.markdown("#### 選擇模型參數")
            self.generate_param_action(**generate_param_action_config)
            enable_param_action_config.update({
                "session_state": self.session_state,
                "key": self.get_key_name(session_name, enable_param_key)
            })
            self.enable_param_action(**enable_param_action_config)

            if self.get_key_value(session_name, enable_param_key):
                params = self.generate_param_layout(
                    **generate_param_layout_config
                )
            else:
                generate_param_layout_config = self._update_disable_key(
                    generate_param_layout_config
                )
                params = self.generate_param_layout(
                    **generate_param_layout_config
                )

        selectbar_template_config.update({
            "options": self.prompt_tags, "value": self.prompt_tags
        })
        
        selection = self.selectbar_template(**selectbar_template_config)

        logging.info(selection)
        col1, col2 = st.columns(2)

        with col1:
            query = self.query_template(**query_template_config)
            instructions = self.instructions_template(
                **instructions_template_config
            )

        with col2:
            answer = self.answer_template(**answer_template_config)

        build_prompt_action_config.update({
            "ordered_prompt_list": self._prepare_prompt_items(
                selection, {
                    self.prompt_tags[0]: query,
                    self.prompt_tags[1]: answer,
                    self.prompt_tags[2]: instructions
                }
            )
        })

        prompts = self.build_prompt_action(
            **build_prompt_action_config
        )
        logging.info(prompts)
        prompt = prompts["prompt"]
        prompt_with_placehold = prompts["prompt_with_placeholder"]

        kwargs = inference_action_config
        kwargs.update({
            "prompt": prompt, **params
        })
        
        response = self.inference_action(**kwargs)
        self.update_key(session_name, response_key, response)

        response_template_config.update({
            "key": self.get_key_name(session_name, response_key)
        })

        self.update_key(session_name, ask_total_prompt, prompt)
        total_prompt_template_config.update({
            "key": self.get_key_name(session_name, ask_total_prompt)
        })

        col3, col4 = st.columns(2)
        with col3:
            self.response_template(**response_template_config)

        with col4:
            if self.get_key_value(session_name, response_key):
                self.total_prompt_template(
                    **total_prompt_template_config
                )

        col5, _, _, _ = st.columns(4)
        with col5:
            save_prompt_action_config.update({
                "prompt_with_placehold": prompt_with_placehold,
            })
            self.save_prompt_action(**save_prompt_action_config)