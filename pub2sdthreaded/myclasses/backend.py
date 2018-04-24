# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 10:22:48 2018

@author: marks
This backend handles 'all' the processing for tasks(buttons)
leaving the guiCore to just drive the gui!
"""
import threading
from unidecode import unidecode

class Backend(threading.Thread):
    """This backend handles 'all' the processing for tasks(buttons)
        leaving the guiCore to just drive the gui!"""
    def __init__(self):
        pass
    
    def run(self, qcommand, qreport):
        while True:
            acommand = qcommand.get()
            if acommand:
                #do it
                #   each button (eventually) creates a command
                #   have lookup dict which points to code,
                #   each packet in queue has 'command_string, tuple'
                #   tuple contains all ifo require for that command, is command specific
                #and report status ('stage x completed', 'command completed')
                pass
        pass

    def _add_tree(self, atuple):
        the_focus, adir_path, noTop, displayColumns, preferred, pref_char = atuple
        #lang not required, backend only deals in english messages, 
        # presentation in appropriate language is gui function
        qreport.put('Status','Unpacking' + adir_path)
        vout = ['collection', '-', '-']
        if 'TIT2' in displayColumns:
            vout.extend([self._my_unidecode(os.path.split(adir_path)[-1], preferred, pref_char),])
        vout.extend(['-' for item in self.displayColumns[2:-1]])

        thisdir = the_focus if noTop \
                            else self.tree.insert(the_focus, \
                                     index='end', values=vout, open=True, \
                                     text='collection')



    def _my_unidecode(self, text, preferred, pref_char):
        """normalize strings to avoid unicode character which won't display
           correctly or whose use in filenames may crash filesystem"""
        l = list()
        if preferred != 1:
            self.pref = list()
        #fix eng/Eng 'bug' in unidecode
        if 'ŋ' not in [v[0] for v in self.pref]:
            self.pref.append(['ŋ', 'ng', re.compile('ŋ')])
        if 'Ŋ' not in [v[0] for v in self.pref]:
            self.pref.append(['Ŋ', 'Ng', re.compile('Ŋ')])
        #scan list of preffered character/string pairs
        for kv in self.pref:# in range(0,len(text)):
            #build list of all hits in text
            l.extend([[m.start(), len(kv[0]), kv[1]] \
                       for m in kv[2].finditer(text)])
        if l:
            #now sort list of hits into sequence order
            l = sorted(l, key=lambda student: student[0])
            result = ''
            s = 0
            for ll in l:
                #from end of last match to start of new match + new match aggress
                result += ''.join([c if c.isalnum() or \
                                        c in self.pref_char else '_' \
                                    for c in unidecode(text[s:ll[0]])]) + ll[2]
                #start of match + len of match
                s = ll[0] + ll[1]
            if s < len(text):
                #from end of last match to end of string aggress
                result += ''.join([c if c.isalnum() or \
                                        c in self.pref_char else '_' \
                                        for c in unidecode(text[s:])])
            return result
        else:
            return ''.join([c if c.isalnum() or c in self.pref_char else '_' \
                            for c in unidecode(text)])
