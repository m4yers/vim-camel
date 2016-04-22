let s:plugin_root = escape( expand( '<sfile>:p:h:h' ), '\' )
let s:python_folder = s:plugin_root . '/python/'

function! camel#Enable()
    call s:Debug("enabled")
endfunction

function! s:Debug(message)
    echohl WarningMsg | echom "Camel: " . a:message | echohl None
endfunction
