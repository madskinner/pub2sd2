"""
"""
READ_TAG = { \
            'TXXX':'[atag.encoding, atag.desc, atag.data]', \
            'WXXX':'[atag.encoding, atag.desc, atag.url]', \
            'ETCO':'[bytes(atag.format), bytes(atag.events)]', \
            'MLLT':'[int(atag.frames), int(atag.bytes), int(atag.milliseconds), bytes(atag.bits_for_bytes), bytes(atag.bits_for_milliseconds), bytes(atag.data)]', \
            'SYTC':'[atag.format, atag.data]', \
            'USLT':'[atag.encoding, atag.lang, atag.desc, atag.text]', \
            'SYLT':'[atag.encoding, atag.lang, atag.format, atag.type, atag.desc, atag.text]', \
            'COMM':'[atag.encoding, atag.lang, atag.desc, atag.text]', \
            'RVA2':'[atag.desc, atag.channel, atag.gain, atag.peak]', \
            'EQU2':'[atag.method, atag.desc, atag.adjustments]', \
            'RVAD':'[atag.adjustments]', \
            'RVRB':'[atag.left, atag.right, atag.bounce_left, atag.bounce_right, atag.feedback_ltl, atag.feedback_ltr, atag.feedback_rtr, atag.feedback_rtl, atag.premix_ltr, atag.premix_rtl]', \
            'APIC':'[atag.encoding, atag.mime, atag.type, atag.desc, atag.data]', \
            'PCNT':'[atag.count]', \
            'PCST':'[atag.value]', \
            'POPM':'[atag.email, atag.rating]', \
            'GEOB':'[atag.encoding, atag.mime, atag.filename, atag.desc, atag.data]', \
            'RBUF':'[atag.size, atag.info, atag.offset]', \
            'AENC':'[atag.owner, atag.preview_start, atag.preview_length, atag.data]', \
            'LINK':'[atag.frameid, atag.url, atag.data]', \
            'POSS':'[atag.format, atag.position]', \
            'UFID':'[atag.owner, atag.data]', \
            'USER':'[atag.encoding, atag.lang, atag.text]', \
            'OWNE':'[atag.encoding, atag.price, atag.date, atag.seller]',\
            'COMR':'[atag.encoding, atag.price, atag.valid_until, atag.contact, atag.format, atag.seller, atag.desc, atag.mime, atag.logo]', \
            'ENCR':'[atag.owner, atag.method, atag.data]', \
            'GRID':'[atag.owner, atag.group, atag.data]', \
            'PRIV':'[atag.owner, atag.data]', \
            'SIGN':'[atag.group, atag.sig]', \
            'SEEK':'[atag.offset]', \
            'ASPI':'[atag.S, atag.L, atag.N, atag.b, atag.Fi]', \
            'TIPL':'[atag.encoding, atag.people]', \
            'TMCL':'[atag.encoding, atag.people]', \
            'IPLS':'[atag.encoding, atag.people]', \
            'MCDI':'[atag.data]', \
            'TBPM':'[atag.encoding, atag.text]', \
            'TLEN':'[atag.encoding, atag.text]', \
            'TORY':'[atag.encoding, atag.text]', \
            'TSIZ':'[atag.encoding, atag.text]', \
            'TYER':'[atag.encoding, atag.text]', \
#NumericPartTextFrame 'X/Y' x of y unary+ returns x
            'TPOS':'[atag.encoding, atag.text]', \
            'TRCK':'[atag.encoding, atag.text]', \
            'MVIN':'[atag.encoding, atag.text]', \
#TimestampTextFrame
#TextFrame
            'MVNM':'[atag.encoding, atag.text]', \
            'TALB':'[atag.encoding, atag.text]', \
            'TCOM':'[atag.encoding, atag.text]', \
            'TCON':'[atag.encoding, atag.text]', \
            'TCOP':'[atag.encoding, atag.text]', \
            'TCMP':'[atag.encoding, atag.text]', \
            'TDAT':'[atag.encoding, atag.text]', \
            'TDEN':'[atag.encoding, atag.text]', \
            'TDES':'[atag.encoding, atag.text]', \
            'TKWD':'[atag.encoding, atag.text]', \
            'TCAT':'[atag.encoding, atag.text]', \
            'TDLY':'[atag.encoding, atag.text]', \
            'TDOR':'[atag.encoding, atag.text]', \
            'TDRC':'[atag.encoding, atag.text]', \
            'TDRL':'[atag.encoding, atag.text]', \
            'TDTG':'[atag.encoding, atag.text]', \
            'TENC':'[atag.encoding, atag.text]', \
            'TEXT':'[atag.encoding, atag.text]', \
            'TFLT':'[atag.encoding, atag.text]', \
            'TGID':'[atag.encoding, atag.text]', \
            'TIME':'[atag.encoding, atag.text]', \
            'TIT1':'[atag.encoding, atag.text]', \
            'TIT2':'[atag.encoding, atag.text]', \
            'TIT3':'[atag.encoding, atag.text]', \
            'TKEY':'[atag.encoding, atag.text]', \
            'TLAN':'[atag.encoding, atag.text]', \
            'TMED':'[atag.encoding, atag.text]', \
            'TMOO':'[atag.encoding, atag.text]', \
            'TOAL':'[atag.encoding, atag.text]', \
            'TOFN':'[atag.encoding, atag.text]', \
            'TOLY':'[atag.encoding, atag.text]', \
            'TOPE':'[atag.encoding, atag.text]', \
            'TOWN':'[atag.encoding, atag.text]', \
            'TPE1':'[atag.encoding, atag.text]', \
            'TPE2':'[atag.encoding, atag.text]', \
            'TPE3':'[atag.encoding, atag.text]', \
            'TPE4':'[atag.encoding, atag.text]', \
            'TPRO':'[atag.encoding, atag.text]', \
            'TPUB':'[atag.encoding, atag.text]', \
            'TRSN':'[atag.encoding, atag.text]', \
            'TRSO':'[atag.encoding, atag.text]', \
            'TSO2':'[atag.encoding, atag.text]', \
            'TSOA':'[atag.encoding, atag.text]', \
            'TSOC':'[atag.encoding, atag.text]', \
            'TSOP':'[atag.encoding, atag.text]', \
            'TSOT':'[atag.encoding, atag.text]', \
            'TSRC':'[atag.encoding, atag.text]', \
            'TSSE':'[atag.encoding, atag.text]', \
            'TSST':'[atag.encoding, atag.text]', \
            'WCOM':'[atag.url]', \
            'WCOP':'[atag.url]', \
            'WOAF':'[atag.url]', \
            'WOAR':'[atag.url]', \
            'WOAS':'[atag.url]', \
            'WORS':'[atag.url]', \
            'WPAY':'[atag.url]', \
            'WPUB':'[atag.url]' \
            }

IDIOT_TAGS = { \
            'COMM':'[atag.encoding, atag.lang, atag.desc, atag.text]', \
            'APIC':'[atag.encoding, atag.mime, atag.type, atag.desc, atag.data]', \
            'TBPM':'[atag.encoding, atag.text]', \
            'TLEN':'[atag.encoding, atag.text]', \
            'TSIZ':'[atag.encoding, atag.text]', \
            'TPOS':'[atag.encoding, atag.text]', \
            'TRCK':'[atag.encoding, atag.text]', \
            'TALB':'[atag.encoding, atag.text]', \
            'TCOM':'[atag.encoding, atag.text]', \
            'TCON':'[atag.encoding, atag.text]', \
            'TCOP':'[atag.encoding, atag.text]', \
            'TCMP':'[atag.encoding, atag.text]', \
            'TDAT':'[atag.encoding, atag.text]', \
            'TDEN':'[atag.encoding, atag.text]', \
            'TDES':'[atag.encoding, atag.text]', \
            'TKWD':'[atag.encoding, atag.text]', \
            'TCAT':'[atag.encoding, atag.text]', \
            'TDLY':'[atag.encoding, atag.text]', \
            'TDOR':'[atag.encoding, atag.text]', \
            'TDRC':'[atag.encoding, atag.text]', \
            'TDRL':'[atag.encoding, atag.text]', \
            'TDTG':'[atag.encoding, atag.text]', \
            'TENC':'[atag.encoding, atag.text]', \
            'TEXT':'[atag.encoding, atag.text]', \
            'TFLT':'[atag.encoding, atag.text]', \
            'TGID':'[atag.encoding, atag.text]', \
            'TIME':'[atag.encoding, atag.text]', \
            'TIT1':'[atag.encoding, atag.text]', \
            'TIT2':'[atag.encoding, atag.text]', \
            'TIT3':'[atag.encoding, atag.text]', \
            'TKEY':'[atag.encoding, atag.text]', \
            'TLAN':'[atag.encoding, atag.text]', \
            'TMED':'[atag.encoding, atag.text]', \
            'TMOO':'[atag.encoding, atag.text]', \
            'TOAL':'[atag.encoding, atag.text]', \
            'TOFN':'[atag.encoding, atag.text]', \
            'TOLY':'[atag.encoding, atag.text]', \
            'TOPE':'[atag.encoding, atag.text]', \
            'TORY':'[atag.encoding, atag.text]', \
            'TOWN':'[atag.encoding, atag.text]', \
            'TPE1':'[atag.encoding, atag.text]', \
            'TPE2':'[atag.encoding, atag.text]', \
            'TPE3':'[atag.encoding, atag.text]', \
            'TPE4':'[atag.encoding, atag.text]', \
            'TPRO':'[atag.encoding, atag.text]', \
            'TPUB':'[atag.encoding, atag.text]', \
            'TRSN':'[atag.encoding, atag.text]', \
            'TRSO':'[atag.encoding, atag.text]', \
            'TSO2':'[atag.encoding, atag.text]', \
            'TSOA':'[atag.encoding, atag.text]', \
            'TSOC':'[atag.encoding, atag.text]', \
            'TSOP':'[atag.encoding, atag.text]', \
            'TSOT':'[atag.encoding, atag.text]', \
            'TSRC':'[atag.encoding, atag.text]', \
            'TSSE':'[atag.encoding, atag.text]', \
            'TSST':'[atag.encoding, atag.text]', \
            'WCOM':'[atag.url]', \
            'WCOP':'[atag.url]', \
            'WOAF':'[atag.url]', \
            'WOAR':'[atag.url]', \
            'WOAS':'[atag.url]', \
            'WORS':'[atag.url]', \
            'WPAY':'[atag.url]', \
            'WPUB':'[atag.url]' \
            }

READ_TAG_INFO = { \
            'TXXX':'[encoding, description, ["text"]] multiple frames possible each with unique description', \
            'WXXX':'[encoding, description, url] multiple frame possible each with unique description', \
            'ETCO':'[bytes(format), bytes(events)]', \
            'MLLT':'[int(frames), int(bytes), int(milliseconds), bytes(bits_for_bytes), bytes(bits_for_milliseconds), bytes(data)]', \
            'SYTC':'[format, data]', \
            'USLT':'[encoding, lang, description, text] multiple frames possible each with unique lang/description', \
            'SYLT':'[encoding, lang, format, type, desc, text]  multiple frames possible each with unique lang/description', \
            'COMM':'[encoding, lang, description, ["text"]] mutiple comments possible each with unique lang/description', \
            'RVA2':'[description, channel, gain, peak] multiple frames possible each with unique description', \
            'EQU2':'[method, description, adjustments] multiple frames possible each with unique lang/description', \
            'RVAD':'[adjustments]', \
            'RVRB':'[left, right, bounce_left, bounce_right, feedback_ltl, feedback_ltr, feedback_rtr, feedback_rtl, premix_ltr, premix_rtl]', \
            'APIC':'[encoding, mime, type, description, data] multiple frames possible each with unique description', \
            'PCNT':'[count]', \
            'PCST':'[value]', \
            'POPM':'[email, rating] multiple frames possible each with unique email address', \
            'GEOB':'[encoding, mime, filename, description, data] multiple frames possible each with unique desription', \
            'RBUF':'[size, info, offset]', \
            'AENC':'[owner, preview_start, preview_length, data] multiple frames possible each with unique owner identifier', \
            'LINK':'[frameid, url, data] multiple frames possible each with unique frameid/url/data ', \
            'POSS':'[format, position]', \
            'UFID':'[owner, data]', \
            'USER':'[encoding, language, text] multiple frames possible each with unique language', \
            'OWNE':'[encoding, price, date, seller]',\
            'COMR':'[encoding, price, valid_until, contact, format, seller, desc, mime, logo] multiple frames possible but each must be unique', \
            'ENCR':'[owner, method, data] multiple frames possible but only one with each owner and only one with each method', \
            'GRID':'[owner, group, data] multiple frames possible but only one with each owner identifier and only one with each group symbol', \
            'PRIV':'[owner, data] multiple frames possible each with unique owner/data', \
            'SIGN':'[group, sig] multiple frames possible each with unique group/sig', \
            'SEEK':'[offset]', \
            'ASPI':'[S, L, N, b, Fi]', \
            'TIPL':'[encoding, [["role1","person1"],["role2","person2"],]] a list of role:person pairs', \
            'TMCL':'[encoding, [["instrument","musician",]]] alist of insrument:musician pairs', \
            'IPLS':'[encoding, people]', \
            'MCDI':'[data]', \
            'TBPM':'[encoding, ["text"]]', \
            'TLEN':'[encoding, ["text"]]', \
            'TORY':'[encoding, ["text"]]', \
            'TSIZ':'[encoding, ["text"]]', \
            'TYER':'[encoding, ["text"]]', \
#NumericPartTextFrame 'X/Y' x of y unary+ returns x
            'TPOS':'[encoding, ["text"]]', \
            'TRCK':'[encoding, ["text"]]', \
            'MVIN':'[encoding, ["text"]]', \
#TimestampTextFrame
#TextFrame
            'MVNM':'[encoding, ["text"]]', \
            'TALB':'[encoding, ["text"]]', \
            'TCOM':'[encoding, ["text"]]', \
            'TCON':'[encoding, ["text"]]', \
            'TCOP':'[encoding, ["text"]]', \
            'TCMP':'[encoding, ["text"]]', \
            'TDAT':'[encoding, ["text"]]', \
            'TDEN':'[encoding, ["text"]]', \
            'TDES':'[encoding, ["text"]]', \
            'TKWD':'[encoding, ["text"]]', \
            'TCAT':'[encoding, ["text"]]', \
            'TDLY':'[encoding, ["text"]]', \
            'TDOR':'[encoding, ["text"]]', \
            'TDRC':'[encoding, ["text"]]', \
            'TDRL':'[encoding, ["text"]]', \
            'TDTG':'[encoding, ["text"]]', \
            'TENC':'[encoding, ["text"]]', \
            'TEXT':'[encoding, ["text"]]', \
            'TFLT':'[encoding, ["text"]]', \
            'TGID':'[encoding, ["text"]]', \
            'TIME':'[encoding, ["text"]]', \
            'TIT1':'[encoding, ["text"]]', \
            'TIT2':'[encoding, ["text"]]', \
            'TIT3':'[encoding, ["text"]]', \
            'TKEY':'[encoding, ["text"]]', \
            'TLAN':'[encoding, ["text"]]', \
            'TMED':'[encoding, ["text"]]', \
            'TMOO':'[encoding, ["text"]]', \
            'TOAL':'[encoding, ["text"]]', \
            'TOFN':'[encoding, ["text"]]', \
            'TOLY':'[encoding, ["text"]]', \
            'TOPE':'[encoding, ["text"]]', \
            'TOWN':'[encoding, ["text"]]', \
            'TPE1':'[encoding, ["text"]]', \
            'TPE2':'[encoding, ["text"]]', \
            'TPE3':'[encoding, ["text"]]', \
            'TPE4':'[encoding, ["text"]]', \
            'TPRO':'[encoding, ["text"]]', \
            'TPUB':'[encoding, ["text"]]', \
            'TRSN':'[encoding, ["text"]]', \
            'TRSO':'[encoding, ["text"]]', \
            'TSO2':'[encoding, ["text"]]', \
            'TSOA':'[encoding, ["text"]]', \
            'TSOC':'[encoding, ["text"]]', \
            'TSOP':'[encoding, ["text"]]', \
            'TSOT':'[encoding, ["text"]]', \
            'TSRC':'[encoding, ["text"]]', \
            'TSSE':'[encoding, ["text"]]', \
            'TSST':'[encoding, ["text"]]', \
            'WCOM':'["url"]', \
            'WCOP':'["url"]', \
            'WOAF':'["url"]', \
            'WOAR':'["url"]', \
            'WOAS':'["url"]', \
            'WORS':'["url"]', \
            'WPAY':'["url"]', \
            'WPUB':'["url"]' \
            }

HASH_TAG_ON = { \
            'TXXX':[False, True, False], \
            'WXXX':[False, True, False], \
            'ETCO':[False, False], \
            'MLLT':[False, False, False, False, False, False], \
            'SYTC':[False, False], \
            'USLT':[False, True, True, False], \
            'SYLT':[False, True, True, False], \
            'COMM':[False, True, True, False], \
            'RVA2':[True, False, False, False], \
            'EQU2':[False, True, False], \
            'RVAD':[False], \
            'RVRB':[False, False, False, False, False, False, False, False, False, False], \
            'APIC':[False, False, False, True, False], \
            'PCNT':[False], \
            'PCST':[False], \
            'POPM':[True, False], \
            'GEOB':[False, False, False, True, False], \
            'RBUF':[False, False], \
            'AENC':[True, False, False, False, False], \
            'LINK':[True, True, True], \
            'POSS':[False, False], \
            'UFID':[False, False], \
            'USER':[False, True, False], \
            'OWNE':[False, False, False, False],\
            'COMR':[True, True, True, True, True, True, True, True, True], \
            'ENCR':[False, True, False], \
            'GRID':[False, True, False], \
            'PRIV':[True, True], \
            'SIGN':[True, True], \
            'SEEK':[False], \
            'ASPI':[False, False, False, False, False], \
            'TIPL':[False, False], \
            'TMCL':[False, False], \
            'IPLS':[False, False], \
            'MCDI':[False], \
            'TBPM':[False, False], \
            'TLEN':[False, False], \
            'TORY':[False, False], \
            'TSIZ':[False, False], \
            'TYER':[False, False], \
            'TPOS':[False, False], \
            'TRCK':[False, False], \
            'MVIN':[False, False], \
            'MVNM':[False, False], \
            'TALB':[False, False], \
            'TCOM':[False, False], \
            'TCON':[False, False], \
            'TCOP':[False, False], \
            'TCMP':[False, False], \
            'TDAT':[False, False], \
            'TDEN':[False, False], \
            'TDES':[False, False], \
            'TKWD':[False, False], \
            'TCAT':[False, False], \
            'TDLY':[False, False], \
            'TDOR':[False, False], \
            'TDRC':[False, False], \
            'TDRL':[False, False], \
            'TDTG':[False, False], \
            'TENC':[False, False], \
            'TEXT':[False, False], \
            'TFLT':[False, False], \
            'TGID':[False, False], \
            'TIME':[False, False], \
            'TIT1':[False, False], \
            'TIT2':[False, False], \
            'TIT3':[False, False], \
            'TKEY':[False, False], \
            'TLAN':[False, False], \
            'TMED':[False, False], \
            'TMOO':[False, False], \
            'TOAL':[False, False], \
            'TOFN':[False, False], \
            'TOLY':[False, False], \
            'TOPE':[False, False], \
            'TOWN':[False, False], \
            'TPE1':[False, False], \
            'TPE2':[False, False], \
            'TPE3':[False, False], \
            'TPE4':[False, False], \
            'TPRO':[False, False], \
            'TPUB':[False, False], \
            'TRSN':[False, False], \
            'TRSO':[False, False], \
            'TSO2':[False, False], \
            'TSOA':[False, False], \
            'TSOC':[False, False], \
            'TSOP':[False, False], \
            'TSOT':[False, False], \
            'TSRC':[False, False], \
            'TSSE':[False, False], \
            'TSST':[False, False], \
            'WCOM':[True], \
            'WCOP':[False], \
            'WOAF':[False], \
            'WOAR':[True], \
            'WOAS':[False], \
            'WORS':[False], \
            'WPAY':[False], \
            'WPUB':[False] \
            }

READ_TAG_HIDE_ENCODING = { \
            'TXXX':'[atag.desc, atag.data]', \
            'WXXX':'[atag.desc, atag.url]', \
            'ETCO':'[bytes(atag.format), bytes(atag.events)]', \
            'MLLT':'[int(atag.frames), int(atag.bytes), int(atag.milliseconds), bytes(atag.bits_for_bytes), bytes(atag.bits_for_milliseconds), bytes(atag.data)]', \
            'SYTC':'[atag.format, atag.data]', \
            'USLT':'[atag.lang, atag.desc, atag.text]', \
            'SYLT':'[atag.lang, atag.format, atag.type, atag.desc, atag.text]', \
            'COMM':'[atag.lang, atag.desc, atag.text]', \
            'RVA2':'[atag.desc, atag.channel, atag.gain, atag.peak]', \
            'EQU2':'[atag.method, atag.desc, atag.adjustments]', \
            'RVAD':'[atag.adjustments]', \
            'RVRB':'[atag.left, atag.right, atag.bounce_left, atag.bounce_right, atag.feedback_ltl, atag.feedback_ltr, atag.feedback_rtr, atag.feedback_rtl, atag.premix_ltr, atag.premix_rtl]', \
            'APIC':'[atag.mime, atag.type, atag.desc, atag.data]', \
            'PCNT':'[atag.count]', \
            'PCST':'[atag.value]', \
            'POPM':'[atag.email, atag.rating]', \
            'GEOB':'[atag.mime, atag.filename, atag.desc, atag.data]', \
            'RBUF':'[atag.size, atag.info, atag.offset]', \
            'AENC':'[atag.owner, atag.preview_start, atag.preview_length, atag.data]', \
            'LINK':'[atag.frameid, atag.url, atag.data]', \
            'POSS':'[atag.format, atag.position]', \
            'UFID':'[atag.owner, atag.data]', \
            'USER':'[atag.lang, atag.text]', \
            'OWNE':'[atag.price, atag.date, atag.seller]',\
            'COMR':'[atag.price, atag.valid_until, atag.contact, atag.format, atag.seller, atag.desc, atag.mime, atag.logo]', \
            'ENCR':'[atag.owner, atag.method, atag.data]', \
            'GRID':'[atag.owner, atag.group, atag.data]', \
            'PRIV':'[atag.owner, atag.data]', \
            'SIGN':'[atag.group, atag.sig]', \
            'SEEK':'[atag.offset]', \
            'ASPI':'[atag.S, atag.L, atag.N, atag.b, atag.Fi]', \
            'TIPL':'atag.people', \
            'TMCL':'atag.people', \
            'IPLS':'atag.people', \
            'MCDI':'[bytes(atag.data]', \
            'TBPM':'atag.text', \
            'TLEN':'atag.text', \
            'TORY':'atag.text', \
            'TSIZ':'atag.text', \
            'TYER':'atag.text', \
#NumericPartTextFrame 'X/Y' x of y unary+ returns x
            'TPOS':'atag.text', \
            'TRCK':'atag.text', \
            'MVIN':'atag.text', \
#TimestampTextFrame
#TextFrame
            'MVNM':'atag.text', \
            'TALB':'atag.text', \
            'TCOM':'atag.text', \
            'TCON':'atag.text', \
            'TCOP':'atag.text', \
            'TCMP':'atag.text', \
            'TDAT':'atag.text', \
            'TDEN':'atag.text', \
            'TDES':'atag.text', \
            'TKWD':'atag.text', \
            'TCAT':'atag.text', \
            'TDLY':'atag.text', \
            'TDOR':'atag.text', \
            'TDRC':'atag.text', \
            'TDRL':'atag.text', \
            'TDTG':'atag.text', \
            'TENC':'atag.text', \
            'TEXT':'atag.text', \
            'TFLT':'atag.text', \
            'TGID':'atag.text', \
            'TIME':'atag.text', \
            'TIT1':'atag.text', \
            'TIT2':'atag.text', \
            'TIT3':'atag.text', \
            'TKEY':'atag.text', \
            'TLAN':'atag.text', \
            'TMED':'atag.text', \
            'TMOO':'atag.text', \
            'TOAL':'atag.text', \
            'TOFN':'atag.text', \
            'TOLY':'atag.text', \
            'TOPE':'atag.text', \
            'TOWN':'atag.text', \
            'TPE1':'atag.text', \
            'TPE2':'atag.text', \
            'TPE3':'atag.text', \
            'TPE4':'atag.text', \
            'TPRO':'atag.text', \
            'TPUB':'atag.text', \
            'TRSN':'atag.text', \
            'TRSO':'atag.text', \
            'TSO2':'atag.text', \
            'TSOA':'atag.text', \
            'TSOC':'atag.text', \
            'TSOP':'atag.text', \
            'TSOT':'atag.text', \
            'TSRC':'atag.text', \
            'TSSE':'atag.text', \
            'TSST':'atag.text', \
            'WCOM':'atag.url', \
            'WCOP':'atag.url', \
            'WOAF':'atag.url', \
            'WOAR':'atag.url', \
            'WOAS':'atag.url', \
            'WORS':'atag.url', \
            'WPAY':'atag.url', \
            'WPUB':'atag.url' \
            }
