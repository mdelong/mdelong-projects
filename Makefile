CHARMC=/opt/sharcnet/charm++/6.2.1/bin/charmc $(OPTS)
CHARMHOME=/opt/sharcnet/charm++/6.2.1/
INCLUDES = -I$(CHARMHOME)/include
LIBS = -L$(CHARMHOME)/lib
OBJS = main.o

default: all
all: wp

wp: $(OBJS)
	$(CHARMC) -language charm++ -o wp $(OBJS)

main.o: main.C main.h wp.decl.h wp.def.h
	$(CHARMC) -o main.o main.C

wp.decl.h wp.h: main.ci
	$(CHARMC) main.ci

clean:
	rm -f *.decl.h *.def.h conv-host *.o wp charmrun charmrun.exe wp.exe wp.pdb wp.ilk

