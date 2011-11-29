/*
 * Michael Delong, University of Guelph, Student ID 0636022
 * Term Project for CIS*3090, Fall 2011
 * This program implements the "Where's Paralleldo" template matching
 * problem from assignments 2 and 3 using the Charm++ paradigm.
 *
 * main.C - entry point for the application 
 *
 * The application should run effectively in parallel on any shared memory 
 * or cluster-type system, thanks to the power of the Charm++ Runtime System.
 * A word of warning: since this initial version does not check for out-of-memory errors, 
 * it will likely crash if the size of the image data being read in is greater 
 * than the processor memory size. The program was developed for experimentation and
 * comparison purposes, and was not intended to be robust.
 *
 * This file contains all function definitions for the mainchare entry point.
 *
 * The program is run as follows: ./charmrun ./wp <template folder> <targets folder> +p(num proc)
 * If running on a SHARCNET cluster, please use sqsub -q mpi ......
 */

#include <dirent.h>
#include <string>
#include <vector>
#include <stdio.h>
#include "wp_utils.decl.h"
#include "main.decl.h"
#include "wp_utils.h"
#include "main.h"

using namespace std;

//reference to main should be globally accessible
CProxy_Main mainProxy;

/* Generic function for reading in a template or image file.
 * As per A2 and A3 specifications, it is assumed that the file begins with
 * its height and width on the first line, followed by the contents, which consist
 * of '0' and '1'.
 * Reads in the file and packs it into message format; this message is returned
 */
FDataMsg *readFile(const char* filename)
{
    FILE *fp = fopen(filename, "rb");
        
    if (fp != NULL)
    {
        //read height and width, allocate buffer
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

        /*we don't want the complete path to be stored with the file data,
        just the file name*/
        const char *p = strrchr(filename, '/');
        if (p)
        {
            p++;
        }
        else
        {
            p = filename;
        }

        //pack file data into message format
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

/*Constructor for Main chare, entry point of the application*/
Main::Main(CkArgMsg *m)
{
    startTime = CkWallTimer();

    string imageext = string(".img");
    string tempext  = string(".txt");

    vector<string> templates;
    vector<string> images;

    //todo - potential bug - what if arguments are not supplied?
    string tdir = string(m->argv[1]);
    string idir = string(m->argv[2]);
    delete m;

    CkPrintf("Running Where's Paralleldo on %d processors\n",CkNumPes());
    mainProxy = thisProxy;
    nfinished = 0;
    searchNo  = 0;

    //scan directories first for filenames
    ntemplates = getFilenames(tdir, tempext, templates);
    nimages    = getFilenames(idir, imageext, images);

    //todo - should print error message and exit if no files found in either folder

    printf("%d templates, %d images\n", ntemplates, nimages);
 
    //create chare groups (1 per processor) for readers and searchers
    freaders   = CProxy_FileReader::ckNew(nimages);
    fsearchers = CProxy_FileSearcher::ckNew();

    //read templates serially, broadcast each one to all search chares
    int w = 0, h = 0;
    for (int i = 0; i < ntemplates; i++)
    {
        FDataMsg *t = readFile(templates[i].c_str());
        fsearchers.GetTemplate(t);
    }

    //Main image file I/O loop - pass each file off to a reader chare
    for (int i = 0; i < nimages; i++)
    {
        string fname = images[i];
        FNameMsg *f = new (fname.length()+1) FNameMsg;
        memcpy(f->fname, fname.c_str(), sizeof(char)*fname.length());
        f->fname[fname.length()] = '\0';

        //we have limited file readers; assign work in a circular fashion
        int index = i;// % CkNumPes();
        freaders[index].ReadFile(f);
    }
}

/*Called to terminate the program*/
void Main::done(void)
{
    CkPrintf("All done\n");
    CkPrintf("Program took %lf seconds to run\n", (CkWallTimer()-startTime)); 
    CkExit();
}

/*Main::checkIn() - entry method, can be invoked by any chare object with access to main
 *Search chares call this to notify main that an image search is finished.
 *When all images have been searched, the program will exit*/
void Main::checkIn()
{
    nfinished++;

    if (nfinished == nimages)
    {
        done();
    }
};

/*Scan the input directory (dirname) for all files ending with the extension specified
 *by parameter fext. The list of names found is stored in vector fnames (parameter).
 *Method returns the number of files that were found*/
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

/* Main::RecvFile(FDataMsg) - entry method, reader chares return the contents
 * of their files to main after reading them in.
 * FDataMsg contains the filename, dimensions, and raw data of the image file.
 * Main chare dispatches this message off to search chare to be matched against
 * the templates.
 */
void Main::RecvFile(FDataMsg *fd)
{
//  CkPrintf("Main Received file %s, %dx%d\n", fd->fname, fd->height, fd->width);
    int index = (searchNo++) % CkNumPes();
    fsearchers[index].GetImageData(fd);
}

#include "main.def.h"


