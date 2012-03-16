/*
 * Michael Delong, University of Guelph, Student ID 0636022
 * Term Project for CIS*3090, Fall 2011
 * This program implements the "Where's Paralleldo" template matching
 * problem from assignments 2 and 3 using the Charm++ paradigm.
 * 
 * wp_utils.C
 *
 * This file contains all function and class definitions for the program's 
 * "threaded" utility chares - the reader chares and search chare objects
 */

#include <string>
#include <vector>
#include "wp_utils.h"
#include "wp_utils.decl.h"

using namespace std;

extern CProxy_Main mainProxy;
extern FDataMsg *readFile(const char* filename);

/* FileReader::ReadFile(FNameMsg) - entry method for FileReader chares
 * Receives filename from mainchare (msg), reads in the file data, and
 * returns the data to the mainchare
 */
void FileReader::ReadFile(FNameMsg *msg)
{
    //CkPrintf("Chare %d received filename %s\n", CkMyPe(), msg->fname);
    FDataMsg *fdata = readFile(msg->fname);     
    
    //pass file contents back to main
    if (fdata != NULL)
    {
        mainProxy.RecvFile(fdata);  
    }

    delete msg;
}

/* FileSearcher::GetTemplate(FDataMsg) - entry method for FileSearcher chare
 * Receives a template from mainchare and stores it for future matching
 */
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

    //need to check for 90, 180, and 270 degree rotations as well
    createRotations(&p);
    templates.push_back(p);
}

/* FileSearcher::GetImageData(img) - entry method for FileSearcher chare
 * Receives image file contents and searches the file for any of the templates
 * this chare has stored. If a match is found, we return without checking the 
 * other templates, since the A2 and A3 specifications mandate that only one 
 * template match exists in a given file.
 */
void FileSearcher::GetImageData(FDataMsg *img)
{
    FileData fd;

    fd.height   = img->height;
    fd.width    = img->width;
    fd.filename = string(img->fname);
    
    //this section of code is performed in a block because files can be quite large.
    // Ensures that stack memory for string object "temp" is freed as soon as possible
    {
        string temp = string(img->fdata);
        int len = temp.length();
        delete img;

        for (int i = 0; i < len; i+= fd.width)
        {
            fd.data.push_back(temp.substr(i, fd.width));
        }
    }

    //search for templates in this image
    for (int i = 0; i < templates.size(); i++)
    {
        Paralleldo p = templates.at(i);
        if (findPattern(&fd, &p) == true)
        {
            break;
        }
    }
    
    //notify mainchare that search has finished
    mainProxy.checkIn();
}

/* Helper method for FileSearcher class
 * Creates and stores 90, 180, and 270 degree rotations of a template image
 */
void FileSearcher::createRotations(Paralleldo *p)
{
    //create 180 degree rotation
    for (int i = (p->height-1); i >= 0; i--)
    {
        string str(p->rotation0[i].rbegin(), p->rotation0[i].rend());
        p->rotation2.push_back(str);
    }

    //create 90 degree rotation
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

    //create 270 degree rotation
    for (int i = (p->width-1); i >= 0; i--)
    {
        string str(p->rotation1[i].rbegin(), p->rotation1[i].rend());
        p->rotation3.push_back(str);
    }
}

/* Helper function for FileSearcher class
 * Checks for all 4 rotations of a template within a given image file (parameter file)
 */
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

/*Helper method for FileSearcher class; performs "grunt work" of pattern matching.
 * This approach is fairly brute-force, and could definitely be improved upon.
 * The efficiency of the search is still only O(n^2), and due to time constraints
 * I haven't been able to improve it as of yet.
 */
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

            //check if there was a match for first line of template; if not, skip to the next line in image
            if (found != std::string::npos)
            {
                *x = found;
                *y = i;

                //signals temporary match; remaining lines of template still must match
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

    //x and y locations represent top left corner of the (unrotated image)
    //Due to this requirement, x and y indices will need to be updated.
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

/* Helper method for FileSearcher class
 * Used to determine how much we can shift by on an image line if an 
 * incomplete match was found
 */
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

#include "wp_utils.def.h"

