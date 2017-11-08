"""
Store
"""
import sys
import re
import threading

class StoreVar:
    """ Class to store variable information """
    def __init__(self):
        self.log_func = None
        self.var_name = dict()
        self.vars = dict()
        self.var_name_lock = threading.Lock()
        self.regx_cmd = re.compile(r'^(\d+)\-var\-create \- \* \"([^\"]+)\"')
        self.regx_res = re.compile(r'^(\d+)\^done,name=\"(var\d+)\",numchild=\"([^\"]+)\",value=\"((\\\"|[^\"])+)\",type=\"([^\"]+)\"')
        self.requery_name = None
    
    def set_log_func(self, log_func):
        self.log_func = log_func

    def _log(self, string):
        if self.log_func:
            self.log_func(string)

    def _push_name(self, idx, name):
        self._log("Stored name %s:%s\n" % (idx, name))
        self.var_name_lock.acquire()
        self.var_name[idx] = name
        self.var_name_lock.release()
    
    def _pop_name(self, idx:str):
        rep = None
        self.var_name_lock.acquire()
        if idx in self.var_name:
            rep = self.var_name[idx]
            del self.var_name[idx]
        self.var_name_lock.release()
        return rep

    def input_line(self, line:str):
        mtc = self.regx_cmd.match(line)
        if mtc is None:
            return
        self._push_name(mtc.group(1), mtc.group(2))

    def output_line(self, line:str):
        self.requery_name = None
        mtc = self.regx_res.match(line)
        if mtc is None:
            return line
        name = self._pop_name(mtc.group(1))
        if name is None:
            return line
        if name[0:2]=="%%":
            name = name[2:]
            values = mtc.group(4).split()
            var = self.vars[name]
            org_val = re.escape(var["value"])
            var["value"] += " " + values[1]
            rep = var["line"]
            rep = re.sub('value=\"'+org_val+'\"', 'value=\"'+var["value"]+'\"', rep)
            return rep

        var = {
            "idx": mtc.group(1),
            "name": mtc.group(2),
            "numchild": mtc.group(3),
            "value": mtc.group(4),
            "type": mtc.group(6),
            "line": line
        }
        self.vars[name] = var
        self._log("Stored var %s:%s\n" % (name, var["type"]))
        if var["type"][0:6]!="char [" and var["type"][0:15]!="unsigned char [":
            return line
        
        self.requery_name = name
        return None
        
    def get_requery(self):
        name = self.requery_name
        var = self.vars[name]
        query = var["idx"] + "-var-create - * \"(char *)" + name  + '\"\n'
        self._push_name(var["idx"], "%%" + name)
        return query

if __name__ == '__main__':
    def log(string):
        sys.stdout.write(string)

    STV = StoreVar()
    STV.set_log_func(log)
    line = r'1087-var-create - * "mrph"' + "\n"
    STV.input_line(line)
    line = r'1087^done,name="var33",numchild="12",value="{...}",type="MRPH",thread-id="1",has_more="0"' + "\n"
    line = STV.output_line(line)
    line = r'1085-var-create - * "mrph.midasi"' + "\n"
    STV.input_line(line)
    line = r'1085^done,name="var32",numchild="129",value="[129]",type="unsigned char [129]",thread-id="1",has_more="0"' + "\n"
    line = STV.output_line(line)
    q = STV.get_requery()
    print(q)
    line = r'1085^done,name="var32",numchild="129",value="0x12345678 \"hogehoge\"",type="char *",thread-id="1",has_more="0"' + "\n"
    line = STV.output_line(line)
