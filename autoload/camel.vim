let s:plugin_root = escape( expand( '<sfile>:p:h:h' ), ' \' )
let s:python_folder = s:plugin_root . '/python/camel/'

function! camel#Enable()
    call s:Emp('Enable')
    execute "pyfile " . s:python_folder . 'setup.py'
    python SetupEnv(vim.eval("s:plugin_root"))
    execute "pyfile " . s:python_folder . 'camel.py'
    python _options = CamelOptions()
    python _options.SetAddress("localhost", 8080)
    python _options.SetRoot(vim.eval("s:plugin_root"))
    python _options.AddDicts(vim.eval("g:camel_additional_dicts"))
    python _camel = CamelClient(_options)
    python _camel.Enable()
endfunction

function! camel#Disable()
    call s:Emp('Disable')
    python _camel.Disable()
    python _camel = None
endfunction

function! camel#IsEnabled()
    return pyeval('_camel.IsEnabled()')
endfunction

function! camel#Ping()
    if !camel#IsEnabled()
        call s:Emp('Camel is not enabled')
        return
    endif

    call s:Ping('Disable')
    let result = pyeval('_camel.Ping()')
    echo string(result)
endfunction

function! camel#Status()
    if !camel#IsEnabled()
        call s:Emp('Camel is not enabled')
        return
    endif

    let result = pyeval('_camel.Status()')
    call s:Emp('Status')
    for key in sort(keys(result))
        echo printf('%-20s', key) . string(result[key])
    endfor
endfunction

function! camel#RestartService()
    if !camel#IsEnabled()
        call s:Emp('Camel is not enabled')
        return
    endif

    call s:Emp('RestartService')
    python _camel.RestartService()
endfunction

function! camel#HumpTop(type)
    if !camel#IsEnabled()
        call s:Emp('Camel is not enabled')
        return
    endif

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
    let @@ = result[0]
    execute 'normal! P'

    " callee restore
    let @@ = saved_reg
    let &clipboard = saved_clipboard
endfunction

function! camel#HumpAll(type)
    if !camel#IsEnabled()
        call s:Emp('Camel is not enabled')
        return
    endif

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
    call complete(s:complete_start, s:complete_result)
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
        echom 'Camel: ' . a:message
    endif
endfunction

function! s:Emp(message)
    echohl WarningMsg | echo 'Camel: ' . a:message | echohl None
endfunction

function! s:Error(message)
    echohl ErrorMsg | echom 'Camel: ' . a:message | echohl None
endfunction
