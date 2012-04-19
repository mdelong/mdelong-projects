<?php
    
    require_once './file_manager.php';
    
    class CompilationManager {
        
        private $username, $project_name, $fs;
        
        function __construct($user, $project) {
            $this->username     = $user;
            $this->project_name = $project;
            $this->fs = new FileManager($user, $project);
        }
        
        /*function __destruct() {
            echo "rm -r " . "~/" . $this->username . "/" . $this->project_name;
            exec("rm -r " . "~/" . $this->username . "/" . $this->project_name);
        }*/
        
        function compile_C_source() {
            $this->create_compile_dir();
            $source_dir = "./" . $this->username . "/" . $this->project_name;
            exec("gcc " . $source_dir . "/*.c -o " . $source_dir . "/main -Wall -std=c99 2> " . $source_dir . "/compile.txt");
            
            $fh = fopen($source_dir . "/compile.txt", "r");
            if ($fh) {
                $sz = filesize("./" . $this->username . "/compile.txt");
                if ($sz > 0) {
                    $results = fread($fh, $sz);
                    fclose($fh);
                    return $results;    
                }
                
                else {
                    return "";
                }
            }
            
            else {
                return "";
            }
        }
        
        function compile_CPP_source() {
            $this->create_compile_dir();
            $source_dir = "./" . $this->username . "/" . $this->project_name;
            exec("g++ " . $source_dir . "/*.c -o " . $source_dir . "/main 2> " . $source_dir . "/compile.txt");
            
            $fh = fopen($source_dir . "/compile.txt", "r");
            if ($fh) {
                $sz = filesize("./" . $this->username . "/compile.txt");
                if ($sz > 0) {
                    $results = fread($fh, $sz);
                    fclose($fh);
                    return $results;    
                }
                
                else {
                    return "";
                }
            }
            
            else {
                return "";
            }
        }
        
        // We will likely change this to attach an EC2 volume, rather than creating a temp directory in the default user directory.
        // This needs to be done for both security and convenience reasons
        private function create_compile_dir() {
            $source_dir = "./" . $this->username . "/" . $this->project_name;
            
            if (!file_exists($source_dir)) {
                mkdir($source_dir, 0, true);
                $files = $this->fs->get_source_files($this->username, $this->project_name);
                
                foreach ($files as $filename => $file_contents) {
                    $fh = fopen($source_dir . $filename, "w");
                    fwrite($fh, $file_contents);
                    fclose($fh);
                }
            }
        }
        
        private function get_source_files() {
            return $this->fs->get_project_files($this->username, $this->project_name);
        }
        
        function run_source($args) {
            $source_dir = "./" . $this->username . "/" . $this->project_name;
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
