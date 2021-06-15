

"""Redis Helper Functions"""

def ksplit(key, mod_key=True):
    """ksplit takes a redis key of the form
       "label1:value1:label2:value2" 
       and converts it into a dictionary for easy access"""
    item_list = key.split(':')
    items = iter(item_list)
    if mod_key:
        return {x.replace('-','_'):next(items) for x in items}
    else:
        return {x:next(items) for x in items}
