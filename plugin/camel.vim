if exists('g:camel_loaded')
    finish
endif

nnoremap <leader>h :set operatorfunc=camel#HumpTop<cr>g@

let g:camel_port = 4321
let g:camel_verbose = 1
let g:camel_loaded = 1

augroup camel_lifecycle
    autocmd!
    autocmd VimEnter * call camel#Connect()
    autocmd VimLeave * call camel#Disconnect()
augroup end
