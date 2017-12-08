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

THE_P = {\
        'MCDI':'[v if not isinstance(v, bytes) else list(v) ' + \
                 'for v in [atag.data]]',\
        'ASPI':'[v if not isinstance(v, bytes) else list(v) ' + \
                 'for v in [atag.S, atag.L, atag.N, atag.b, atag.Fi]]',\
        'SEEK':'[atag.offset]',\
        'SIGN':'[v if not isinstance(v, bytes) else list(v) ' + \
                 'for v in [atag.group, atag.sig]]',\
        'PRIV':'[v if not isinstance(v, bytes) else list(v) ' + \
                 'for v in [atag.owner, atag.data]]',\
        'GRID':'[v if not isinstance(v, bytes) else list(v) ' + \
                 'for v in [atag.owner, atag.group, atag.data]]',\
        'ENCR':'[v if not isinstance(v, bytes) else list(v) ' + \
                 'for v in [atag.owner, atag.method, atag.data]]',\
        'COMR':'[v if not isinstance(v, bytes) else list(v) ' + \
                 'for v in [int(atag.encoding), atag.price, ' + \
                 'atag.valid_until, atag.contact, atag.format, ' + \
                 'atag.seller, atag.desc, atag.mime, atag.logo]]',\
        'OWNE':'[int(atag.encoding), atag.price, atag.date, atag.seller]',\
        'USER':'[int(atag.encoding), atag.lang, atag.text]',\
        'UFID':'[v if not isinstance(v, bytes) else list(v) ' + \
                 'for v in [atag.owner, atag.data]]',\
        'POSS':'[atag.format, atag.position]',\
        'LINK':'[v if not isinstance(v, bytes) else list(v) ' + \
                 'for v in [atag.frameid, atag.url, atag.data]]',\
        'AENC':'[v if not isinstance(v, bytes) else list(v) ' + \
                 'for v in [atag.owner, atag.preview_start, ' + \
                 'atag.preview_length, atag.data]]',\
        'RBUF':'[v if not isinstance(v, bytes) else list(v) ' + \
                 'for v in [atag.size, atag.info, atag.offset]]',\
        'GEOB':'[v if not isinstance(v, bytes) else list(v) ' + \
                 'for v in [int(atag.encoding), atag.mime, atag.filename, ' + \
                 'atag.desc, atag.data]]',\
        'POPM':'[atag.email, atag.rating]',\
        'PCST':'[atag.value,]',\
        'PCNT':'[atag.count]',\
        'RVRB':'[atag.left, atag.right, atag.bounce_left, ' + \
                 'atag.bounce_right, atag.feedback_ltl, ' + \
                 'atag.feedback_ltr, atag.feedback_rtr, ' + \
                 'atag.feedback_rtl, atag.premix_ltr, atag.premix_rtl]',\
        'RVAD':'[atag.adjustments]',\
        'EQU2':'[atag.method, atag.desc, atag.adjustments]',\
        'RVA2':'[atag.desc, atag.channel, atag.gain, atag.peak]',\
        'COMM':'[int(atag.encoding), atag.lang, atag.desc, atag.text]',\
        'SYLT':'[v if not isinstance(v, bytes) else list(v) ' + \
                 'for v in [int(atag.encoding), atag.lang, atag.format, ' + \
                 'atag.type, atag.desc, atag.text]]',\
        'USLT':'[int(atag.encoding), atag.lang, atag.desc, atag.text]',\
        'SYTC':'[atag.format, atag.data]',\
        'MLLT':'[v if not isinstance(v, bytes) else list(v) ' + \
                 'for v in [int(atag.frames), int(atag.bytes), ' + \
                 'int(atag.milliseconds), bytes(atag.bits_for_bytes), ' + \
                 'bytes(atag.bits_for_milliseconds), bytes(atag.data)]]',\
        'ETCO':'[v if not isinstance(v, bytes) else list(v) ' + \
                 'for v in [bytes(atag.format), bytes(atag.events)]]',\
        'WXXX':'[int(atag.encoding), atag.desc, atag.url]',\
        'TXXX':'[int(atag.encoding), atag.desc, atag.text]',\
        'TIPL':'[int(atag.encoding), atag.people]', \
        'TMCL':'[int(atag.encoding), atag.people]', \
        'IPLS':'[int(atag.encoding), atag.people]', \
        'TBPM':'[int(atag.encoding), atag.text]', \
        'TLEN':'[int(atag.encoding), atag.text]', \
        'TORY':'[int(atag.encoding), atag.text]', \
        'TSIZ':'[int(atag.encoding), atag.text]', \
        'TYER':'[int(atag.encoding), atag.text]', \
        'TPOS':'[int(atag.encoding), atag.text]', \
        'TRCK':'[int(atag.encoding), atag.text]', \
        'MVIN':'[int(atag.encoding), atag.text]', \
        'WCOM':'[atag.url]', \
        'WCOP':'[atag.url]', \
        'WOAF':'[atag.url]', \
        'WOAR':'[atag.url]', \
        'WOAS':'[atag.url]', \
        'WORS':'[atag.url]', \
        'WPAY':'[atag.url]', \
        'WPUB':'[atag.url]', \
        'MVNM':'[int(atag.encoding), atag.text]', \
        'TALB':'[int(atag.encoding), atag.text]', \
        'TCOM':'[int(atag.encoding), atag.text]', \
        'TCON':'[int(atag.encoding), atag.text]', \
        'TCOP':'[int(atag.encoding), atag.text]', \
        'TCMP':'[int(atag.encoding), atag.text]', \
        'TDAT':'[int(atag.encoding), atag.text]', \
        'TDEN':'[int(atag.encoding), atag.text]', \
        'TDES':'[int(atag.encoding), atag.text]', \
        'TKWD':'[int(atag.encoding), atag.text]', \
        'TCAT':'[int(atag.encoding), atag.text]', \
        'TDLY':'[int(atag.encoding), atag.text]', \
        'TDOR':'[int(atag.encoding), atag.text]', \
        'TDRC':'[int(atag.encoding), atag.text]', \
        'TDRL':'[int(atag.encoding), atag.text]', \
        'TDTG':'[int(atag.encoding), atag.text]', \
        'TENC':'[int(atag.encoding), atag.text]', \
        'TEXT':'[int(atag.encoding), atag.text]', \
        'TFLT':'[int(atag.encoding), atag.text]', \
        'TGID':'[int(atag.encoding), atag.text]', \
        'TIME':'[int(atag.encoding), atag.text]', \
        'TIT1':'[int(atag.encoding), atag.text]', \
        'TIT2':'[int(atag.encoding), atag.text]', \
        'TIT3':'[int(atag.encoding), atag.text]', \
        'TKEY':'[int(atag.encoding), atag.text]', \
        'TLAN':'[int(atag.encoding), atag.text]', \
        'TMED':'[int(atag.encoding), atag.text]', \
        'TMOO':'[int(atag.encoding), atag.text]', \
        'TOAL':'[int(atag.encoding), atag.text]', \
        'TOFN':'[int(atag.encoding), atag.text]', \
        'TOLY':'[int(atag.encoding), atag.text]', \
        'TOPE':'[int(atag.encoding), atag.text]', \
        'TOWN':'[int(atag.encoding), atag.text]', \
        'TPE1':'[int(atag.encoding), atag.text]', \
        'TPE2':'[int(atag.encoding), atag.text]', \
        'TPE3':'[int(atag.encoding), atag.text]', \
        'TPE4':'[int(atag.encoding), atag.text]', \
        'TPRO':'[int(atag.encoding), atag.text]', \
        'TPUB':'[int(atag.encoding), atag.text]', \
        'TRSN':'[int(atag.encoding), atag.text]', \
        'TRSO':'[int(atag.encoding), atag.text]', \
        'TSO2':'[int(atag.encoding), atag.text]', \
        'TSOA':'[int(atag.encoding), atag.text]', \
        'TSOC':'[int(atag.encoding), atag.text]', \
        'TSOP':'[int(atag.encoding), atag.text]', \
        'TSOT':'[int(atag.encoding), atag.text]', \
        'TSRC':'[int(atag.encoding), atag.text]', \
        'TSSE':'[int(atag.encoding), atag.text]', \
        'TSST':'[int(atag.encoding), atag.text]', \
       }

THE_IDIOT_P = {\
                'MVNM':'atag.text[0]', \
                'TALB':'atag.text[0]', \
                'TCOM':'atag.text[0]', \
                'TCON':'atag.text[0]', \
                'TCOP':'atag.text[0]', \
                'TCMP':'atag.text[0]', \
                'TDAT':'atag.text[0]', \
                'TDEN':'atag.text[0]', \
                'TDES':'atag.text[0]', \
                'TKWD':'atag.text[0]', \
                'TCAT':'atag.text[0]', \
                'TDLY':'atag.text[0]', \
                'TDOR':'atag.text[0]', \
                'TDRC':'atag.text[0]', \
                'TDRL':'atag.text[0]', \
                'TDTG':'atag.text[0]', \
                'TENC':'atag.text[0]', \
                'TEXT':'atag.text[0]', \
                'TFLT':'atag.text[0]', \
                'TGID':'atag.text[0]', \
                'TIME':'atag.text[0]', \
                'TIT1':'atag.text[0]', \
                'TIT2':'atag.text[0]', \
                'TIT3':'atag.text[0]', \
                'TKEY':'atag.text[0]', \
                'TLAN':'atag.text[0]', \
                'TMED':'atag.text[0]', \
                'TMOO':'atag.text[0]', \
                'TOAL':'atag.text[0]', \
                'TOFN':'atag.text[0]', \
                'TOLY':'atag.text[0]', \
                'TOPE':'atag.text[0]', \
                'TOWN':'atag.text[0]', \
                'TPE1':'atag.text[0]', \
                'TPE2':'atag.text[0]', \
                'TPE3':'atag.text[0]', \
                'TPE4':'atag.text[0]', \
                'TPRO':'atag.text[0]', \
                'TPUB':'atag.text[0]', \
                'TRSN':'atag.text[0]', \
                'TRSO':'atag.text[0]', \
                'TSO2':'atag.text[0]', \
                'TSOA':'atag.text[0]', \
                'TSOC':'atag.text[0]', \
                'TSOP':'atag.text[0]', \
                'TSOT':'atag.text[0]', \
                'TSRC':'atag.text[0]', \
                'TSSE':'atag.text[0]', \
                'TSST':'atag.text[0]', \
                'TORY':'atag.text[0]', \
                'TVIM':'atag.text[0]', \
                'WCOM':'atag.url[0]', \
                'WCOP':'atag.url[0]', \
                'WOAF':'atag.url[0]', \
                'WOAR':'atag.url[0]', \
                'WOAS':'atag.url[0]', \
                'WORS':'atag.url[0]', \
                'WPAY':'atag.url[0]', \
                'WPUB':'atag.url[0]', \
                'TPOS':'atag.text[0]', \
                'TRCK':'atag.text[0]', \
                'MVIN':'atag.text[0]', \
                'TBPM':'atag.text[0]', \
                'TLEN':'atag.text[0]', \
                'TSIZ':'atag.text[0]', \
                'TYER':'atag.text[0]', \
                'COMM':'atag.text[0]', \
                }

THIS_VERSION = '0.9.9.18'



RECOMMENDED_COLUMNS = ['Type', 'Name', 'Location', 'TIT2', 'TALB', 'TPE1', \
                      'TPE2', 'TCOP', 'APIC', 'TDRC', 'TRCK', 'TPOS', 'COMM', \
                      'TCON', 'TCOM', 'adummy']
 