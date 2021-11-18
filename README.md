# EAF Video Player
This repository provides the EAF Video Player application for the [Emacs Application Framework](https://github.com/emacs-eaf/emacs-application-framework).

### Load application
[Install EAF](https://github.com/emacs-eaf/emacs-application-framework#install) first, then add below code in your emacs config:

```Elisp
(add-to-list 'load-path "~/.emacs.d/site-lisp/emacs-application-framework/")
(require 'eaf)
(require 'eaf-video-player)
```

### The keybinding of EAF Video Player.

| Key   | Event   |
| :---- | :------ |
| `SPC` | toggle_play |
| `x` | close_buffer |
| `h` | play_backward |
| `l` | play_forward |
| `j` | decrease_volume |
| `k` | increase_volume |
| `f` | toggle_fullscreen |
| `r` | restart |

