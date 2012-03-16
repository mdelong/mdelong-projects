<?php

    $SDK_HOME = './aws_php_sdk/';
    error_reporting(-1); // Enable full-blown error reporting.
	header("Content-type: text/plain; charset=utf-8"); // Set plain text headers
	require_once $SDK_HOME . 'sdk.class.php'; // Include the SDK
    
    function file_path($file)
    {
        return !is_dir($file) ? realpath($file) : null;
    }
    
    class FileUpload
    {
        private $s3, $bucket;
        
        function create_s3_instance() {
            $this->s3 = new AmazonS3();
        }
        
        function get_all_buckets() {
            $response = $this->s3->list_buckets();
            foreach ($response->body->Buckets[0] as $bucket_name) {
                echo (string) $bucket_name->Name;
                $objects = $s3->get_object_list($bucket_name);
                foreach ($objects as $object) {
                    echo $object . " " . $s3->get_object_url($bucket_name, $object, '5 minutes') . PHP_EOL;
                }
            }
        }
        
        function get_all_files() {
            $objects = $s3->get_object_list($this->bucket);
            $results = array();
            
            foreach ($objects as $object) {
                echo $object . " " . $s3->get_object_url($this->bucket, $object, '5 minutes') . PHP_EOL;
                $file_contents = get_file($this->bucket, $object);
                if ($file_contents) {
                    $results[$object] = $file_contents;
                }
            }
            
            return $results;
        }
        
        function get_file($bucket_name, $object_name) {
            $url = $this->s3->get_object_url($bucket_name, $object_name, '5 minutes');
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
        
        function create_bb_project($name) {
            return $this->create_project($name, "./defaultproj/BB/");
        }
        
        function create_c_project($name) {
            return $this->create_project($name, "./defaultproj/C/");            
        }
        
        function create_cpp_project($name) {
            return $this->create_project($name, "./defaultproj/CPP/");            
        }
        
        function create_java_project($name) {
            return $this->create_project($name, "./defaultproj/JAVA/");           
        }
        
        function save_file($name, $data) {
            $filename = "mdelong/" . $name;
            $saved_data = json_encode($data);
            $options = array('body' => $saved_data);
            $this->s3->create_object($this->bucket, $filename, $options);
        }
        
        function delete_file($name) {
            $filename = "mdelong/" . $name;
            $response = $this->s3->delete_object($this->bucket, $filename);
            return $response->isOk();
        }
        
        function delete_project() {
            $response = $this->s3->delete_bucket($this->bucket, true);
            return $response->isOk();
        }

        private function create_project($name, $input_dir) {
            $this->bucket = strtolower("mdelong" . '-' . $name);
            
            $exists = $this->s3->if_bucket_exists($this->bucket);
            if (!$exists) {
                $create_bucket_response = $this->s3->create_bucket($this->bucket, AmazonS3::REGION_US_W1);
                
                if ($create_bucket_response->isOk()) {
                    echo "Project " . $name . " created from input dir " . $input_dir . "\n";
                    $exists = $this->s3->if_bucket_exists($this->bucket);
                    echo $this->bucket . PHP_EOL;
                     while (!$exists)
                     {
                        sleep(1);
                        $exists = $this->s3->if_bucket_exists($this->bucket);
                        echo $exists;
                     }
                    
                    echo $this->bucket . " done\n";
                    return $this->upload_files($input_dir);
                }
                
                else {
                    echo "Error: could not create bucket" . PHP_EOL;
                    return false;
                }
            }
            
            else {
                return true;
            }
        }
        
        private function upload_files($dir) {
            $file_list = $this->filter_file_list(glob($dir . '*'));
            $individual_files = array();
            
            foreach($file_list as $file) {
                $filename = explode(DIRECTORY_SEPARATOR, $file);
                $filename = array_pop($filename);
                $individual_files[] = $filename;
                $this->s3->batch()->create_object($this->bucket, $filename, array('fileUpload' => $file));
            }
            
            $file_upload_response = $this->s3->batch()->send(); //execute requests queue
            
            if (true)
            /* Check if all requests were successful */
            if ($file_upload_response->areOK())
            {
                foreach ($individual_files as $filename)
                {
                    echo $filename . "\n";
                    echo $this->s3->get_object_url($this->bucket, $filename, '5 minutes') . PHP_EOL . PHP_EOL; // display URL for each uploaded file
                }
                return true;
            }
            
            else {
                return false;
            }
        }
        
        private function filter_file_list($arr)
        {
            return array_values(array_filter(array_map('file_path', $arr)));
        }
    }
?>