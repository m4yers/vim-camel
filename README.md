Intro
=====
vim-camel adds auto-casing for keywords

Instalation
===========

Usage
=====

Dependencies
============
pip install futures

Todo
====
 - [ ] Add doc
 - [ ] Tests
 - [ ] optimize dict loading speed, pickle?
 - [ ] Add user dict options
 - [ ] Add service restart on plugin update
 - [ ] Add rules for word sufuxes lise 's', 'es' etc
 - [ ] Randomize port
 - [ ] Kill connected users after few hours of inactivity
 - [ ] Make bad(unmatched) words handling optional and dynamic(for cases where result list is < N)
 - [ ] Handle passed delimiters
 - [ ] Handle abbreviations e.g. DDR, IO etc must use same case for every character
 - [ ] Error handling
 - [ ] Add support for other styles(lo-camel-case, [lo/hi]-snake-case, kebab-case, lisp-case, train-case, title-case, all-caps-case, lower-case)
 - [ ] mutli word support
 - [ ] Variable name simplify, expand, generating, synonyms
 - [ ] Variable generation based on meta input?
 - [ ] Word search based on meta input?
 - [ ] Windows?

Bugs
====
 - [ ] cursor goes to the end of the word; it should stay on the same character
