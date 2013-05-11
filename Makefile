SUBDIRS = i18n
.PHONY: $(SUBDIRS)

ALL = $(addsuffix -all,$(SUBDIRS))
INSTALL = $(addsuffix -install,$(SUBDIRS))
CLEAN = $(addsuffix -clean,$(SUBDIRS))

all: $(ALL)
install: $(INSTALL)
clean: $(CLEAN)

$(ALL): 
	$(MAKE) -C $(@:-all=) all

$(INSTALL):
	$(MAKE) -C $(@:-install=) install
	mkdir -p $(DESTDIR)/net
	mkdir -p $(DESTDIR)/usr/bin
	mkdir -p $(DESTDIR)/etc/init
	mkdir -p $(DESTDIR)/etc/default
	mkdir -p $(DESTDIR)/etc/avahi/services
	mkdir -p $(DESTDIR)/etc/avahi-linker
	install -m 755 avahi-linker.py $(DESTDIR)/usr/bin/avahi-linker
	install avahi-linker.conf $(DESTDIR)/etc/init
	install auto.master $(DESTDIR)/etc
	#install -m 644 /etc/avahi/services/* $(DESTDIR)/etc/avahi/services
	install -m 500 config/default.cfg $(DESTDIR)/etc/avahi-linker

$(CLEAN):
	$(MAKE) -C $(@:-clean=) clean
