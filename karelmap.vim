" Vim syntax file
" Language: Karel the Robot maps
" Maintainer: Ondřej Šebek
" Latest Revision: 1 February 2020

if exists("b:current_syntax")
  finish
endif

syn match karelSpace	"\v\."
syn match karelWall	    "\v#"
syn match karelBeeper	"\v\d"

syn match karelBot	"\v\>"
syn match karelBot	"\v\<"
syn match karelBot	"\v\^"
syn match karelBot	"\vv"


let b:current_syntax = "karelmap"

hi def link karelWall	Constant
hi def link karelSpace	Comment
hi def link karelBeeper	Label
hi def link karelBot	Todo
