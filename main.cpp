#include <dirent.h>
#include <string>
#include <vector>
#include <stdio.h>

using namespace std;

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
}

int main(int argc, char*argv[])
{
	string imageext = string(".img");
	string tempext  = string(".txt");

	vector<string> templates;
	vector<string> images;

	string tdir = string(argv[1]);
	string idir = string(argv[2]);

	int ntmp = GetFilenames(tdir, tempext, templates);
	int nimg = GetFilenames(idir, imageext, images);

	printf("%d templates, %d images\n", ntmp, nimg);

	for (int i = 0; i < templates.size(); i++)
	{
		printf("template: %s\n", templates[i].c_str());
	}

	for (int i = 0; i < images.size(); i++)
	{
		printf("images: %s\n", images[i].c_str());
	}
	
	return 0;
}

