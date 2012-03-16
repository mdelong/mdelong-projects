<?php
    require_once "create_projects.php";
    
    $fu = new FileUpload();
    $fu->create_s3_instance();
    $result = $fu->create_bb_project("MyBBProject");
    $result = $fu->create_c_project("MyCProject");
    $result = $fu->create_cpp_project("MyCppProject");
    $result = $fu->create_java_project("MyJavaProject");
?>
