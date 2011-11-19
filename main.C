#include <dirent.h>
#include <string>
#include <vector>
#include <stdio.h>
#include "wp.decl.h"

using namespace std;

CProxy_Main mainProxy;

class Main : public CBase_Main
{
	public:
		int nfinished;

	Main(CkArgMsg *m)
	{
		string imageext = string(".img");
		string tempext  = string(".txt");

		vector<string> templates;
		vector<string> images;

		string tdir = string(m->argv[1]);
		string idir = string(m->argv[2]);

		delete m;
    	CkPrintf("Running Hello on %d processors\n",
	     CkNumPes());
    	mainProxy = thisProxy;
		nfinished = 0;
		int ntmp = GetFilenames(tdir, tempext, templates);
		int nimg = GetFilenames(idir, imageext, images);

		printf("%d templates, %d images\n", ntmp, nimg);
		mainProxy.done();	
	};

	void done(void)
  	{
    	CkPrintf("All done\n");
   		CkExit();
  	};
	
	int GetFilenames(string &dirname, string &fext, vector<string> &fnames)
	{
    	DIR* directory;
    	struct dirent* dir_entry;
    	int fcount = 0;
    
    	if ((directory = opendir(dirname.c_str())) != NULL)
    	{
        	while ((dir_entry = readdir(directory)) != NULL)
        	{
            	if (strstr(dir_entry->d_name, fext.c_str()) != NULL)
            	{
					fnames.push_back(string(dir_entry->d_name));
					fcount++;
            	}
        	}
        
        	closedir(directory);
    	}
    
    	return fcount;
	};
};

#include "wp.def.h"

