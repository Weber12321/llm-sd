import os
from .placeholder import Placeholder

# 呼叫 LLM 模型推論 API
inference_action_config = {
    # "label": "生成回覆",
    # "button_type": "primary",
    "llm_api_path": "http://localhost:8001/api/v0/llm/rag",
    "prompt": Placeholder.QUERY,
    "top_p": Placeholder.GENERATE_TOP_P,
    "top_k": Placeholder.GENERATE_TOP_K,
    "temperature": Placeholder.GENERATE_TEMPERATURE,
    "max_token": Placeholder.GENERATE_MAX_TOKEN,
    "response_key": Placeholder.GENERATE_RESPONSE,
}

# 模型參數說明模板
generate_param_action_config = {
    "label": "模型生成參數說明",
    "button_type": "primary",
    "title": "模型生成參數說明",
    "markdown": """
    + Temperature: 決定模型輸出文字的機率分佈的樣態。設定越大分佈樣態越平滑可能性越大，反之越趨近於單一。  
    + Top_k: 控制模型生成的候選文字總量，值越高則候選越多，增加越多的可能性。建議設定 40-100.   
    + Top_p: 該參數為控制候選文字的機率加總，取前幾個機率分數加總為 top_p 值的候選文字。top_p 越大則可能性越大，反之越精確。  
    + Max_token: 生成 token 的數量上限，超過上限則生成停止。會影響模型生成效能。  
    
    建議先由 temperature 開始調整，再來是 top_p 和 top_k，最後再調整 max_token。
    """
}

# 模型參數設定模板
generate_param_layout_config = {
    "top_p_config": {
        "label": "Top-p",
        "value": 0.50,
        "min_value": 0.01,
        "max_value": 1.0,
        "step": 0.01,
        "format": "%.2f",
        "response_key": Placeholder.GENERATE_TOP_P
    },
    "top_k_config": {
        "label": "Top-k",
        "value": 50,
        "min_value": 1,
        "max_value": 100,
        "step": 1,
        "response_key": Placeholder.GENERATE_TOP_K
    },
    "temperature_config": {
        "label": "Temperature",
        "value": 0.50,
        "min_value": 0.01,
        "max_value": 1.0,
        "step": 0.01,
        "format": "%.2f",
        "response_key": Placeholder.GENERATE_TEMPERATURE
    },
    "max_token_config": {
        "label": "Max token",
        "value": 1000,
        "min_value": 1,
        "max_value": 8000,
        "step": 1,
        "response_key": Placeholder.GENERATE_MAX_TOKEN
    },
}

# 問題模板
query_template_config = {
    "label": "輸入要潤飾的問題",
    "value": "請問我要如何請特休？",
    "height": 300,
    "response_key": Placeholder.QUERY
}

# 回答模板
answer_template_config = {
    "label": "請輸入要潤飾的答案",
    "value": """
    報告文章：AI技術應用與企業轉型挑戰
        演講者：胡德民，遠傳電信資訊長暨執行副總經理

        1. 尋找痛點，非亮點
        胡德民強調企業在導入AI技術時，應專注於解決實際業務痛點，而非只關注技術亮點。他以「OCR單據處理」與「RPA」(自動化流程機器人)為例，指出這些技術的目的是解決業務效率與精準度的問題，而非單純展示技術創新。

        2. 成功導入AI的關鍵特質
        胡德民認為，成功的企業必須具備全面理解AI技術的能力。這並不僅限於技術人員，而是應該推廣至所有組織成員。企業的領導者更需要具備一個重要的特質：了解新技術如何解決企業問題。他強調，技術的應用最終應指向業務痛點的解決，而非盲目追求技術發展。

        3. 技術變革與商業模式轉型的挑戰
        針對1996至2007年的科技泡沫，胡德民回顧了當時的技術成本下降現象，如Token成本的十倍下降，並討論了商業模式變革的臨界點是否即將到來。他指出，這取決於企業投入的規模。當投入成本過高，且成功機率不確定時，企業往往不敢採取行動，經營者也會害怕失敗。因此，他建議企業主應具備風險意識，避免過度投入，並透過小規模驗證的方式來測試新技術的可行性。胡德民提出了從公有雲入手，逐步轉向Ownground本地化大型語言模型（LLM）的策略。

        4. 商業模式的獲利預期
        胡德民指出，AI應用已開始在企業中產生利潤，許多新創企業也因AI應用而獲利，並逐步增加對算力的資本支出。他強調，儘管技術本身的核心大多相似，企業的創新應用是其能否成功的關鍵。

        5. 法律與語言模型的應用挑戰
        胡德民提到了繁體中文語言模型的發展，特別是「混合專家系統」（Mixure of Experts）的潛在應用。他指出，企業需要理解如何解讀資料才能有效運用這些技術，並舉例說明以判決書作為測試資料，藉此驗證模型的邏輯性與準確度。

        總結
        胡德民的演講強調了AI技術導入的策略與挑戰，強調企業應聚焦痛點解決、具備風險意識、從小規模驗證技術的可行性，並認識到創新應用對商業模式轉型的重要性。繁體中文語言模型的法律應用更突顯了技術在特定領域的潛在價值。
    """,
    "height": 300,
    "response_key": Placeholder.HISTORY_ANSWER
}

# 指示模板
instructions_template_config = {
    "label": "請輸入要潤飾的指示",
    "value": "請綜合問題和潤飾回覆的答案做統整，並生成出三個延伸問題。",
    "height": 300,
    "response_key": Placeholder.INSTRUCTIONS
}

# 生成結果模板
response_template_config = {
    "label": "回應",
    "value": Placeholder.GENERATE_RESPONSE,
    "height": 300
}

# 確認調整模型參數模板
enable_param_action_config = {
    "label": "調整參數",
    "button_type": "primary",
    "title": "確認調整參數",
    "warning_message": "調整模型生成參數會影響 prompt 的實驗信度，造成前後生成結果不一致。請問您是否還執意要調整參數？"
}

# 模板選擇模板，選項記錄與 constructor，此僅記錄 label
selectbar_template_config = {
    "label": "請按照順序選擇模板",
}

# Prompt 組建功能
build_prompt_action_config = {
    "build_prompt_api": os.getenv(
        "BUILD_PROMPT_API", "http://localhost:8001/api/v0/knowledgeset/prompt"
    ),
}

save_prompt_action_config = {
    "label": "儲存 Prompt",
    "button_type": "primary",
    "prompt_create_api": os.getenv(
        "PROMPT_CREATE_API", "http://localhost:8001/api/v0/prompt/create"
    ),
    "prompt_form_title": "儲存 Prompt 表單",
    "prompt_form_button_label": "儲存",
    "prompt_form_button_type": "primary",
    "prompt_form_prompt_type": "generation", 
    "prompt_form_name_config": {
        "label": "Prompt 名稱",
        "placeholder": "請輸入 Prompt 名稱",
    },
    "prompt_form_description_config": {
        "label": "Prompt 描述",
        "value": "請輸入 Prompt 描述",
        "height": 100,
    },
}

total_prompt_template_config = {
    "label": "完整 Prompt",
    "height": 300,
}

call_llm_button_template_config = {
    "label": "生成回覆",
    "type": "primary",
}
