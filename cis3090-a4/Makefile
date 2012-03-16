CHARMC=/opt/sharcnet/charm++/6.2.1/bin/charmc $(OPTS)
CHARMHOME=/opt/sharcnet/charm++/6.2.1/
INCLUDES = -I$(CHARMHOME)/include
LIBS = -L$(CHARMHOME)/lib
OBJS = main.o wp_utils.o
CFLAGS = -O2

default: all
all: wp

wp: $(OBJS)
	$(CHARMC) -language charm++ -o wp $(OBJS) $(CFLAGS)

main.o: main.C main.h main.decl.h main.def.h wp_utils.o wp_utils.h
	$(CHARMC) -o main.o main.C $(CFLAGS)

wp_utils.o: wp_utils.h wp_utils.C
	$(CHARMC) -o wp_utils.o wp_utils.C $(CFLAGS)

main.decl.h main.h: main.ci wp_utils.decl.h
	$(CHARMC) main.ci

wp_utils.decl.h wp_utils.h: wp_utils.ci
	$(CHARMC) wp_utils.ci

clean:
	rm -f *.decl.h *.def.h conv-host *.o wp charmrun charmrun.exe wp.exe wp.pdb wp.ilk

