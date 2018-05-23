# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 07:23:42 2017

@author: marks
"""
import ast
from tkinter import messagebox
from mutagen.id3 import TXXX, WXXX, ETCO, MLLT, SYTC, USLT, SYLT, COMM, \
                        RVA2, EQU2, RVAD, RVRB, PCNT, PCST, POPM, \
                        GEOB, RBUF, AENC, LINK, POSS, UFID, USER, OWNE, \
                        COMR, ENCR, GRID, PRIV, SIGN, SEEK, ASPI, TIPL, \
                        TMCL, IPLS, MCDI, TBPM, TLEN, TORY, TSIZ, TYER, \
                        TPOS, TRCK, MVIN, MVNM, TALB, TCOM, TCON, TCOP, \
                        TCMP, TDAT, TDEN, TDES, TKWD, TCAT, TDLY, TDOR, \
                        TDRC, TDRL, TDTG, TENC, TEXT, TFLT, TGID, TIME, \
                        TIT1, TIT2, TIT3, TKEY, TLAN, TMED, TMOO, TOAL, \
                        TOFN, TOLY, TOPE, TOWN, TPE1, TPE2, TPE3, TPE4, \
                        TPRO, TPUB, TRSN, TRSO, TSO2, TSOA, TSOC, TSOP, \
                        TSOT, TSRC, TSSE, TSST, WCOM, WCOP, WOAF, WOAR, \
                        WOAS, WORS, WPAY, WPUB

from .localizedText import LOCALIZED_TEXT
from .regexs import escape_tab_return_feed, unescape_tab_return_feed
#RVA2, PRIV not implemented?
def _audio_mvnm(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(MVNM(3, param[1]))
    else:
        audio.add(MVNM(3, atag))

def _audio_talb(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TALB(3, param[1]))
    else:
        audio.add(TALB(3, atag))

def _audio_tcom(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TCOM(3, param[1]))
    else:
        audio.add(TCOM(3, atag))

def _audio_tcon(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TCON(3, param[1]))
    else:
        audio.add(TCON(3, atag))

def _audio_tcop(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TCOP(3, param[1]))
    else:
        audio.add(TCOP(3, atag))

def _audio_tcmp(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TCMP(3, param[1]))
    else:
        audio.add(TCMP(3, atag))

def _audio_tdat(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TDAT(3, param[1]))
    else:
        audio.add(TDAT(3, atag))

def _audio_tden(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TDEN(3, param[1]))
    else:
        audio.add(TDEN(3, atag))

def _audio_tdes(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TDES(3, param[1]))
    else:
        audio.add(TDES(3, atag))

def _audio_tkwd(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TKWD(3, param[1]))
    else:
        audio.add(TKWD(3, atag))

def _audio_tcat(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TCAT(3, param[1]))
    else:
        audio.add(TCAT(3, atag))

def _audio_tdly(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TDLY(3, param[1]))
    else:
        audio.add(TDLY(3, atag))

def _audio_tdor(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TDOR(3, param[1]))
    else:
        audio.add(TDOR(3, atag))

def _audio_tdrc(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TDRC(3, param[1]))
    else:
        audio.add(TDRC(3, atag))

def _audio_tdrl(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TDRL(3, param[1]))
    else:
        audio.add(TDRL(3, atag))

def _audio_tdtg(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TDTG(3, param[1]))
    else:
        audio.add(TDTG(3, atag))

def _audio_tenc(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TENC(3, param[1]))
    else:
        audio.add(TENC(3, atag))

def _audio_text(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TEXT(3, param[1]))
    else:
        audio.add(TEXT(3, atag))

def _audio_tflt(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TFLT(3, param[1]))
    else:
        audio.add(TFLT(3, atag))

def _audio_tgid(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TGID(3, param[1]))
    else:
        audio.add(TGID(3, atag))

def _audio_time(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TIME(3, param[1]))
    else:
        audio.add(TIME(3, atag))

def _audio_tit1(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TIT1(3, param[1]))
    else:
        audio.add(TIT1(3, atag))

def _audio_tit2(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TIT2(3, param[1]))
    else:
        audio.add(TIT2(3, atag))

def _audio_tit3(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TIT3(3, param[1]))
    else:
        audio.add(TIT3(3, atag))

def _audio_tkey(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TKEY(3, param[1]))
    else:
        audio.add(TKEY(3, atag))

def _audio_tlan(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TLAN(3, param[1]))
    else:
        audio.add(TLAN(3, atag))

def _audio_tmed(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TMED(3, param[1]))
    else:
        audio.add(TMED(3, atag))

def _audio_tmoo(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TMOO(3, param[1]))
    else:
        audio.add(TMOO(3, atag))

def _audio_toal(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TOAL(3, param[1]))
    else:
        audio.add(TOAL(3, atag))

def _audio_tofn(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TOFN(3, param[1]))
    else:
        audio.add(TOFN(3, atag))

def _audio_toly(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TOLY(3, param[1]))
    else:
        audio.add(TOLY(3, atag))

def _audio_tope(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TOPE(3, param[1]))
    else:
        audio.add(TOPE(3, atag))

def _audio_town(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TOWN(3, param[1]))
    else:
        audio.add(TOWN(3, atag))

def _audio_tpe1(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TPE1(3, param[1]))
    else:
        audio.add(TPE1(3, atag))

def _audio_tpe2(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TPE2(3, param[1]))
    else:
        audio.add(TPE2(3, atag))

def _audio_tpe3(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TPE3(3, param[1]))
    else:
        audio.add(TPE3(3, atag))

def _audio_tpe4(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TPE4(3, param[1]))
    else:
        audio.add(TPE4(3, atag))

def _audio_tpro(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TPRO(3, param[1]))
    else:
        audio.add(TPRO(3, atag))

def _audio_tpub(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TPUB(3, param[1]))
    else:
        audio.add(TPUB(3, atag))

def _audio_trsn(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TRSN(3, param[1]))
    else:
        audio.add(TRSN(3, atag))

def _audio_trso(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TRSO(3, param[1]))
    else:
        audio.add(TRSO(3, atag))

def _audio_tso2(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TSO2(3, param[1]))
    else:
        audio.add(TSO2(3, atag))

def _audio_tsoa(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TSOA(3, param[1]))
    else:
        audio.add(TSOA(3, atag))

def _audio_tsoc(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TSOC(3, param[1]))
    else:
        audio.add(TSOC(3, atag))

def _audio_tsop(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TSOP(3, param[1]))
    else:
        audio.add(TSOP(3, atag))

def _audio_tsot(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TSOT(3, param[1]))
    else:
        audio.add(TSOT(3, atag))

def _audio_tsrc(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TSRC(3, param[1]))
    else:
        audio.add(TSRC(3, atag))

def _audio_tsse(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TSSE(3, param[1]))
    else:
        audio.add(TSSE(3, atag))

def _audio_tsst(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TSST(3, param[1]))
    else:
        audio.add(TSST(3, atag))

def _audio_tpos(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TPOS(3, param[1]))
    else:
        audio.add(TPOS(3, atag))

def _audio_trck(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TRCK(3, param[1]))
    else:
        audio.add(TRCK(3, atag))

def _audio_mvin(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(MVIN(3, param[1]))
    else:
        audio.add(MVIN(3, atag))

def _audio_tbpm(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TBPM(3, param[1]))
    else:
        audio.add(TBPM(3, atag))

def _audio_tlen(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TLEN(3, param[1]))
    else:
        audio.add(TLEN(3, atag))

def _audio_tory(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TORY(3, param[1]))
    else:
        audio.add(TORY(3, atag))

def _audio_tsiz(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TSIZ(3, param[1]))
    else:
        audio.add(TSIZ(3, atag))

def _audio_tyer(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TYER(3, param[1]))
    else:
        audio.add(TYER(3, atag))

def _audio_tipl(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TIPL(3, param[1]))
    else:
        audio.add(TIPL(3, atag))

def _audio_tmcl(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(TMCL(3, param[1]))
    else:
        audio.add(TMCL(3, atag))

def _audio_ipls(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        param = ast.literal_eval(atag)
        audio.add(IPLS(3, param[1]))
    else:
        audio.add(IPLS(3, atag))

def _audio_wcom(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(WCOM(3, param[1]))

def _audio_wcop(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(WCOP(3, param[1]))

def _audio_woaf(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(WOAF(3, param[1]))

def _audio_woar(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(WOAR(3, param[1]))

def _audio_woas(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(WOAS(3, param[1]))

def _audio_wors(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(WORS(3, param[1]))

def _audio_wpay(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(WPAY(3, param[1]))

def _audio_wpub(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(WPUB(3, param[1]))

def _audio_mcdi(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(MCDI(bytes(param[0])))

def _audio_seek(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(SEEK(param[0]))

def _audio_sign(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(SIGN(param[0], bytes(param[1])))

def _audio_aspi(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(ASPI(param[0], param[1], param[2], param[3], param[4]))

def _audio_priv(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(ASPI(param[0], bytes(param[1])))

def _audio_comr(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(COMR(param[0], param[1], param[2], param[3], bytes(param[4]), \
                   param[5], param[6], param[7], param[8]))

def _audio_owne(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(OWNE(param[0], param[1], param[2], param[3]))

def _audio_user(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(USER(param[0], param[1], param[2]))

def _audio_ufid(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(UFID(param[0], bytes(param[1])))

def _audio_poss(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(POSS(param[0], param[1]))

def _audio_link(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(LINK(param[0], param[1], bytes(param[2])))

def _audio_aenc(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(AENC(param[0], param[1], param[2], bytes(param[3])))

def _audio_rbuf(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(RBUF(param[0], param[1], param[2]))

def _audio_geob(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(GEOB(param[0], param[1], param[2], param[3], bytes(param[4])))

def _audio_popm(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(POPM(param[0], param[1])) #, param[2]))

def _audio_pcst(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(PCST(param[0]))

def _audio_pcnt(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(PCNT(param[0]))

def _audio_rvrb(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(RVRB(param[0], param[1], param[2], param[3], param[4], \
                   param[5], param[6], param[7], param[8], param[9]))

def _audio_rvad(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(RVAD(param[0]))

def _audio_equ2(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(EQU2(param[0], param[1], param[2]))

def _audio_comm(atuple):
    audio, atag, advanced, _, _ = atuple
    if advanced:
        print('in _audio_comm')
        print(atag)
        param = ast.literal_eval(escape_tab_return_feed(atag))
        print(param)
        print(">{}<".format(param[3]))
        param[3] = [unescape_tab_return_feed(p) for p in param[3]]
        audio.add(COMM(param[0], param[1], param[2], param[3]))
    else:
        audio.add(COMM(3, 'XXX', '', atag))

def _audio_sylt(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(SYLT(param[0], param[1], param[2], param[3], param[4], \
                                                             bytes(param[5])))

def _audio_uslt(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(USLT(param[0], param[1], param[2], param[3]))

def _audio_sytc(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(SYTC(param[0], bytes(param[1])))

def _audio_mllt(atuple):
    audio, atag, _, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(MLLT(param[0], param[1], param[2], param[3], param[4], \
                                                           bytes(param[5])))

def _audio_etco(atuple):
    audio, atag, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(ETCO(param[0], bytes(param[1])))

def _audio_wxxx(atuple):
    audio, atag, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(WXXX(param[0], param[1], param[2]))

def _audio_txxx(atuple):
    audio, atag, _, _ = atuple
    param = ast.literal_eval(atag)
    audio.add(TXXX(param[0], param[1], param[2]))

def _audio_encr(atuple):
    audio, atag, _, list_owners, filechild = atuple
    param = ast.literal_eval(atag)
    if param[0] in list_owners:
        pass
    else:
        list_owners.extend([param[0]])
        audio.add(ENCR(param[0], param[1], bytes(param[2])))

def _audio_grid(atuple):
    audio, atag, _, list_owners, filechild = atuple
    param = ast.literal_eval(atag)
    if param[0] in list_owners:
#        messagebox.showwarning('GRID', LOCALIZED_TEXT[lang][\
#                "Only the first frame with this owner will be written to {}"].\
#                format(filechild))
        pass
    else:
        list_owners.extend([param[0]])
        audio.add(GRID(param[0], param[1], bytes(param[2])))

AUDIO = {\
        'MVNM': _audio_mvnm,
        'TALB': _audio_talb,
        'TCOM': _audio_tcom,
        'TCON': _audio_tcon,
        'TCOP': _audio_tcop,
        'TCMP': _audio_tcmp,
        'TDAT': _audio_tdat,
        'TDEN': _audio_tden,
        'TDES': _audio_tdes,
        'TKWD': _audio_tkwd,
        'TCAT': _audio_tcat,
        'TDLY': _audio_tdly,
        'TDOR': _audio_tdor,
        'TDRC': _audio_tdrc,
        'TDRL': _audio_tdrl,
        'TDTG': _audio_tdtg,
        'TENC': _audio_tenc,
        'TEXT': _audio_text,
        'TFLT': _audio_tflt,
        'TGID': _audio_tgid,
        'TIME': _audio_time,
        'TIT1': _audio_tit1,
        'TIT2': _audio_tit2,
        'TIT3': _audio_tit3,
        'TKEY': _audio_tkey,
        'TLAN': _audio_tlan,
        'TMED': _audio_tmed,
        'TMOO': _audio_tmoo,
        'TOAL': _audio_toal,
        'TOFN': _audio_tofn,
        'TOLY': _audio_toly,
        'TOPE': _audio_tope,
        'TOWN': _audio_town,
        'TPE1': _audio_tpe1,
        'TPE2': _audio_tpe2,
        'TPE3': _audio_tpe3,
        'TPE4': _audio_tpe4,
        'TPRO': _audio_tpro,
        'TPUB': _audio_tpub,
        'TRSN': _audio_trsn,
        'TRSO': _audio_trso,
        'TSO2': _audio_tso2,
        'TSOA': _audio_tsoa,
        'TSOC': _audio_tsoc,
        'TSOP': _audio_tsop,
        'TSOT': _audio_tsot,
        'TSRC': _audio_tsrc,
        'TSSE': _audio_tsse,
        'TSST': _audio_tsst,
        'TPOS': _audio_tpos,
        'TRCK': _audio_trck,
        'MVIN': _audio_mvin,
        'TBPM': _audio_tbpm,
        'TLEN': _audio_tlen,
        'TORY': _audio_tory,
        'TSIZ': _audio_tsiz,
        'TYER': _audio_tyer,
        'TIPL': _audio_tipl,
        'TMCL': _audio_tmcl,
        'IPLS': _audio_ipls,
        'WCOM': _audio_wcom,
        'WCOP': _audio_wcop,
        'WOAF': _audio_woaf,
        'WOAR': _audio_woar,
        'WOAS': _audio_woas,
        'WORS': _audio_wors,
        'WPAY': _audio_wpay,
        'WPUB': _audio_wpub,
        'MCDI': _audio_mcdi,
        'SEEK': _audio_seek,
        'SIGN': _audio_sign,
        'ASPI': _audio_aspi,
        'PRIV': _audio_priv,
        'COMR': _audio_comr,
        'OWNE': _audio_owne,
        'USER': _audio_user,
        'UFID': _audio_ufid,
        'POSS': _audio_poss,
        'LINK': _audio_link,
        'AENC': _audio_aenc,
        'RBUF': _audio_rbuf,
        'GEOB': _audio_geob,
        'POPM': _audio_popm,
        'PCST': _audio_pcst,
        'PCNT': _audio_pcnt,
        'RVRB': _audio_rvrb,
        'RVAD': _audio_rvad,
        'EQU2': _audio_equ2,
        'COMM': _audio_comm,
        'SYLT': _audio_sylt,
        'USLT': _audio_uslt,
        'SYTC': _audio_sytc,
        'MLLT': _audio_mllt,
        'ETCO': _audio_etco,
        'WXXX': _audio_wxxx,
        'TXXX': _audio_txxx,
        'ENCR': _audio_encr,
        'GRID': _audio_grid,
        }
