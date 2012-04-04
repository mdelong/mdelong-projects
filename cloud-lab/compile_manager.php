<?php
    
    require_once './file_manager.php';
    
    class CompilationManager {
        
        private $username, $project_name, $fs;
        
        function __construct($user, $project) {
            $username     = $user;
            $project_name = $project;
            $this->fs = new FileManager($user, $project);
        }
        
        function __destruct() {
            echo "rm -r " . "~/" . $this->username . "/" . $this->project_name;
            //exec("rm -r " . "~/" . $this->username . "/" . $this->project_name);
        }
        
        function compile_source($username) {
            $this->create_compile_dir();
            $source_dir = "~/" . $this->username . "/" . $this->project_name;
            exec("gcc " . $source_dir . "/*.c -o main - Wall -std=c99 2> " . $source_dir . "/compile.txt");
            
            $fh = fopen($source_dir . "/compile.txt");
            $results = fread($fh, filesize("~/" . $this->username . "/compile.txt"));
            fclose($fh);
            return $results;
        }
        
        // We will likely change this to attach an EC2 volume, rather than creating a temp directory in the default user directory.
        // This needs to be done for both security and convenience reasons
        private function create_compile_dir() {
            $source_dir = "~/" . $this->username . "/" . $this->project_name;
            mkdir(($source_dir, 0, true));
            $files = $this->fs->get_source_files($this->username, $this->project_name);
            
            foreach ($files as $filename => $file_contents) {
                $fh = fopen($source_dir . $filename, "w");
                foreach ($file_contents as $line) { //maybe just write the contents in one shot? Have to look into this
                    fwrite($fh, $line . "\n");
                }
                fclose($fh);
            }
        }
        
        private function get_source_files() {
            return $this->fs->get_project_files($this->username, $this->project_name);
        }
        
        function run_source($args) {
            $source_dir = "~/" . $this->username . "/" . $this->project_name;
            $command = $source_dir . "/main";
            
            if ($args) {
                foreach ($args as $arg) {
                    $command = $command . " " . $arg;
                }
            }
            exec($command . " 2> " . $source_dir . "/run.log >> " . $source_dir . "/run.log");
            $fh = fopen($source_dir . "/run.log");
            $results = fread($fh, filesize($source_dir . "/run.log"));
            fclose($fh);
            return $results;
        }
    }
    
?>
