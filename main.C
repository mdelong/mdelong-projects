#include <dirent.h>
#include <string>
#include <vector>
#include <stdio.h>
#include "wp.decl.h"
#include "main.h"

using namespace std;

CProxy_Main mainProxy;

Main::Main(CkArgMsg *m)
{
	string imageext = string(".img");
	string tempext  = string(".txt");

	vector<string> templates;
	vector<string> images;

	string tdir = string(m->argv[1]);
	string idir = string(m->argv[2]);

	delete m;
    CkPrintf("Running Hello on %d processors\n",CkNumPes());
    mainProxy = thisProxy;
	nfinished = 0;
	int ntmp = getFilenames(tdir, tempext, templates);
	int nimg = getFilenames(idir, imageext, images);

	printf("%d templates, %d images\n", ntmp, nimg);
	
	CProxy_FileReader freaders = CProxy_FileReader::ckNew();

	int fcount = 0;
	while (fcount < nimg)
	{
		for (int i = 0; i < CkNumPes(); i++)
		{
			string fname = images[fcount++];
			FNameMsg *f = new (fname.length()+1) FNameMsg;
			memcpy(f->fname, fname.c_str(), sizeof(char)*fname.length());
			f->fname[fname.length()] = '\0';
			freaders[i].GetFilename(f);

			if (fcount == nimg)
				break;
		}
	}

	mainProxy.done();	
}

void Main::done(void)
{
	CkPrintf("All done\n");
   	CkExit();
}

void Main::checkIn()
{
	nfinished++;

	if (nfinished == CkNumPes())
	{
		mainProxy.done();
	}
};

int Main::getFilenames(string &dirname, string &fext, vector<string> &fnames)
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
}

#include "wp.def.h"

