HOSTNAME ?= $(shell hostname)

update:
	git fetch --all
	git merge origin/master

%.zip %.tar.gz %.tar.xz: dest ?= ../$@
%.zip %.tar.gz %.tar.xz:
	git archive -o $(dest) HEAD:$(basename $(basename $@))/
	[ -s $(dest) ]
