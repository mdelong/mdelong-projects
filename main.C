#include <dirent.h>
#include <string>
#include <vector>
#include <stdio.h>
#include "wp.decl.h"
#include "main.h"

using namespace std;

CProxy_Main mainProxy;

FDataMsg *readFile(const char* filename)
{
	FILE *fp = fopen(filename, "rb");
		
	if (fp != NULL)
	{
		int w = 0, h = 0;
		fscanf(fp, "%d %d", &h, &w);
		char *buf = new char[(h*w)+1];
		int count = 0, c = 0;
		
		do {
			c = fgetc(fp);

			if (c == '0' || c == '1')
			{
				buf[count++] = (char)c;
			}

		} while (c != EOF);

		fclose(fp);
		buf[h*w] = '\0';

		const char *p = strrchr(filename, '/');
		if (p)
		{
			p++;
		}
		else
		{
			p = filename;
		}

		FDataMsg *fdata = new (strlen(p)+1, (w*h)+1) FDataMsg(h, w);
		memcpy(fdata->fname, p, sizeof(char)*strlen(p)+1);
		memcpy(fdata->fdata, buf, sizeof(char)*((w*h)+1));
		delete [] buf;
		return fdata;
	}
	else
	{
		return NULL;
	}
}

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
	
	freaders   = CProxy_FileReader::ckNew();
	fsearchers = CProxy_FileSearcher::ckNew();

	int w = 0, h = 0;
	for (int i = 0; i < ntemplates; i++)
	{
		FDataMsg *t = readFile(templates[i].c_str());
		fsearchers.GetTemplate(t);
	}

	int fcount = 0;
	while (fcount < nimages)
	{
		for (int i = 0; i < CkNumPes(); i++)
		{
			string fname = images[fcount++];
			FNameMsg *f = new (fname.length()+1) FNameMsg;
			memcpy(f->fname, fname.c_str(), sizeof(char)*fname.length());
			f->fname[fname.length()] = '\0';
			freaders[i].ReadFile(f);

			if (fcount == nimages)
			{
				break;
			}
		}
	}
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

	nfinished++;
	if (nfinished == ntemplates)
		mainProxy.done();
	else if (nfinished == 1)
		fsearchers[0].GetTemplate(fd);
	else
		delete fd;
}

void FileReader::ReadFile(FNameMsg *msg)
{
	//CkPrintf("Chare %d received filename %s\n", CkMyPe(), msg->fname);
	FDataMsg *fdata = readFile(msg->fname);		
	if (fdata != NULL)
	{
		mainProxy.RecvFile(fdata);	
	}

	delete msg;
}

void FileSearcher::GetTemplate(FDataMsg *t)
{
	string temp = string(t->fdata);
	Paralleldo p;
	p.height   = t->height;
	p.width    = t->width;
	p.filename = string(t->fname);

	delete t;

	int len = temp.length();
	
	for (int i = 0; i < len; i+=p.width)
	{
		string str = temp.substr(i, p.width);
		p.rotation0.push_back(str);
	}

	CkPrintf("Chare %d created paralleldo %s of size %dx%d, %dx%d\n", CkMyPe(), p.filename.c_str(), p.height, p.width,
	p.rotation0.size(), p.rotation0[0].length());

	createRotations(&p);
	templates.push_back(p);
}

void FileSearcher::createRotations(Paralleldo *p)
{
	for (int i = (p->height-1); i >= 0; i--)
    {
        string str(p->rotation0[i].rbegin(), p->rotation0[i].rend());
        p->rotation2.push_back(str);
    }

    char* rot90 = new char[p->height+1];
    for (int i = 0; i < p->width; i++)
    {
        for (int j = (p->height-1); j >= 0; j--)
        {
            rot90[p->height-j-1] = p->rotation0[j][i];
        }
        rot90[p->height] = '\0';
        p->rotation1.push_back(string(rot90));
    }
    delete [] rot90;

    for (int i = (p->width-1); i >= 0; i--)
    {
        string str(p->rotation1[i].rbegin(), p->rotation1[i].rend());
        p->rotation3.push_back(str);
    }
}

#include "wp.def.h"

