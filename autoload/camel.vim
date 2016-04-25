let s:plugin_root = escape( expand( '<sfile>:p:h:h' ), '\' )
let s:python_folder = s:plugin_root . '/python/camel/'

function! camel#Connect()
    call s:Debug('Connect')
    execute "pyfile " . s:python_folder . 'setup.py'
    python SetupEnv(vim.eval("s:plugin_root"))
    execute "pyfile " . s:python_folder . 'camel.py'
    python _options = CamelOptions()
    python _options.SetAddress("localhost", 8080)
    python _options.SetRoot(vim.eval("s:plugin_root"))
    python _options.AddDicts(vim.eval("g:camel_additional_dicts"))
    python _camel = CamelClient(_options)
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

    let result = pyeval('_camel.Hump("camelcase","' . @@ . '")')
    let @@ = result.json.data[0]
    execute 'normal! P'

    " callee restore
    let @@ = saved_reg
    let &clipboard = saved_clipboard
endfunction

function! camel#HumpAll(type)
    " callee save
    let saved_clipboard = &clipboard
    let saved_reg = @@

    " We want to user the real unnamed register
    let &clipboard=''

    if a:type ==# 'char'
        execute 'normal! `[v`]y`]'
    else
        return
    endif

    let s:complete_result = pyeval('_camel.Hump("camelcase","' . @@ . '")')
    let s:complete_start = col("'[")
    let s:complete_end = col("']")

    call feedkeys("a\<c-r>=camel#Complete()\<cr>", 't')

    " callee restore
    let @@ = saved_reg
    let &clipboard = saved_clipboard
endfunction

function! camel#Complete()
    call complete(s:complete_start, s:complete_result.json.data)
    return ''
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

function! s:Debug(message)
    if exists('g:camel_verbose')
        echohl WarningMsg | echom 'Camel: ' . a:message | echohl None
    endif
endfunction

function! s:Error(message)
    echohl ErrorMsg | echom 'Camel: ' . a:message | echohl None
endfunction
