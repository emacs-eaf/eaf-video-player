# EAF Video Player
This repository provides the EAF Video Player application for the [Emacs Application Framework](https://github.com/emacs-eaf/emacs-application-framework).

### Load application

```Elisp
(add-to-list 'load-path "~/.emacs.d/site-lisp/eaf-video-player/")
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

