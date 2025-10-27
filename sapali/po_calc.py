import pandas as pd, numpy as np
from .export_excel import to_excel_bytes
def suggest_mapping(cols):
    lower={c.lower():c for c in cols}
    return {'Item':lower.get('item') or lower.get('code') or lower.get('sku') or list(cols)[0],
            'QtyNeeded':lower.get('qtyneeded') or lower.get('qty') or lower.get('quantity') or list(cols)[1],
            'StockOnHand':lower.get('stockonhand') or lower.get('stock') or lower.get('onhand') or list(cols)[2],
            'LeadTimeDays':lower.get('leadtimedays') or lower.get('leadtime'),
            'MOQ':lower.get('moq')}
def compute(df, m, safety_pct=10.0, default_moq=0):
    item=df[m['Item']].astype(str)
    need=pd.to_numeric(df[m['QtyNeeded']],errors='coerce').fillna(0).astype(float)
    stock=pd.to_numeric(df[m['StockOnHand']],errors='coerce').fillna(0).astype(float)
    lt=pd.to_numeric(df[m['LeadTimeDays']],errors='coerce').fillna(0).astype(int) if m.get('LeadTimeDays') and m['LeadTimeDays'] in df.columns else None
    moq=pd.to_numeric(df[m['MOQ']],errors='coerce').fillna(0).astype(int) if m.get('MOQ') and m['MOQ'] in df.columns else None
    safety=(need*(1+safety_pct/100)).round(0); raw=(safety-stock).clip(lower=0)
    purchase= np.where(raw>0, np.maximum(raw, moq) if moq is not None else np.maximum(raw, default_moq), 0).astype(int)
    out={'Item':item,'QtyNeeded':need.astype(int),'StockOnHand':stock.astype(int),'Safety(%)':float(safety_pct),'PurchaseQty':purchase}
    if lt is not None: out['LeadTimeDays']=lt
    if moq is not None: out['MOQ']=moq.astype(int)
    return pd.DataFrame(out).sort_values(['PurchaseQty','Item'],ascending=[False,True]).reset_index(drop=True)
def export_excel(df): return to_excel_bytes(df)
