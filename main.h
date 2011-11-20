#ifndef __MAIN_H__
#define __MAIN_H__

#include <string>
#include <vector>
#include <stdio.h>

using namespace std;

class FNameMsg : public CMessage_FNameMsg {
	public:
		char *fname;
		FNameMsg(){};
};

class FDataMsg : public CMessage_FDataMsg {
	public:
		char *fname;
		char *fdata;
		int height;
		int width;
		FDataMsg(int h, int w)
		{
			height = h;
			width  = w;
		};
};

class FileReader : public CBase_FileReader {	

public:
	FileReader(){};
	void ReadFile(FNameMsg *msg);
};

class FileSearcher : public CBase_FileSearcher {	

private:
	void searchFile();

public:
	FileSearcher(){};
	void GetFileData(FDataMsg *p){};
};

class Main : public CBase_Main
{
	private:
		CProxy_FileReader freaders;
		int nfinished;
		int nimages;
		int ntemplates;
		int getFilenames(string &dirname, string &fext, vector<string> &fnames);

	public:
		Main(CkArgMsg *m);
		Main(CkMigrateMessage *m);
		void done();
		void checkIn();
		void RecvFile(FDataMsg *fd);
};

#endif
