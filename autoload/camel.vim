let s:plugin_root = escape( expand( '<sfile>:p:h:h' ), '\' )
let s:python_folder = s:plugin_root . '/python/camel/'

function! camel#Connect()
    call s:Debug('Connect')
    execute "pyfile " . s:python_folder . 'camel.py'
    python _camel = CamelClient("localhost", 8080)
    python _camel.Connect()
endfunction

function! camel#Disconnect()
    call s:Debug('Disconnect')
    python _camel.Disconnect()
    python _camel = None
endfunction

function! camel#Ping()
    call s:Debug('Ping')
    let result = pyeval('_camel.Ping()')
    echom result.json.data
endfunction

function! camel#HumpTop(type)
    " callee save
    let saved_clipboard = &clipboard
    let saved_reg = @@

    " We want to user the real unnamed register
    let &clipboard=''

    if a:type ==# 'v'
        execute 'normal! `<v`>d'
    elseif a:type ==# 'char'
        execute 'normal! `[v`]d'
    else
        return
    endif

    let result = pyeval('_camel.HumpTop("camelcase","' . @@ . '")')
    let @@ = result.json.data
    execute 'normal! P'

    " callee restore
    let @@ = saved_reg
    let &clipboard = saved_clipboard
endfunction

" Move the selected word to the top
" function! camel#HumpTopSave(style, raw, humped)
"     call s:Debug('HumpTopSave')
"     call s:Request('PATCH', '/humps/' . a:raw)
" endfunction
"
" function! camel#HumpAdd(style, humped)
"     call s:Debug('HumpAdd')
"     call s:Request('POST', '/humps')
" endfunction
"
" function! camel#HumpAll(style, raw)
"     call s:Debug('HumpAll')
"     call s:Request('GET', '/humps/' . a:raw . '?style=' . a:style . '&select=all')
" endfunction

function! s:Debug(message)
    if exists('g:camel_verbose')
        echohl WarningMsg | echom 'Camel: ' . a:message | echohl None
    endif
endfunction

function! s:Error(message)
    echohl ErrorMsg | echom 'Camel: ' . a:message | echohl None
endfunction
