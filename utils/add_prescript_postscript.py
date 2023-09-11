def pad_prescript_postscript(body: str) -> str:
    with open('configs/prescript.txt', 'rb') as f:
        prescript = f.read().decode('euc-kr').rstrip()
    
    with open('configs/postscript.txt', 'rb') as f:
        postscript = f.read().decode('euc-kr').rstrip()
    
    add_prescript = prescript + '\n\n' + body if prescript else body
    finalized_text = add_prescript + '\n\n' + postscript if postscript else add_prescript
    return finalized_text