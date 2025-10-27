import pandas as pd
def to_excel_bytes(df: pd.DataFrame)->bytes:
    from io import BytesIO
    out=BytesIO()
    with pd.ExcelWriter(out, engine='xlsxwriter') as w: df.to_excel(w, index=False, sheet_name='PurchasePlan')
    return out.getvalue()
