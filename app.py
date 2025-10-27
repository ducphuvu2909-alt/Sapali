import os, io, json
import streamlit as st
import pandas as pd
from sapali.settings import DB_PATH, CHUNK_SIZE, CHUNK_OVERLAP, CHAT_MODEL
from sapali.llm import embed_texts, chat
from sapali.drive import build_drive_from_json, list_files_in_folder, download_file_bytes, export_google_doc_as_text
from sapali.chunker import chunk_text
from sapali.vectorstore import VectorStore
from sapali.rag import answer_query
from sapali.history import export_json as history_export
from sapali.po_calc import suggest_mapping as po_map, compute as po_compute, export_excel as po_export
from sapali.utils import human_sources

st.set_page_config(page_title='SapaliAI Enterprise', page_icon='🤖', layout='wide')
st.title('SapaliAI Enterprise')
st.caption('ChatGPT + RAG + Google Drive ingest + PO calculator + History export')

with st.sidebar:
    st.subheader('🔐 API & Model')
    api_key = st.text_input('OPENAI_API_KEY', value=os.getenv('OPENAI_API_KEY',''), type='password')
    chat_model = st.text_input('Chat model', value=CHAT_MODEL)
    session_id = st.text_input('Session ID', value='default-session')
    st.divider()
    st.subheader('Ingest params')
    chunk_size = st.number_input('Chunk size', value=CHUNK_SIZE, step=200)
    chunk_overlap = st.number_input('Chunk overlap', value=CHUNK_OVERLAP, step=50)
    st.caption(f'DB: {DB_PATH}')

db = VectorStore(DB_PATH)

tab_chat, tab_data, tab_po, tab_hist = st.tabs(['💬 Chat', '📁 Data (Drive ingest)', '📦 PO Calculator', '📝 History'])

with tab_chat:
    st.subheader('Chat with RAG')
    q = st.text_input('Câu hỏi')
    if st.button('Gửi', key='ask'):
        if not api_key:
            st.error('Nhập OPENAI_API_KEY ở Sidebar.')
        elif not q.strip():
            st.warning('Nhập câu hỏi.')
        else:
            ans, hits = answer_query(db, q, api_key=api_key, model=chat_model)
            st.write(ans)
            with st.expander('Nguồn tham chiếu'):
                st.text(human_sources(hits))

with tab_data:
    st.subheader('Google Drive ingest')
    creds_file = st.file_uploader('credentials.json (Service Account)', type=['json'])
    folder_id = st.text_input('Folder ID')
    if st.button('Liệt kê file'):
        if not creds_file or not folder_id: st.warning('Thiếu credentials.json hoặc Folder ID')
        else:
            creds_json = json.load(creds_file)
            drive = build_drive_from_json(creds_json)
            files = list_files_in_folder(drive, folder_id)
            st.session_state['drive_files'] = files
            st.write(files if files else 'Không có file.')
    if st.button('Ingest toàn bộ folder'):
        files = st.session_state.get('drive_files')
        if not files: st.warning('Chưa liệt kê file.')
        else:
            creds_json = json.load(creds_file)
            drive = build_drive_from_json(creds_json)
            ingested=0
            for f in files:
                name, mime, fid, modified = f['name'], f['mimeType'], f['id'], f.get('modifiedTime','')
                try:
                    if mime.startswith('application/vnd.google-apps'):
                        text = export_google_doc_as_text(drive, fid)
                    else:
                        data = download_file_bytes(drive, fid)
                        if name.lower().endswith('.pdf'):
                            from pdfminer.high_level import extract_text
                            text = extract_text(io.BytesIO(data))
                        elif name.lower().endswith('.docx'):
                            import mammoth
                            text = mammoth.convert_to_markdown(io.BytesIO(data)).value
                        else:
                            try: text = data.decode('utf-8', errors='ignore')
                            except: text = data.decode('latin-1', errors='ignore')
                    chunks = chunk_text(text, chunk_size=chunk_size, overlap=chunk_overlap)
                    embs = embed_texts(chunks, api_key=api_key)
                    doc_id = db.add_document(fid, name, mime, modified)
                    db.add_chunks(doc_id, [(i,ch,embs[i]) for i,ch in enumerate(chunks)])
                    ingested+=1
                except Exception as e:
                    st.error(f'{name}: {e}')
            st.success(f'Đã ingest {ingested} file.')
            st.write(db.list_docs())

with tab_po:
    st.subheader('Upload PO (.xlsx)')
    up = st.file_uploader('PO Excel', type=['xlsx'], key='po')
    if up is not None:
        df = pd.read_excel(up)
        st.session_state['po_df'] = df
        st.dataframe(df.head(20), use_container_width=True)
        st.session_state['po_map'] = po_map(df.columns)
        st.info(f'Mapping gợi ý: {st.session_state["po_map"]}')
    safety = st.number_input('Safety stock (%)', value=10.0, min_value=0.0, max_value=100.0, step=1.0)
    default_moq = st.number_input('MOQ mặc định', value=0, min_value=0, step=1)
    if st.button('Tính Purchase Plan'):
        if 'po_df' not in st.session_state: st.warning('Chưa có PO.')
        else:
            plan = po_compute(st.session_state['po_df'], st.session_state['po_map'], safety_pct=safety, default_moq=default_moq)
            st.session_state['plan'] = plan
            st.dataframe(plan, use_container_width=True)
    if 'plan' in st.session_state:
        data = po_export(st.session_state['plan'])
        st.download_button('Tải PurchasePlan.xlsx', data=data, file_name='PurchasePlan.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

with tab_hist:
    st.subheader('Xuất lịch sử hội thoại (JSON)')
    session_id = st.text_input('Session cần xuất', value='default-session', key='hist_sid')
    if st.button('Xuất JSON'):
        from sapali.vectorstore import VectorStore
        vs = VectorStore(DB_PATH)
        js = history_export(vs, session_id)
        st.download_button('Tải conversation.json', data=js.encode('utf-8'), file_name='conversation.json', mime='application/json')
    st.write('Tài liệu đã ingest:')
    st.write(db.list_docs())
