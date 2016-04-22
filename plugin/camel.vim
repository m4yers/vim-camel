if exists('g:camel_loaded')
    finish
endif

let g:camel_verbose = 1
let g:camel_loaded = 1

augroup camel_start
    autocmd!
    autocmd VimEnter * call camel#Enable()
augroup end
