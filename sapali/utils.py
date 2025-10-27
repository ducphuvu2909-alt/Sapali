def human_sources(hits):
    return '\n'.join([f'[{i+1}] score={s:.3f} doc#{d} pos{p}' for i,(s,_,d,p) in enumerate(hits)])
