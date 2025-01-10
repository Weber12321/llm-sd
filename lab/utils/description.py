import streamlit as st


@st.dialog("模型參數說明")
def generate_description() -> None:
    st.markdown(
        """
        + Temperature: 決定模型輸出文字的機率分佈的樣態。設定越大分佈樣態越平滑可能性越大，反之越趨近於單一。  
        + Top_k: 控制模型生成的候選文字總量，值越高則候選越多，增加越多的可能性。建議設定 40-100.   
        + Top_p: 該參數為控制候選文字的機率加總，取前幾個機率分數加總為 top_p 值的候選文字。top_p 越大則可能性越大，反之越精確。  
        + Max_token: 生成 token 的數量上限，超過上限則生成停止。會影響模型生成效能。  
           
        建議先由 temperature 開始調整，再來是 top_p 和 top_k，最後再調整 max_token。
        """
    )


@st.dialog("Chunk 設定說明")
def chunk_description() -> None:
    st.markdown(
        """
        點選:blue-background[:material/save:匯出知識庫]按鈕，可以下載 csv 檔案，用來更新 Chunk 內容。
           
        Chunk csv 檔案範例：
        | Chunk Id   | Text   | Metadata   | Source   |
        |------------|--------|------------|----------|
        | bEljbZMBZRXIzty3trN8 | text1  | metadata1  | source1  |

        + Chunk Id: Chunk 的編號，用來識別每個 Chunk 的唯一值 uuid，:red-background[**請勿修改**]。
        + Text: Chunk 的文字內容, 用來儲存 Chunk 的文字內容。可以編輯，不過 :red-background[**請勿刪除**]出現在內容中的圖表標示，如 `<圖>` 、`<表>`、 `<圖表>`等等。
        + Metadata: Chunk 的 Metadata，用來儲存 Chunk 的 Metadata 資訊如圖表原始資料與來源，:red-background[**請勿修改**]。
        + Source: Chunk 的來源，用來儲存 Chunk 的來源資訊，:red-background[**請勿修改**]。

        下載 csv 檔案後，請依照上述格式進行編輯，並上傳至系統，成功上傳後將會更新知識庫 index 內所有 chunk。

        > BTW 請勿修改 csv 檔案的欄位名稱和欄位格式，否則將會導致設定失敗 :smile:。   
        
        """
    )


@st.dialog("問題集檔案說明")
def questions_description() -> None:
    st.markdown(
        """
        問題集 檔案範例：
        | 問題 |
        |------------|
        | 要怎麼請病假? |
        | 一年有幾天特休? |

        *欄位title "問題" 為必填欄位，請勿刪除或修改欄位名稱。
        """
    )


@st.dialog("問題集檔案說明")
def questions_answer_description() -> None:
    st.markdown(
        """
        問題集 檔案範例：
        | 問題 | 答案 |
        |------------|------------|
        | 要怎麼請病假? | 你可以在 HR 系統上申請病假。 |
        | 一年有幾天特休? | 一年有 7 天特休。 |

        *欄位title "問題", "答案" 為必填欄位，請勿刪除或修改欄位名稱。
        """
    )
