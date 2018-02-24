# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 04:02:23 2017

@author: marks
"""

LATIN1 = "À/À, Á/Á, Â/Â, Ã/Ã, Ä/Ä, Å/Å, " + \
            "Æ/Æ, Ç/Ç, È/È, É/É, Ê/Ê, Ë/Ë, " + \
            "Ì/Ì, Í/Í, Î/Î, Ï/Ï, Ð/Ð, Ñ/Ñ, " + \
            "Ò/Ò, Ó/Ó, Ô/Ô, Õ/Õ, Ö/Ö, Ø/Ø, " + \
            "Ù/Ù, Ú/Ú, Û/Û, Ü/Ü, Ý/Ý, Þ/Þ, ß/ß,  " + \
            "à/à, á/á, â/â, ã/ã, ä/ä, å/å, " + \
            "æ/æ, ç/ç, è/è, é/é, ê/ê, ë/ë, " + \
            "ì/ì, í/í, î/î, ï/ï, ð/ð, ñ/ñ, " + \
            "ò/ò, ó/ó, ô/ô, õ/õ, ö/ö, ø/ø, " + \
            "ù/ù, ú/ú, û/û, ü/ü, ý/ý, þ/þ, ÿ/ÿ"

TRIM_IT = {'digits':'0123456789', \
           'alphanumerics':'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'\
           }

PICTURE_TYPE = {\
                'OTHER':0, \
                'FILE_ICON':1, \
                'OTHER_FILE_ICON':2, \
                'COVER_FRONT':3, \
                'COVER_BACK':4, \
                'LEAFLET_PAGE':5, \
                'MEDIA':6, \
                'LEAD_ARTIST':7, \
                'ARTIST':8, \
                'CONDUCTOR':9, \
                'BAND':10, \
                'COMPOSER':11, \
                'LYRICIST':12, \
                'RECORDING_LOCATION':13, \
                'DURING_RECORDING':14, \
                'DURING_PERFORMANCE':15, \
                'SCREEN_CAPTURE':16, \
                'FISH':17, \
                'ILLUSTRATION':18, \
                'BAND_LOGOTYPE':19, \
                'PUBLISHER_LOGOTYPE':20\
                }

TF_TAGS = ['MVNM', 'TALB', 'TCOM', 'TCON', 'TCOP', \
                                 'TCMP', 'TDAT', 'TDEN', 'TDES', 'TKWD', \
                                 'TCAT', 'TDLY', 'TDOR', 'TDRC', 'TDRL', \
                                 'TDTG', 'TENC', 'TEXT', 'TFLT', 'TGID', \
                                 'TIME', 'TIT1', 'TIT2', 'TIT3', 'TKEY', \
                                 'TLAN', 'TMED', 'TMOO', 'TOAL', 'TOFN', \
                                 'TOLY', 'TOPE', 'TOWN', 'TPE1', 'TPE2', \
                                 'TPE3', 'TPE4', 'TPRO', 'TPUB', 'TRSN', \
                                 'TRSO', 'TSO2', 'TSOA', 'TSOC', 'TSOP', \
                                 'TSOT', 'TSRC', 'TSSE', 'TSST', \
                                 'TPOS', 'TRCK', 'MVIN', \
                                 'TBPM', 'TLEN', 'TORY', 'TSIZ', 'TYER', \
                                 'TIPL', 'TMCL', 'IPLS']
PF = {\
    'MCDI':'audio.add(MCDI(bytes(param[0])))',\
    'SEEK':'audio.add(SEEK(param[0]))',\
    'SIGN':'audio.add(SIGN(param[0], bytes(param[1])))',\
    'ASPI':'audio.add(ASPI(param[0], param[1], param[2], param[3], ' + \
                           'param[4]))',\
    'PRIV':'audio.add(ASPI(param[0], bytes(param[1])))',\
    'COMR':'audio.add(COMR(param[0], param[1], param[2], param[3], ' + \
                           'bytes(param[4]), param[5], param[6], ' + \
                            'param[7], param[8]))',\
    'OWNE':'audio.add(OWNE(param[0], param[1], param[2], param[3]))',\
    'USER':'audio.add(USER(param[0], param[1], param[2]))',\
    'UFID':'audio.add(UFID(param[0], bytes(param[1])))',\
    'POSS':'audio.add(POSS(param[0], param[1]))',\
    'LINK':'audio.add(LINK(param[0], param[1], bytes(param[2])))',\
    'AENC':'audio.add(AENC(param[0], param[1], param[2], bytes(param[3])))',\
    'RBUF':'audio.add(RBUF(param[0], param[1], param[2]))',\
    'GEOB':'audio.add(GEOB(param[0], param[1], param[2], param[3], ' + \
                           'bytes(param[4])))',\
    'POPM':'audio.add(POPM(param[0], param[1])) #, param[2]))',\
    'PCST':'audio.add(PCST(param[0]))',\
    'PCNT':'audio.add(PCNT(param[0]))',\
    'RVRB':'audio.add(RVRB(param[0], param[1], param[2], param[3], ' + \
                           'param[4], param[5], param[6], param[7], ' + \
                                 'param[8], param[9]))',\
    'RVAD':'audio.add(RVAD(param[0]))',\
    'EQU2':'audio.add(EQU2(param[0], param[1], param[2]))',\
    'COMM':"audio.add(COMM(3, 'XXX', '', atag)) " + \
                     "if self.mode.get() == 0 else audio.add(" + \
                     "COMM(param[0], param[1], param[2], param[3]))",\
    'SYLT':'audio.add(SYLT(param[0], param[1], param[2], param[3], ' + \
                           'param[4], bytes(param[5])))',\
    'USLT':'audio.add(USLT(param[0], param[1], param[2], param[3]))',\
    'SYTC':'audio.add(SYTC(param[0], bytes(param[1])))',\
    'MLLT':'audio.add(MLLT(param[0], param[1], param[2], param[3], ' + \
                           'param[4], bytes(param[5])))',\
    'ETCO':'audio.add(ETCO(param[0], bytes(param[1])))',\
    'WXXX':'audio.add(WXXX(param[0], param[1], param[2]))',\
    'TXXX':'audio.add(TXXX(param[0], param[1], param[2]))',\
    'ENCR':'if param[0] in list_owners:\n' +\
                '\tmessagebox.showwarning(k, LOCALIZED_TEXT[lang][' +\
            '"Only the first frame with this owner will be written to {}"].' +\
                                        'format(self.files[child][0]))\n' +\
           'else:\n' +\
               '\tlist_owners.extend([param[0]])\n' +\
               '\taudio.add(ENCR(param[0], param[1], bytes(param[2])))', \
    'GRID':'if param[0] in list_owners:\n' +\
               '\tmessagebox.showwarning(k, LOCALIZED_TEXT[lang][' +\
        '"Only the first frame with this owner will be written to {}"].' +\
                        'format(self.files[child][0]))\n' +\
           'else:\n' +\
               '\tlist_owners.extend([param[0]])\n' +\
               '\taudio.add(GRID(param[0], param[1], bytes(param[2])))', \
    }


def _aenc(atag, advanced):
    return [v if not isinstance(v, bytes) else list(v) \
            for v in \
            [atag.owner, atag.preview_start, atag.preview_length, atag.data]]
    
def _aspi(atag, advanced):
    return [v if not isinstance(v, bytes) else list(v) \
            for v in [atag.S, atag.L, atag.N, atag.b, atag.Fi]]
    
def _comm(atag, advanced):
    return [int(atag.encoding), atag.lang, atag.desc, atag.text] \
                                                if advanced else atag.text[0]
def _comr(atag, advanced):
    return [v if not isinstance(v, bytes) else list(v) \
            for v in [int(atag.encoding), atag.price, atag.valid_until, \
                      atag.contact, atag.format, atag.seller, atag.desc, \
                      atag.mime, atag.logo]]
    
def _encr(atag, advanced):
    return [v if not isinstance(v, bytes) else list(v) \
            for v in [atag.owner, atag.method, atag.data]]
    
def _equ2(atag, advanced):
    return [atag.method, atag.desc, atag.adjustments]

def _etco(atag, advanced):
    return [v if not isinstance(v, bytes) else list(v) \
            for v in [bytes(atag.format), bytes(atag.events)]]
    
def _geob(atag, _):
    return [v if not isinstance(v, bytes) else list(v) \
            for v in [int(atag.encoding), atag.mime, atag.filename, \
                      atag.desc, atag.data]]
    
def _grid(atag, advanced):
    return [v if not isinstance(v, bytes) else list(v) \
            for v in [atag.owner, atag.group, atag.data]]
def _ipls(atag, advanced):
    return [int(atag.encoding), atag.people]

def _link(atag, advanced):
    return [v if not isinstance(v, bytes) else list(v) \
            for v in [atag.frameid, atag.url, atag.data]]
    
def _mcdi(atag, advanced):
    return [v if not isinstance(v, bytes) else list(v) for v in [atag.data]]
def _mllt(atag, advanced):
    return [v if not isinstance(v, bytes) else list(v) \
            for v in [int(atag.frames), int(atag.bytes), \
                      int(atag.milliseconds), bytes(atag.bits_for_bytes), \
                      bytes(atag.bits_for_milliseconds), bytes(atag.data)]]
    
def _mvin(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _mvnm(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _owne(atag, advanced):
    return [int(atag.encoding), atag.price, atag.date, atag.seller]

def _pcnt(atag, advanced):
    return [atag.count]

def _pcst(atag, advanced):
    return [atag.value,]

def _popm(atag, advanced):
    return [atag.email, atag.rating]

def _poss(atag, advanced):
    return [atag.format, atag.position]

def _priv(atag, advanced):
    return [v if not isinstance(v, bytes) else list(v) \
            for v in [atag.owner, atag.data]]
    
def _rbuf(atag, advanced):
    return [v if not isinstance(v, bytes) else list(v) \
            for v in [atag.size, atag.info, atag.offset]]
    
def _rva2(atag, advanced):
    return [atag.desc, atag.channel, atag.gain, atag.peak]

def _rvad(atag, advanced):
    return [atag.adjustments]

def _rvrb(atag, advanced):
    return [atag.left, atag.right, atag.bounce_left, atag.bounce_right, \
            atag.feedback_ltl, atag.feedback_ltr, atag.feedback_rtr, \
            atag.feedback_rtl, atag.premix_ltr, atag.premix_rtl]
    
def _seek(atag, advanced):
    return [atag.offset]

def _sign(atag, advanced):
    return [v if not isinstance(v, bytes) else list(v) \
            for v in [atag.group, atag.sig]]
    
def _sylt(atag, advanced):
    return [v if not isinstance(v, bytes) else list(v) \
            for v in [int(atag.encoding), atag.lang, atag.format, \
                      atag.type, atag.desc, atag.text]]
    
def _sytc(atag, advanced):
    return [atag.format, atag.data]

def _talb(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tbpm(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tcat(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tcmp(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tcom(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tcon(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tcop(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tdat(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tden(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tdes(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tdly(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tdor(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tdrc(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tdrl(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tdtg(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tenc(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _text(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tflt(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tgid(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _time(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tipl(atag, advanced):
    return [int(atag.encoding), atag.people]

def _tit1(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tit2(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tit3(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tkey(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tkwd(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tlan(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tlen(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tmcl(atag, advanced):
    return [int(atag.encoding), atag.people]

def _tmed(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tmoo(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _toal(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tofn(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _toly(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tope(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tory(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _town(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tpe1(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tpe2(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tpe3(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tpe4(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tpos(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tpro(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tpub(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _trck(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _trsn(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _trso(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tsiz(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tso2(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tsoa(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tsoc(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tsop(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tsot(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tsrc(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tsse(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _tsst(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _txxx(atag, advanced):
    return [int(atag.encoding), atag.desc, atag.text] \
                                            if advanced else atag.text[0]
def _tyer(atag, advanced):
    return [int(atag.encoding), atag.text] if advanced else atag.text[0]

def _ufid(atag, advanced):
    return [v if not isinstance(v, bytes) else list(v) \
            for v in [atag.owner, atag.data]]
    
def _user(atag, advanced):
    return [int(atag.encoding), atag.lang, atag.text]

def _uslt(atag, advanced):
    return [int(atag.encoding), atag.lang, atag.desc, atag.text]

def _wcom(atag, advanced):
    return [atag.url] if advanced else atag.url

def _wcop(atag, advanced):
    return [atag.url] if advanced else atag.url

def _woaf(atag, advanced):
    return [atag.url] if advanced else atag.url

def _woar(atag, advanced):
    return [atag.url] if advanced else atag.url

def _woas(atag, advanced):
    return [atag.url] if advanced else atag.url

def _wors(atag, advanced):
    return [atag.url] if advanced else atag.url

def _wpay(atag, advanced):
    return [atag.url] if advanced else atag.url

def _wpub(atag, advanced):
    return [atag.url] if advanced else atag.url

def _wxxx(atag, advanced):
    return [int(atag.encoding), atag.desc, atag.url]

THE_P = {\
    'AENC':_aenc,\
    'ASPI':_aspi,\
    'COMM':_comm,\
    'COMR':_comr,\
    'ENCR':_encr,\
    'EQU2':_equ2,\
    'ETCO':_etco,\
    'GEOB':_geob,\
    'GRID':_grid,\
    'IPLS':_ipls,\
    'LINK':_link,\
    'MCDI':_mcdi,\
    'MLLT':_mllt,\
    'MVIN':_mvin,\
    'MVNM':_mvnm,\
    'OWNE':_owne,\
    'PCNT':_pcnt,\
    'PCST':_pcst,\
    'POPM':_popm,\
    'POSS':_poss,\
    'PRIV':_priv,\
    'RBUF':_rbuf,\
    'RVA2':_rva2,\
    'RVAD':_rvad,\
    'RVRB':_rvrb,\
    'SEEK':_seek,\
    'SIGN':_sign,\
    'SYLT':_sylt,\
    'SYTC':_sytc,\
    'TALB':_talb,\
    'TBPM':_tbpm,\
    'TCAT':_tcat,\
    'TCMP':_tcmp,\
    'TCOM':_tcom,\
    'TCON':_tcon,\
    'TCOP':_tcop,\
    'TDAT':_tdat,\
    'TDEN':_tden,\
    'TDES':_tdes,\
    'TDLY':_tdly,\
    'TDOR':_tdor,\
    'TDRC':_tdrc,\
    'TDRL':_tdrl,\
    'TDTG':_tdtg,\
    'TENC':_tenc,\
    'TEXT':_text,\
    'TFLT':_tflt,\
    'TGID':_tgid,\
    'TIME':_time,\
    'TIPL':_tipl,\
    'TIT1':_tit1,\
    'TIT2':_tit2,\
    'TIT3':_tit3,\
    'TKEY':_tkey,\
    'TKWD':_tkwd,\
    'TLAN':_tlan,\
    'TLEN':_tlen,\
    'TMCL':_tmcl,\
    'TMED':_tmed,\
    'TMOO':_tmoo,\
    'TOAL':_toal,\
    'TOFN':_tofn,\
    'TOLY':_toly,\
    'TOPE':_tope,\
    'TORY':_tory,\
    'TOWN':_town,\
    'TPE1':_tpe1,\
    'TPE2':_tpe2,\
    'TPE3':_tpe3,\
    'TPE4':_tpe4,\
    'TPOS':_tpos,\
    'TPRO':_tpro,\
    'TPUB':_tpub,\
    'TRCK':_trck,\
    'TRSN':_trsn,\
    'TRSO':_trso,\
    'TSIZ':_tsiz,\
    'TSO2':_tso2,\
    'TSOA':_tsoa,\
    'TSOC':_tsoc,\
    'TSOP':_tsop,\
    'TSOT':_tsot,\
    'TSRC':_tsrc,\
    'TSSE':_tsse,\
    'TSST':_tsst,\
    'TXXX':_txxx,\
    'TYER':_tyer,\
    'UFID':_ufid,\
    'USER':_user,\
    'USLT':_uslt,\
    'WCOM':_wcom,\
    'WCOP':_wcop,\
    'WOAF':_woaf,\
    'WOAR':_woar,\
    'WOAS':_woas,\
    'WORS':_wors,\
    'WPAY':_wpay,\
    'WPUB':_wpub,\
    'WXXX':_wxxx,\
       }

THE_IDIOT_P = {\
                'MVNM': '',\
                'TALB': '',\
                'TCOM': '',\
                'TCON': '',\
                'TCOP': '',\
                'TCMP': '',\
                'TDAT': '',\
                'TDEN': '',\
                'TDES': '',\
                'TKWD': '',\
                'TCAT': '',\
                'TDLY': '',\
                'TDOR': '',\
                'TDRC': '',\
                'TDRL': '',\
                'TDTG': '',\
                'TENC': '',\
                'TEXT': '',\
                'TFLT': '',\
                'TGID': '',\
                'TIME': '',\
                'TIT1': '',\
                'TIT2': '',\
                'TIT3': '',\
                'TKEY': '',\
                'TLAN': '',\
                'TMED': '',\
                'TMOO': '',\
                'TOAL': '',\
                'TOFN': '',\
                'TOLY': '',\
                'TOPE': '',\
                'TOWN': '',\
                'TPE1': '',\
                'TPE2': '',\
                'TPE3': '',\
                'TPE4': '',\
                'TPRO': '',\
                'TPUB': '',\
                'TRSN': '',\
                'TRSO': '',\
                'TSO2': '',\
                'TSOA': '',\
                'TSOC': '',\
                'TSOP': '',\
                'TSOT': '',\
                'TSRC': '',\
                'TSSE': '',\
                'TSST': '',\
                'TORY': '',\
                'TVIM': '',\
                'WCOM': '',\
                'WCOP': '',\
                'WOAF': '',\
                'WOAR': '',\
                'WOAS': '',\
                'WORS': '',\
                'WPAY': '',\
                'WPUB': '',\
                'TPOS': '',\
                'TRCK': '',\
                'MVIN': '',\
                'TBPM': '',\
                'TLEN': '',\
                'TSIZ': '',\
                'TYER': '',\
                'COMM': '',\
                }

THIS_VERSION = '1.0.0'



RECOMMENDED_COLUMNS = ['Type', 'Name', 'Location', 'TIT2', 'TALB', 'TPE1', \
                      'TPE2', 'TCOP', 'APIC', 'TDRC', 'TRCK', 'TPOS', 'COMM', \
                      'TCON', 'TCOM', 'adummy']
 