<?php
    require_once "file_manager.php";
    require_once "compile_manager.php";
    require_once "project_manager.php";

    
    /*$pm = new ProjectManager();
    
    $pm->create_bb_project("lab1-bb");
    $pm->create_c_project("lab1-c");
    $pm->create_cpp_project("lab1-cpp");
    $projects = $pm->list_projects();
    
    $fm = new FileManager("mdelong", "lab1-bb");
    $r = $fm->delete_file("index.html");
    if ($r) {
        echo "deleted\n";
    }
    else {
        echo "pain and suffering\n";
    }*/
    
    $cm = new CompilationManager("default", "lab1-c");
    $cm->compile_source();
?>
