#ifndef __MAIN_H__
#define __MAIN_H__

#include <string>
#include <vector>
#include <stdio.h>

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
    std::vector<std::string> data;//contents stored as vector of strings
    std::string filename;
} FileData;

/* stores template/paralleldo data. All 4 rotations of the template are stored
 * in this data structure. Rotations 0-3 correspond to 0-90-180-270 degrees, respectively.*/
typedef struct p
{
    unsigned int height;
    unsigned int width;
    std::vector<std::string> rotation0;
    std::vector<std::string> rotation1;
    std::vector<std::string> rotation2;
    std::vector<std::string> rotation3;
    std::string filename;
} Paralleldo;
    
class FNameMsg : public CMessage_FNameMsg {
    public:
        char *fname;
        FNameMsg(){};
};

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

class FileReader : public CBase_FileReader {    

public:
    FileReader(){};
    FileReader(CkMigrateMessage *m){};
    void ReadFile(FNameMsg *msg);
};

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

class Main : public CBase_Main
{
    private:
        CProxy_FileReader freaders;
        CProxy_FileSearcher fsearchers;
        vector<FDataMsg*> tdata;
        int nfinished;
        int nimages;
        int ntemplates;
        int searchNo;
        double startTime;
		int getFilenames(string &dirname, string &fext, vector<string> &fnames);

    public:
        Main(CkArgMsg *m);
        Main(CkMigrateMessage *m);
        void done();
        void checkIn();
        void RecvFile(FDataMsg *fd);
};

#endif
