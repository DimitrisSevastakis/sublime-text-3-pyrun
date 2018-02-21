# sublime-text-3-pyrun
Plugin for sublime text 3 which give the ability to send selected text to a terminal (similar to Spider, RStudio etc.) 

It ONLY works for Linux. Unfortunatelly it does require to start sublime as root in order for it to be able to write directly to a terminal.

First open a terminal and open python. The plugin will detect all python instances running on open terminals and give you a dropdown selection.

Select part of the code you want to execute, and hit the (Default) ctrl+enter, and watch the code being executed.

To change target terminal you can do so using the menu. Hit ctrl+shift+p type pyrun and you will see the two options
1) Run (same as ctrl+enter)
2) Select Terminal (selection from dropdown menu)
