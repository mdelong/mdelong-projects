#ifndef __MAIN_H__
#define __MAIN_H__

#include <string>
#include <vector>

using namespace std;

class FNameMsg : public CMessage_FNameMsg {
	public:
		char *fname;
		FNameMsg(){};
};

class FileReader : public CBase_FileReader {	

public:
	FileReader(){};

	void GetFilename(FNameMsg *msg)
	{
		CkPrintf("Chare %d received filename %s\n", CkMyPe(), msg->fname);
		delete msg;
	};
};

class Main : public CBase_Main
{
	private:
		CProxy_FileReader freaders;
		int nfinished;
		int getFilenames(string &dirname, string &fext, vector<string> &fnames);

	public:
		Main(CkArgMsg *m);
		Main(CkMigrateMessage *m);
		void done();
		void checkIn();
};

#endif
