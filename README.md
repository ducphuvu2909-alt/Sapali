# SapaliAI Enterprise — RAG + Drive Ingest + Chat + PO Calculator

Trợ lý AI độc lập: ChatGPT + RAG, tự đọc Google Drive (Service Account), lưu lịch sử, tính mua hàng & xuất Excel.

## Run
```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env                         # hoặc tạo file .env
streamlit run app.py
```
