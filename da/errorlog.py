from datetime import datetime as dt


def errorlog(reason, reg_addr, field, ODF=None, error=None):
    f = open('./err/'+field,'a')
    f.write('{}: {}, {}, {}\n'.format(dt.now(), reason, reg_addr, ODF))
    if error: f.write('{}\n\n\n'.format(error))
    f.close()



