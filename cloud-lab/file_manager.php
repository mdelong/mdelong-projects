<?php
    
    $SDK_HOME = './aws_php_sdk/';
    error_reporting(-1); // Enable full-blown error reporting.
	header("Content-type: text/plain; charset=utf-8"); // Set plain text headers
	require_once $SDK_HOME . 'sdk.class.php'; // Include the SDK
    
    
    function startsWith($haystack, $needle) {
        $length = strlen($needle);
        $s = substr($haystack, 0, $length);        
        return (substr($haystack, 0, $length) == $needle);
    }
    
    class FileManager
    {
        private $s3, $project, $username;
        
        function __construct($user, $project_name) {
            $this->s3       = new AmazonS3();
            $this->project  = strtolower($project_name);
            $this->username = $user;
                        
            if (!($this->has_edited())) {
                echo "has edited = false" . PHP_EOL;
                $this->copy_from_default();
            }
            else {
                echo "has edited = true" . PHP_EOL;
            }
        }
        
        private function get_project_filenames($user) {
            $files   = $this->s3->get_object_list($this->project);
            $results = array();
            
            foreach ($files as $file) {
                echo $file . PHP_EOL;
                if (startsWith($file, $user . "/")) {
                    $results[] = $file;
                }
            }
            return $results;
        }
        
        // check if this is the first user login (user should have created his/her own files)
        private function has_edited() {
            return (sizeof($this->get_project_filenames($this->username)) != 0);
        }
        
        private function copy_from_default() {
            $files = $this->get_project_filenames("default");
            echo $this->username . PHP_EOL;
            foreach ($files as $file) {                
                $this->save_file($this->username . "/" . substr($file, 8), $this->get_file($file));
            }
        }
        
        function get_source_files() {
            $files   = $this->s3->get_object_list($this->project);
            $results = array();
            
            foreach ($files as $file) {
                if (startsWith($file, $this->username . "/")) {
                    $contents = $this->get_file($file);
                    if ($contents) {
                        $results[substr($file, strlen($this->username))] = $contents;
                    }
                }
            }
            return $results;
        }
        
        // retrieve file data
        function get_file($filename) {
            $url = $this->s3->get_object_url($this->project, $filename, '5 minutes');
            $responseData = @file_get_contents($url);

            if ($responseData) {
                return $responseData;
            }

            else {
                return false;
            }
        }
        
        function create_html_source($name) {
            $exists = $this->s3->if_bucket_exists(strtolower($this->project));
            if (!$exists) {
                echo "Error: could not find bucket\n";
                return false;
            }
            
            else {
                $DEFAULT_HTML = "<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\">\n<html>\n    <head>\n        <meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">\n        <meta name=\"viewport\" id=\"viewport\" content=\"height=600, width=1024, user-scalable=no\" />\n\n        <title>BlackBerry Default App</title>\n        <link href=\"style.css\" rel=\"stylesheet\" type=\"text/css\">\n        <script type=\"text/javascript\" src=\"script.js\"></script>\n    </head>\n\n    <body>\n        <h2>Hello World!</h2>\n    </body>\n</html>\n";
                $this->save_file($this->username . "/" . $name . ".html", $DEFAULT_HTML);
            }            
        }
        
        function create_js_source($name) {
            $exists = $this->s3->if_bucket_exists(strtolower($this->project));
            if (!$exists) {
                echo "Error: could not find bucket\n";
                return false;
            }
            
            else {
                $DEFAULT_JS  = "\nfunction foo() {\n    return;\n}\n";
                $this->save_file($this->username . "/" . $name . ".js", $DEFAULT_JS);
            }            
        }
        
        function create_css_source($name) {
            $exists = $this->s3->if_bucket_exists(strtolower($this->project));
            if (!$exists) {
                echo "Error: could not find bucket\n";
                return false;
            }
            
            else {
                $DEFAULT_CSS = "@CHARSET \"ISO-8859-1\";\n\nbody {\n/* Body styles go here */\n}\n\n#header {\n/* Header styles go here */\n}\n";
                $this->save_file($this->username . "/" . $name . ".css",  $DEFAULT_CSS);
            }            
        }
        
        function create_h_source($name) {
            $exists = $this->s3->if_bucket_exists(strtolower($this->project));
            if (!$exists) {
                echo "Error: could not find bucket\n";
                return false;
            }
            
            else {
                $DEFAULT_H = "\n#ifndef _main_h\n#define _main_h\n\n#endif\n";
                $this->save_file($this->username . "/" . $name . ".h", $DEFAULT_H);
            }            
        }
        
        function create_hpp_source($name) {
            $exists = $this->s3->if_bucket_exists(strtolower($this->project));
            if (!$exists) {
                echo "Error: could not find bucket\n";
                return false;
            }
            
            else {
                $DEFAULT_HPP = "\n#ifndef _main_hpp\n#define _main_hpp\n\n#endif\n";
                $this->save_file($this->username . "/" . $name . ".hpp", $DEFAULT_HPP);
            }            
        }
        
        function create_cpp_source($name) {
            $exists = $this->s3->if_bucket_exists(strtolower($this->project));
            if (!$exists) {
                echo "Error: could not find bucket\n";
                return false;
            }
            
            else {
                $DEFAULT_CPP = "\n#include <iostream>\n#include \"main.hpp\"\n\nint main (void) {\n    std::cout << \"Hello world\" << endl;\n    return 0;\n}\n";
                $this->save_file($this->username . "/" . $name . ".cpp", $DEFAULT_CPP);
            }            
        }
        
        function create_c_source($name) {
            $exists = $this->s3->if_bucket_exists(strtolower($this->project));
            if (!$exists) {
                echo "Error: could not find bucket\n";
                return false;
            }
            
            else {
                $DEFAULT_C = "\n#include <stdio.h>\n#include \"main.h\"\n\nint main(void) {\n    printf(\"Hello World\\n\");\n    return 0;\n}\n";
                $this->save_file($this->username . "/" . $name . ".c", $DEFAULT_C);
            }            
        }
        
        function save_file($filename, $data) {
            $options = array('body' => $data);
            $this->s3->create_object($this->project, $filename, $options);
        }
        
        function delete_file($name) {
            $filename = $this->username . "/" . $name;
            $response = $this->s3->delete_object($this->project, $filename);
            return $response->isOk();
        }
    }
?>