import time
from bitward.ApiWork import BitWardCl
from bitward.config_items import MASTER_PASS

def find_item_by_username_flexible(username_search, exact_match=False):
    bw = BitWardCl()
    bw.setup()
    if not bw.unlock(MASTER_PASS):
        return None

    all_items = bw.list_items("")
    
    if not all_items:
        return None
    
    matches = []
    
    for item in all_items:
        if item.get('type') == 1: 
            login = item.get('login', {})
            item_username = login.get('username', '')
            
            if not item_username:
                continue
            
            if exact_match:
                if item_username == username_search:
                    matches.append(item)
            else:
                if username_search.lower() in item_username.lower():
                    matches.append(item)
    
    if not matches:
        return None
    password = matches[0]['login'].get('password')
    if password:
        return password
    
    return None