/*
 * Michael Delong, University of Guelph, Student ID 0636022
 * Term Project for CIS*3090, Fall 2011
 * This program implements the "Where's Paralleldo" template matching
 * problem from assignments 2 and 3 using the Charm++ paradigm.
 * 
 * wp_utils.h
 * This file contains all function and class declarations for the following:
 * --- Message classes
 * --- File Reader chares
 * --- File Search chares
 */

#ifndef __WP_UTILS_H__
#define __WP_UTILS_H__

#include <string>
#include <vector>
#include "main.decl.h"

using namespace std;

typedef enum {
    Rotation_0 = 0,
    Rotation_90,
    Rotation_180,
    Rotation_270
} Rotation;

//stores image data (height, width, filename, and contents)
typedef struct fdata
{
    unsigned int height;
    unsigned int width;
    vector<string> data;//contents stored as vector of strings
    string filename;
} FileData;

/* stores template/paralleldo data. All 4 rotations of the template are stored
 * in this data structure. Rotations 0-3 correspond to 0-90-180-270 degrees, respectively.*/
typedef struct p
{
    unsigned int height;
    unsigned int width;
    vector<string> rotation0;
    vector<string> rotation1;
    vector<string> rotation2;
    vector<string> rotation3;
    string filename;
} Paralleldo;

/*Class for reader chares. 
 *These objects read in file data and pass it back to the main chare
 */
class FileReader : public CBase_FileReader {    

public:
    FileReader(){};
    FileReader(CkMigrateMessage *m){};
    void ReadFile(FNameMsg *msg);
};

/* Class for search chares.
 * These objects are passed an image file from main, and search the file
 * for one template match. Templates are stored in the "templates" vector.
 */
class FileSearcher : public CBase_FileSearcher {    

private:
    vector<Paralleldo> templates;
    void createRotations(Paralleldo *p);
    bool findPattern(FileData *file, Paralleldo *pattern);
    int getShift(string str);
    bool match(vector<string> data, vector<string> pattern, 
                int *x, int *y, Rotation rot);

public:
    FileSearcher(){};
    void GetImageData(FDataMsg *img);
    void GetTemplate(FDataMsg *t);
};


/*Encapsulates a file name*/    
class FNameMsg : public CMessage_FNameMsg {
    public:
        char *fname;
        FNameMsg(){};
};

/*Encapsulates file data (dimensions, filename, and actual data)*/
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

#endif

