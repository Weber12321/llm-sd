import requests
import streamlit as st
from components.actions.interfaces import CallBackAction
from components.templates.templates import (TextInputTemplate,
                                            TextPromptTemplate)


class InferenceCallBackAction(CallBackAction):
    
    def resonpse_parser(self, response):
        return response.json().get('results', '').get('text', '')

    def function(
        self, 
        llm_api_path,
        prompt,
        top_p,
        top_k,
        temperature,
        max_token
    ):
        """
        Construct a text area with the given label and key for response.
        """
        response = requests.post(
            url=llm_api_path,
            json={
                "query": prompt,
                "top_p": top_p,
                "top_k": top_k,
                "temperature": temperature,
                "max_token": max_token
            },
            timeout=600
        )

        if response.status_code != 200:
            response.raise_for_status()

        return self.resonpse_parser(response)


class GenerateParamDescriptionCallBackAction(CallBackAction):

    def function(self, title: str, markdown: str) -> None:
        
        @st.dialog(title)
        def popup():
            st.markdown(markdown)
        
        popup()


class EnableGenerateParamPopUpCallBackAction(CallBackAction):

    def enable_adjust_param(
        self, session_state: st.session_state, key: str
    ) -> None:
        session_state[key] = True

    def function(
        self, 
        title: str, 
        warning_message: str,
        session_state: st.session_state,
        key: str
    ) -> None:
        
        @st.dialog(title)
        def popup():
            st.warning(warning_message, icon="⚠️")
            if st.button(
                "確認調整",
                on_click=self.enable_adjust_param,
                kwargs={"session_state": session_state, "key": key},
                type="primary",
            ):
                st.rerun()
        
        popup()


class SavePromptCallBackAction(CallBackAction):
    def __init__(self):
        self.name = TextInputTemplate()
        self.description = TextPromptTemplate()

    def function(
        self, 
        prompt_create_api: str, 
        prompt_form_title: str,
        prompt_form_button_label: str,
        prompt_form_button_type: str,
        prompt_form_prompt_type: str,
        prompt_form_name_config: dict,
        prompt_form_description_config: dict,
        prompt_with_placehold: str
    ):
        
        @st.dialog(prompt_form_title)
        def form(
            prompt_create_api: str, 
            prompt_form_title: str,
            prompt_form_button_label: str,
            prompt_form_button_type: str,
            prompt_form_prompt_type: str,
            prompt_form_name_config: dict,
            prompt_form_description_config: dict,
            prompt_with_placehold: str
        ) -> None:
            
            with st.form(prompt_form_title):
                name = self.name(**prompt_form_name_config)
                description = self.description(
                    **prompt_form_description_config
                )
                submitted = st.form_submit_button(
                    prompt_form_button_label, type=prompt_form_button_type)
                if submitted:
                    response = requests.post(
                        url=prompt_create_api,
                        json={
                            "name": name,
                            "prompt": prompt_with_placehold,
                            "prompt_type": prompt_form_prompt_type,
                            "description": description
                        },
                        timeout=120
                    )
                    if response.status_code != 201:
                        st.error("Prompt 儲存失敗！")
                    else:
                        st.success("Prompt 儲存成功！")
                        st.rerun()

        form(
            prompt_create_api, 
            prompt_form_title,
            prompt_form_button_label,
            prompt_form_button_type,
            prompt_form_prompt_type,
            prompt_form_name_config,
            prompt_form_description_config,
            prompt_with_placehold
        )
