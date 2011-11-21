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
	searchNo  = 0;
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

	if (nfinished == nimages)
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
//	CkPrintf("Main Received file %s, %dx%d\n", fd->fname, fd->height, fd->width);

	int index = searchNo % CkNumPes();
	fsearchers[index].GetImageData(fd);
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

	createRotations(&p);
	templates.push_back(p);
}

void FileSearcher::GetImageData(FDataMsg *img)
{
	FileData fd;

	fd.height   = img->height;
	fd.width    = img->width;
	fd.filename = string(img->fname);
	
	{
		string temp = img->fdata;
		int len = temp.length();
		delete img;

		for (int i = 0; i < len; i+= fd.width)
		{
			fd.data.push_back(temp.substr(i, fd.width));
		}
	}

	for (int i = 0; i < templates.size(); i++)
	{
		Paralleldo p = templates.at(i);
		if (findPattern(&fd, &p) == true)
		{
			break;
		}
	}
	
	mainProxy.checkIn();
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

bool FileSearcher::findPattern(FileData *file, Paralleldo *pattern)
{
    int x = 0, y = 0;
    
    if (match(file->data, pattern->rotation0, &x, &y, Rotation_0) == true)
    {
        CkPrintf("$%s %s (%d,%d,0)\n", pattern->filename.c_str(), file->filename.c_str(), y, x);
        return true;
    }
    else if (match(file->data, pattern->rotation1, &x, &y, Rotation_90) == true)
    {
        CkPrintf("$%s %s (%d,%d,90)\n", pattern->filename.c_str(), file->filename.c_str(), y, x);
        return true;
    }
    else if (match(file->data, pattern->rotation2, &x, &y, Rotation_180) == true)
    {
        CkPrintf("$%s %s (%d,%d,180)\n", pattern->filename.c_str(), file->filename.c_str(), y, x);
        return true;
    }
    else if (match(file->data, pattern->rotation3, &x, &y, Rotation_270) == true)
    {
        CkPrintf("$%s %s (%d,%d,270)\n", pattern->filename.c_str(), file->filename.c_str(), y, x);
        return true;
    }

    return false;
}

bool FileSearcher::match(vector<string> data, vector<string> pattern, 
               int *x, int *y, Rotation rot)
{
    int pheight = pattern.size();
    int dheight = data.size();
    int shift   = getShift(pattern[0]); 

    bool match = false, matchFound = false;
    size_t found;
    std::string line, line2;
    int matchCount = 0;

    for (int i = 0; i <= (dheight-pheight); i++, matchFound==false)
    {
        line = data[i];

        do {
            if (matchFound == true)
            {
                break;
            }

            found = line.find(pattern[0]);
            if (found != std::string::npos)
            {
                *x = found;
                *y = i;
                match = true;
                for (int j = 1; j < pheight; j++)
                {
                    if ((j+i > dheight))
                    {
                        match = false;
                        break;
                    }

                    line2 = data[j+i].substr(*x, pattern[j].length());
                    if (line2 != pattern[j])
                    {
                        match = false;
                        if (*x+shift >= line.length())
                        {
                            line = line.substr(*x+shift);
                        }
                        else
                        {
                            line = line.substr(line.length()-1);
                        }
                        break;
                    }
                }

                if (match == true)
                {
                    matchFound = true;
                    break;
                }
            }
        } while (found != std::string::npos);
    }

    switch(rot)
    {
    case Rotation_0:
    {
        *x += 1;
        *y += 1;
        break;
    }
    case Rotation_90:
    {
        *x += pattern[0].length();
        *y += 1;
        break;
    }
    case Rotation_180:
    {
        *x += pattern[0].length();
        *y += pheight;
        break;
    }
    case Rotation_270:
    {
        *x += 1;
        *y += pheight;
        break;
    }
    default:
        break;
    }

    return matchFound;
}

int FileSearcher::getShift(string str)
{
    int shift = str.length();
    std::string temp = str.substr(1);
    for (int i = str.length()-2; i >= 1; i++)
    {
        int p = temp.find_last_of(str.substr(0, i));
        if (p != std::string::npos)
        {
            shift = p;
            break;
        }
    }

    return shift;
}


#include "wp.def.h"

