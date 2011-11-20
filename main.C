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
	ntemplates = getFilenames(tdir, tempext, templates);
	nimages    = getFilenames(idir, imageext, images);

	printf("%d templates, %d images\n", ntemplates, nimages);
	
	CProxy_FileReader freaders = CProxy_FileReader::ckNew();

	int fcount = 0;
	while (fcount < nimages)
	{
		for (int i = 0; i < CkNumPes(); i++)
		{
			string fname = images[fcount++];
			FNameMsg *f = new (fname.length()+1) FNameMsg;
			memcpy(f->fname, fname.c_str(), sizeof(char)*fname.length());
			f->fname[fname.length()] = '\0';
			freaders[i].GetFilename(f);

			if (fcount == nimages)
				break;
		}
	}

	//mainProxy.done();	
}

void Main::done(void)
{
	CkPrintf("All done\n");
	CkPrintf("Program took %lf seconds to run\n", CkWallTimer()); 
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
				string fname = dirname + "/" + string(dir_entry->d_name);
				fnames.push_back(fname);
				fcount++;
            }
        }
        
        closedir(directory);
    }
    
    return fcount;
}

void Main::RecvFile(FDataMsg *fd)
{
	CkPrintf("Main Received file %s, %dx%d\n", fd->fname, fd->height, fd->width);
	delete fd;
	nfinished++;
	if (nfinished == nimages)
		mainProxy.done();
}

void FileReader::GetFilename(FNameMsg *msg)
{
	CkPrintf("Chare %d received filename %s\n", CkMyPe(), msg->fname);
	FILE *fp = fopen(msg->fname, "rb");
		
	if (fp != NULL)
	{
		int w = 0, h = 0;
		fscanf(fp, "%d %d", &h, &w);
		char *buf = new char[h*w];
		int count = 0, c = 0;
		
		do {
			c = fgetc(fp);

			if (c == '0' || c == '1')
			{
				buf[count++] = (char)c;
			}

		} while (c != EOF);

		CkPrintf("Chare %d read file %s, %dx%d\n", CkMyPe(), msg->fname, h, w);			
		fclose(fp);

		char *p = strrchr(msg->fname, '/');
		if (p)
		{
			p++;
		}
		else
			p = msg->fname;

		FDataMsg *fdata = new (strlen(p)+1, w*h) FDataMsg(h, w);
		memcpy(fdata->fname, p, sizeof(char)*strlen(p)+1);
		memcpy(fdata->fdata, buf, sizeof(char)*w*h);
		mainProxy.RecvFile(fdata);
		delete [] buf;
	}
	delete msg;
}

#include "wp.def.h"

