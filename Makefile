CHARMC=/opt/sharcnet/charm++/6.2.1/bin/charmc $(OPTS)

CHARMHOME=/opt/sharcnet/charm++/6.2.1/
OBJS = main.o
INCLUDES = -I$(CHARMHOME)/include
LIBS = -L$(CHARMHOME)/lib

all: wp

wp: $(OBJS)
	$(CHARMC) -language charm++ -o wp $(OBJS)

wp.decl.h wp.def.h: main.ci
	$(CHARMC)  main.ci $(INCLUDES) $(LIBS)

clean:
	rm -f *.decl.h *.def.h conv-host *.o main charmrun charmrun.exe main.exe main.pdb main.ilk

main.o: main.C wp.decl.h
	$(CHARMC) -c main.C $(INCLUDES) $(LIBS)

test: all
	./charmrun ./wp +p4 10 $(TESTOPTS)

bgtest: all
	./charmrun ./wp +p4 10 +x2 +y2 +z2 $(TESTOPTS)

