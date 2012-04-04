<?php

    $DEFAULT_HTML = "<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\">\n<html>\n<head>\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">\n<meta name=\"viewport\" id=\"viewport\" content=\"height=600, width=1024, user-scalable=no\" />\n<title>BlackBerry Default App</title>\n<link href=\"style.css\" rel=\"stylesheet\" type=\"text/css\">\n<script type=\"text/javascript\" src=\"script.js\"></script>\n</head>\n\n<body>\n<h2>Hello World!</h2>\n</body>\n</html>\n";
    
    $DEFAULT_CSS = "@CHARSET \"ISO-8859-1\";\n\nbody {\n/* Body styles go here */\n}\n\n#header {\n/* Header styles go here */\n}\n";
    
    $DEFAULT_JS  = "\nfunction foo() {\n    return;\n}\n";
    
    $DEFAULT_C = "\n#include <stdio.h>\n#include \"main.h\"\nint main(void) {\n    printf(\"Hello World\n\");    return 0;\n}\n";
    
    $DEFAULT_CPP = "\n#include <iostream>\n#include \"main.h\"\n\nint main (void) {\n    std::cout << \"Hello world\" << endl;\n    return 0;\n}\n";
    
    $DEFAULT_H = "\n#ifndef _main_h\n#define _main_h\n\n#endif\n";
    
    
    $SDK_HOME = './aws_php_sdk/';
    error_reporting(-1); // Enable full-blown error reporting.
	header("Content-type: text/plain; charset=utf-8"); // Set plain text headers
	require_once $SDK_HOME . 'sdk.class.php'; // Include the SDK
    
    
    function startsWith($haystack, $needle) {
        $length = strlen($needle);
        return (substr($haystack, 0, $length) === $needle);
    }
    
    class FileManager
    {
        private $s3, $project, $username;
        
        function __construct($user, $project_name) {
            $this->s3      = new AmazonS3();
            $this->project = strlower($name);
            $this->user    = $username;
                        
            if (!($this->has_edited())) {
                $this->copy_from_default();
            }
        }

        // for listing files in IDE tab
        function get_project_files() {
            $files   = $this->s3->get_object_list($this->project);
            $results = array();
            
            foreach ($files as $file) {
                echo $file . " " . $s3->get_object_url($this->project, $file, '5 minutes') . PHP_EOL;
                
                if (startsWith($file, $this->username)) {
                    $file_contents = $this->get_file($this->project, $file);
                    if ($file_contents) {
                        $results[$file] = $file_contents; //key-value pairing of filename and contents
                    }
                }
            }
            return $results;
        }
        
        private function get_project_filenames($user) {
            $files   = $this->s3->get_object_list($this->project);
            $results = array();
            
            foreach ($files as $file) {
                echo $file . " " . $s3->get_object_url($this->project, $file, '5 minutes') . PHP_EOL;
                
                if (startsWith($file, $user)) {
                    $file_contents = $this->get_file($this->project, $file);
                    if ($file_contents) {
                        $results[] = $file;
                    }
                }
            }
            return $results;
        }
        
        // check if this is the first user login (user should have created his/her own files)
        private function has_edited() {
            return (sizeof($this->get_project_files($this->username)) != 0);
        }
        
        private function copy_from_default() {
            
            $files = $this->get_project_filenames("default");
                
            foreach ($files as $file) {
                $response = $this->s3->copy_object(
                                                   array( // Source
                                                         'bucket'   => $this->project,
                                                         'filename' => $file
                                                         ),
                                                   array( // Destination
                                                         'bucket'   => $this->project,
                                                         'filename' => $this->username . "/" . $file
                                                         )
                                                   );                
            }

            // Success?
            var_dump($response->isOK());
        }
        
        // retrieve file data
        function get_file($filename) {
            $url = $this->s3->get_object_url($this->project, $filename, '5 minutes');
            $responseData = @file_get_contents($url);

            if ($responseData) {
                $responseArray = json_decode($responseData, true);
                if ($is_array($responseArray)) {
                    return $responseArray;
                }

                else {
                    return false;
                }
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
                $this->save_file($this->username . "/" . $name . ".h", $DEFAULT_H);
            }            
        }
        
        function create_cpp_source($name) {
            $exists = $this->s3->if_bucket_exists(strtolower($this->project));
            if (!$exists) {
                echo "Error: could not find bucket\n";
                return false;
            }
            
            else {
                $this->save_file($this->username . "/" . $name . ".cpp", $DEFAULT_CPP);
            }            
        }
        
        private function save_file($filename, $data) {
            $saved_data = json_encode($data);
            $options = array('body' => $saved_data);
            $this->s3->create_object($this->project, $filename, $options);
        }
        
        function delete_file($name) {
            $filename = $this->username . "/" . $name;
            $response = $this->s3->delete_object($this->project, $filename);
            return $response->isOk();
        }
    }
?>