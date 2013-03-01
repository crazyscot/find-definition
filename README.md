find-definition
===============

This is a script I lashed together to open up a new editor directly
at the definition of a type, structure, function or anything else that
ctags reports.

I use it with vim.  With other editors you either need to have ctags
support (contributions welcome! see the ctags man page for some pointers)
or be prepared to use vi or gvim or one of its derivatives as an external
source browser.


Usage
-----

In my shell I can type:

`$ find_definition.py fooBar`

... and vim opens up in read-only mode, right at the definition of fooBar.
(I keep a symlink to the script on my PATH.)
If the definition isn't found in the tags file, the script apologises.

With a suitable bash\_completion rune (see `bash-completion.sample`)
you can even tab-complete definitions in your tags file.

But, of course, this only works because I already have a tags file in
place. Read on...


Limitations
-----------

In the words of A.A. Milne, this script is a bear of little brain.
It takes you only to the first match it finds for the given tag.
(This is not necessarily the first match in the file, as it uses a
binary search for speed. If this bugs you, you can always edit the
TagsSearcherFactory to return the linear searcher.)

In other words, if there are multiple matches in the tags file, you need
to know how to drive your source browser to walk them.

In vim:

1. Put the cursor on the keyword
2. Ctrl-] to do a tags search
3. Use command :tn for next, :tp for previous.

Users of other editors are welcome to contribute instructions!
Don't despair, the ctags man page has some pointers.

My tags file at work is 78M but the searching is blink-of-an-eye fast.
Even the lsearch powering tab-completion is very fast.


Setting up
----------

Install the exuberant-ctags package, if you don't already have it.

`$ sudo apt-get install exuberant-ctags`

You need to run ctags regularly to keep the tags file up to date.

I have set up a personal cron job on my workstation to do this, here's the crontab line:

    0 6 * * * /home/younger/bin/update-ctags

My `update-ctags` script looks like this (redacted; edit to suit):

    #!/bin/sh
	
    cd /home/younger/Work/Mainline
    ctags -R --c++-kinds=+p --fields=+iaS --extra=+q SourceDir* AutoGenDir

Put find\_definition.py, or a symlink to it, on your PATH.
Set up an alias if you like (I alias it to `fd`).
If you want to tab-complete, read the instructions at the top of
`bash-completion.sample`.


Configuration
-------------

By default, the script reads `~/Work/Mainline/tags` and uses my `ViewInvocation` class (which opens vim in read-only mode).

You can change this behaviour by creating a config file `~/.find_definition`:

    [DEFAULT]
    tagsfile=/some/where/tags
    invocation=MyClass

`invocation` is the name of a class.
If it's not within the main script then the script will attempt to import
the named class (so you might want to set your `PYTHONPATH` suitably)
and then construct it with no parameters.


Invocation Classes
------------------

`ViewInvocation` is the default. It opens up the source in `view` (which is a read-only vim), in the current shell.

`GViewInvocation` opens up the source in `gview` which spawns a new graphical vim, read-only mode.

Contributions welcome!


Writing your own Invocation class
---------------------------------

It's probably easiest to crib from one of the existing invocation classes.
You are given the filename and the ex-command (vim-style regex search)
that will take you to the tag.

If your editor can't cope with regexp-style ex-commands, you might care to look
into driving ctags with `--excmd=number` to have it use line numbers
instead; see the ctags man page for a discussion of the advantages and
disadvantages.

