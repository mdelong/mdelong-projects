/*
 * Michael Delong, University of Guelph, Student ID 0636022
 * Term Project for CIS*3090, Fall 2011
 * This program implements the "Where's Paralleldo" template matching
 * problem from assignments 2 and 3 using the Charm++ paradigm.
 * 
 * main.h
 *
 * This file contains all function and class declarations for the mainchare 
 * or application entry point.
 */

#ifndef __MAIN_H__
#define __MAIN_H__

#include <vector>
#include <string>

using namespace std;

/* Main chare, and entry point for the application.*/
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
        void done();

    public:
        Main(CkArgMsg *m);
        Main(CkMigrateMessage *m);
        void checkIn();
        void RecvFile(FDataMsg *fd);
};

#endif

