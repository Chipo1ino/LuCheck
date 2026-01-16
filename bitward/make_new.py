import time
from bitward.ApiWork import BitWardCl
from bitward.config_items import MASTER_PASS

def new_item_def(name_arc, passwd):
    bw = BitWardCl()
    bw.setup()
    bw.get_status()
    if not bw.unlock(MASTER_PASS):
        return
    bw.sync()
    result = bw.create_login(name_arc, passwd)
    bw.sync()
