if exists('g:camel_loaded')
    finish
endif

nnoremap <leader>hh :set operatorfunc=camel#HumpTop<cr>g@iw
nnoremap <leader>ha :set operatorfunc=camel#HumpAll<cr>g@iw

let g:camel_port = 4321
let g:camel_additional_dicts = ['/usr/share/dict/web2']
let g:camel_verbose = 1
let g:camel_loaded = 1

augroup camel_lifecycle
    autocmd!
    autocmd VimEnter * call camel#Connect()
    autocmd VimLeave * call camel#Disconnect()
augroup end
