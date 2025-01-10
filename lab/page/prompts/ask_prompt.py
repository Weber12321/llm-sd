from builders.constructors import AskPromptConstructor
from settings.configs.components import (answer_template_config,
                                         build_prompt_action_config,
                                         enable_param_action_config,
                                         generate_param_action_config,
                                         generate_param_layout_config,
                                         inference_action_config,
                                         instructions_template_config,
                                         query_template_config,
                                         response_template_config,
                                         save_prompt_action_config,
                                         selectbar_template_config,
                                         total_prompt_template_config)



def get_config():
    query_template_config.update({
        "value": """請幫我將演講內容，整理成可以報告的文章：

        胡德民 遠傳電信資訊長暨執行副總經理
        「找痛點，而不是找亮點」，舉例：OCR單據 > RPA

        什麼是容易成功的特質？
        所有人都需要對於AI技術理解，基於AI技術上可以解決什麼痛點。領導者必須了解新技術可以怎麼用。

        96~07年泡沫，Token成本10倍在下降，商業模式零界點快到了嗎？
        取決於要投入的規模，投入成本高的時候，執行者不敢做，企業害怕失敗。怕投入成本後沒有結果。沒有90%的把握，經營者無法下定論。但，老闆要知道要有失敗的風險意識，不要過度投入，從小規模去驗證；先從公有雲，再到Ownground的LLM。

        每投入一塊錢有多少Interner，有可獲利商業模式是何時？
        已經有企業開始獲利，新創AI應用產生利潤，開始資本支出投資算力。技術大部分都一樣，但應用比較有創意。

        從法律看繁體中文語言模型需要Mixure Experts？
        知道怎麼看資料才知道有邏輯，用判決書去測試。

        """
    })

    answer_template_config.update({
        "value": """報告文章：AI技術應用與企業轉型挑戰
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
        
        """
    })

    instructions_template_config.update({
        "value": "請綜合問題和潤飾回覆的答案做統整，並生成出三個延伸問題。"
    })

    save_prompt_action_config.update({
        "prompt_form_prompt_type": "recommendation", 
    })

    return {
        "session_name": "ask_prompt",
        "enable_param_action_config": enable_param_action_config,
        "inference_action_config": inference_action_config,
        "generate_param_action_config": generate_param_action_config,
        "generate_param_layout_config": generate_param_layout_config,
        "selectbar_template_config": selectbar_template_config,
        "query_template_config": query_template_config,
        "answer_template_config": answer_template_config,
        "instructions_template_config": instructions_template_config,
        "build_prompt_action_config": build_prompt_action_config,
        "response_template_config": response_template_config,
        "save_prompt_action_config": save_prompt_action_config,
        "total_prompt_template_config": total_prompt_template_config
    }


def main():
    mapping = get_config()
    ask_prompt = AskPromptConstructor()
    ask_prompt(**mapping)


main()