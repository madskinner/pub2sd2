# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 11:54:48 2019

@author: marks
"""
import codecs

STARTHEADER = [codecs.BOM_UTF8.decode(),'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">',\
               "<html>\n  <head>"]
# title will be supplied via .format()
MAINTITLE = '    <meta http-equiv="content-type" content="text/html; charset=utf-8"><title>{}</title>' 
MYCSSAJAMI = ['    <--', \
              '    <link rel="stylesheet" href="./css/ajami.css">', \
              '    -->']
MYCSSLATIN = ['    <--', \
              '    <link rel="stylesheet" href="./css/latin.css">', \
              '    -->']
SUMMARYCSSAJAMI = ['	<--', \
                   '    <link rel="stylesheet" href="css/index.css">', \
                   '	-->']
SUMMARYCSSLATIN = ['	<--', \
                   '    <link rel="stylesheet" href="css/index.css">', \
                   '	-->']
CLOSEHEADER = ['  </head>', '  <body dir="ltr" lang="en-US">', ]
OPENNAVBAR = ['  <nav id="navbar">',\
              '    <img src="./images/SIL-SN-LOGO.png" alt="SIL Senegal logo" title="" align="bottom" width="270">',]
CLOSENAVBAR = ['    <header>Cheatsheet</header>',\
               '    <ul>']
SUMMARYNAVBAR = ['  <nav id="navbar">',\
                 '    <img src="./images/SIL-SN-LOGO.png" alt="SIL Senegal logo" title="" align="bottom" width="270">',\
                 '    <div class="container col">',\
                 '       <div class="container col">',\
                 '          <header align="left">Touch (Android, iOS)</header>',\
                 '          <a class="nav-link" href="./{}{}.html" rel="internal" align="center"><li>qwerty</li></a>',\
                 '          <a class="nav-link" href="./{}{}.html" rel="internal" align="center"><li>azerty</li></a>',\
                 '       </div>',\
                 '       <div class="container col">',\
                 '          <header align="left">Web, Mac, Linux</header>',\
                 '             <a class="nav-link" href="./{}{}.html" rel="internal" align="center"><li>qwerty</li></a>',\
                 '             <a class="nav-link" href="./{}{}.html" rel="internal" align="center"<li>>azerty</li></a>',\
                 '       </div>',\
                 '       <div class="container col">',\
                 '          <header align="left">Windows</header>',\
                 ]
ANAVLINK = '      <a class="nav-link" href="../{}" rel="internal"><li>{}</li></a>'

JSFUNCTIONS = [\
               'function set_fr(kv) {',\
               '     document.getElementById(kv[0]).innerHTML = strs[kv1].fr;',\
               '}',\
               'function set_en() {',\
               '     document.getElementById(kv[0]).innerHTML = strs[kv1].en;',\
               '}',\
               'function set_pt() {',\
               '     document.getElementById(kv[0]).innerHTML = strs[kv1].pt;',\
               '}',\
               ]
STRINGS = ['var strs = {',\
"	p001:{en:'A non-breaking space is indicated by «&#x2248;».',",\
"         fr:'Un espace incassable est indiqué par «&#x2248;».',",\
"         pt:'Um espaço sem quebra é indicado por «&#x25CA;».'",\
"        },",\
'	p002:{en:"vowels",',\
'         fr:"les voyelles",',\
'         pt:"vogais"',\
'        },',\
'	p003:{en:"Vowels",',\
'          fr:"Les Voyelles",',\
'          pt:"Vogais",',\
'        },',\
'	p004:{en:"consonants",',\
'          fr:"les consonnes",',\
'          pt:"consoantes",',\
'        },',\
'	p005:{en:"Consonants",',\
'          fr:"Les Consonnes",',\
'          pt:"Consoantes",',\
'        },',\
'	p006:{en:"When a deadkey is followed by a space the deadkey''s base character will be produced.",',\
'          fr:"Lorsqu''une clé morte est suivie d''un espace, le caractère de base de la clé morte sera produit.",',\
'          pt:"Quando uma tecla morta é seguida por um espaço, o caractere base da tecla morta será produzido.",',\
'        },',\
'	p007:{en:"When you double tap the following deadkeys a combining diacritic will be produced.",',\
'          fr:"Lorsque vous double-cliquez sur les touches mortes suivantes, un diacritique de combinaison s''affiche.",',\
'          pt:"Quando você toca duas vezes nas seguintes teclas, um diacrítico combinando será produzido."',\
'        },',\
'	p008:{en:"others",',\
'          fr:"d''autres",',\
'          pt:"outros"',\
'        },',\
"	p009:{en:'The keys surrounded by () are deadkeys. A non-breaking space is indicated by «&#x2248;».',",\
"          fr:'Les touches entouré par () sont les touches mortes. Un espace incassable est indiqué par «&#x2248;».',",\
"          pt:'As teclas rodeado por () são teclas mortas. Um espaço sem quebra é indicado por «&#x2248;».'",\
"        },",\
"}",\
]
strs = {\
        "p001":{"en":'A non-breaking space is indicated by «&#x2248;».',\
                "fr":'Un espace incassable est indiqué par «&#x2248;».',\
                "pt":'Um espaço sem quebra é indicado por «&#x2248;».',\
                },\
        'p002':{'en':"vowels",\
                'fr':"les voyelles",\
                'pt':"vogais",\
                },\
        'p003':{'en':"Vowels",\
                'fr':"Les Voyelles",\
                'pt':"Vogais",\
                },\
        'p004':{'en':"consonants",\
                'fr':"les consonnes",\
                'pt':"consoantes",\
                },\
        'p005':{'en':"Consonants",\
                'fr':"Les Consonnes",\
                'pt':"Consoantes",\
                },\
        'p006':{'en':"When a deadkey is followed by a space the deadkey's base character will be produced.",\
                'fr':"Lorsqu'une clé morte est suivie d'un espace, le caractère de base de la clé morte sera produit.",\
                'pt':"Quando uma tecla morta é seguida por um espaço, o caractere base da tecla morta será produzido.",\
                },\
        'p007':{'en':"When you double tap the following deadkeys a combining diacritic will be produced.",\
                'fr':"Lorsque vous double-cliquez sur les touches mortes suivantes, un diacritique de combinaison s'affiche.",\
                'pt':"Quando você toca duas vezes nas seguintes teclas, um diacrítico combinando será produzido."\
                },
        'p008':{'en':"others",\
                'fr':"d'autres",\
                'pt':"outros",\
                },\
        "p009":{'en':'The keys surrounded by () are deadkeys. A non-breaking space is indicated by «&#x2248;».',\
                "fr":'Les touches entouré par () sont les touches mortes. Un espace incassable est indiqué par «&#x2248;».',\
                "pt":'As teclas rodeado por () são teclas mortas. Um espaço sem quebra é indicado por «&#x2248;».',\
                },\
    }

FILECSSLATIN = [\
                "@import 'http://fonts.googleapis.com/css?family=""Andika Afr"":400,400italic&subset=latin,latin-ext';", \
"", \
"html,body{", \
"  min-width:290px;", \
"  color: black;", \
"  background-color: #ffffff;", \
"  font-family: ""Andika Afr"", Andika, Arial, Helvetica, sans-serif;", \
"  line-height: 1.5;", \
"}", \
"", \
"p { font-family : ""Andika Afr"", andika, geneva, arial, helvetica, sans-serif; font-size : 13pt; font-style : normal; color: #000000; margin-top: 0.07in; margin-bottom: 0.07in }", \
"h1 { font-family : ""Andika Afr"", andika, geneva, arial, helvetica, sans-serif; font-size : 20pt; font-style : normal; color: #000000; margin-top: 0.07in; margin-bottom: 0.07in  }", \
"h2 { font-family : ""Andika Afr"", andika, geneva, arial, helvetica, sans-serif; font-size : 16pt; font-style : normal; color: #000000; margin-top: 0.07in; margin-bottom: 0.07in  }", \
"a:link { font-family : ""Andika Afr"", andika, geneva, arial, helvetica, sans-serif; color: #0000ff }", \
"a:visited { font-family : ""Andika Afr"", andika, geneva, arial, helvetica, sans-serif; color: #800080 }", \
"#navbar{", \
"  position:fixed;", \
"  min-width:290px;", \
"  top:0px;", \
"  left:0px;", \
"  width:300px;", \
"  height:100%;", \
"  border-right:solid;", \
"  border-color:rgba(0,22,22,0.4)", \
"}", \
"header{", \
"  color:black;", \
"  font-size: 30px;", \
"  margin:10px;", \
"  text-align:center;", \
"  font-size:1.8em;", \
"  font-weight:thin;", \
"}", \
"#main-doc header{", \
"  text-align:left;", \
"  margin:0px;", \
"}", \
"#navbar ul{", \
"  height:70%;", \
"  /*border:1px solid;*/", \
"  overflow-y:auto;", \
"  overflow-x:hidden;", \
"}", \
"#navbar li{", \
"  color: #4d4e53;", \
"  border:1px solid;", \
"  border-bottom-width:1px;", \
"  border-top-width:1px;", \
"  padding:8px;", \
"  padding-left:45px;", \
"  list-style: none;", \
"  position:relative;", \
"/*  left:-50px;*/", \
"  width:100%; ", \
"}", \
"#navbar li:first-child{", \
"  border-top: 1px solid;", \
"}", \
"#navbar a{", \
"  color: #4d4e53;", \
"  text-decoration:none;", \
"  cursor:pointer;", \
"} ", \
".container {", \
"  display: flex;", \
"  flex-direction: row;", \
"}", \
".row {flex-direction: row;}", \
".col {flex-direction: column;}", \
"", \
".block {", \
"  display: block;", \
"}", \
".empty-box {", \
"  background-color: #FFF;", \
"  width: 20px;", \
"  height: 2px;", \
"}", \
"", \
"@media only screen and (max-width: 815px) {", \
"  /* For mobile phones: */", \
"  #navbar ul{", \
"    border:1px solid;", \
"    height:207px;", \
"  }", \
"  #navbar{", \
"    background-color:white;", \
"    position:absolute;", \
"    top:0;", \
"    padding:0;", \
"    margin: 0;", \
"    width:100%;", \
"    max-height:275px;", \
"    border:none;", \
"    z-index:1;", \
"    border-bottom:2px solid;", \
"  }", \
"  #main-doc{", \
"    position: relative;", \
"    margin-left:0px;", \
"    margin-top:270px;", \
"  }", \
"  #main-doc section {", \
"    /*padding-top: 240px; */", \
"  }", \
"}", \
"@media only screen and (max-width: 400px) {", \
"  #main-doc{", \
"    margin-left:-10px;", \
"  }", \
"  code{", \
"    margin-left:-20px;", \
"    width:100%;", \
"    padding:15px;", \
"    padding-left:10px;", \
"    padding-right:45px;", \
"    min-width:233px;", \
"  }", \
"}", \
""]