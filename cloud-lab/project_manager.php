<?php
    $SDK_HOME = './aws_php_sdk/';
    error_reporting(-1); // Enable full-blown error reporting.
	header("Content-type: text/plain; charset=utf-8"); // Set plain text headers
	require_once $SDK_HOME . 'sdk.class.php'; // Include the SDK
    require_once 'file_manager.php';
    
    class ProjectManager
    {
        private $s3;

        function __construct() {
            $this->s3 = new AmazonS3();
        }
        
        // for page after login
        function list_projects() {
            $response = $this->s3->list_buckets();
            $project_list = array();
            foreach ($response->body->Buckets[0] as $bucket_name) {
                echo (string) $bucket_name->Name . PHP_EOL;
                $project_list[] = $bucket_name->Name;
            }
            return $project_list;
        }
        
        function create_bb_project($project_name) {
            $bucket = $this->create_project($project_name);
            if ($bucket) {
                $fm = new FileManager("default", $bucket);
                $fm->create_html_source("index");
                $fm->create_js_source("script");
                $fm->create_css_source("style");
                return true;
            }
            else {
                return false;
            }
        }
        
        function create_c_project($project_name) {
            $bucket = $this->create_project($project_name);
            if ($bucket) {
                $fm = new FileManager("default", $bucket);
                $fm->create_c_source("main");
                $fm->create_h_source("main");
                return true;
            }
            else {
                return false;
            }
        }
        
        function create_cpp_project($project_name) {
            $bucket = $this->create_project($project_name);
            if ($bucket) {
                $fm = new FileManager("default", $bucket);
                $fm->create_cpp_source("main");
                $fm->create_hpp_source("main");
                return true;
            }
            else {
                return false;
            }
        }
        
        function delete_project($project_name) {
            $bucket = strtolower($project_name);
            $response = $this->s3->delete_bucket($bucket, true);
            return $response->isOk();
        }

        private function create_project($project_name) {
            $bucket = strtolower($project_name);
            
            if (!($this->s3->if_bucket_exists($bucket))) {
                $create_bucket_response = $this->s3->create_bucket($bucket, AmazonS3::REGION_US_W1);
                
                if ($create_bucket_response->isOk()) {
                    $exists = $this->s3->if_bucket_exists($bucket);
                     while (!$exists)
                     {
                        sleep(1);
                        $exists = $this->s3->if_bucket_exists($bucket);
                     }
                    
                    return $bucket;
                }
                
                else {
                    echo "Error: failed to create project\n";
                    return false;
                }
            }

            else {
                echo "Error: project named " . $project_name . " already exists.\n";
                return false;
            }
        }
    }
?>