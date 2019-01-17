import os

def get(iv_name):
    # function to get mandatory specs for an indicator 
    # and check validity of indicator specs
    # Hans Roelofsen, WEnR, 16/Jan/2019 16:08

    from sastdes import iv_definitions

    ivs = iv_definitions.get()
        
    try:
        iv_sel = ivs[iv_name]
        
        req_keys = set(['name', 'label', 'method', 'source','sum_stat', 'classes', 'relative'])
        given_keys = set([k for k, v in iv_sel.items()])
        if any([x not in req_keys for x in given_keys]):
            raise Exception('{0} is a required indicator property, but not provided for {1}'.
                            format(req_keys - given_keys, iv_name))
        
        if iv_sel['method'] not in ['categorical', 'sum_stat', 'count']:
            raise Exception('{0} is is not a valid method'.format(iv_sel['method']))
        
        if not isinstance(iv_sel['relative'], bool):
            raise Exception('Relative should be boolean, currently is {0}'.format(iv_sel['relative']))        
        
        if iv_sel['sum_stat'] not in [None, 'mean', 'min', 'max']:
            raise Exception('sum_stat should be one of None;mean;min;max, but currently is {0}'.
                            format(iv_sel['sum_stat']))
            
        if not os.path.isfile(iv_sel['source']):
            raise Exception('{0} does not seem to exist, better try again'.format(iv_sel['source']))

        return iv_sel

    except KeyError:
        raise Exception('{0} is not a recognized indicator'.format(iv_name))
    
    