var parentDOM = document.getElementById("content");
var test=parentDOM.getElementsByClassName("test")

var now=new Date();
var sec=now.getSeconds();
var min=now.getMinutes();
var hour=now.getHours();

test.innerHTML( "+"+(hour>9?hour:"0"+hour)
                  +":"+(min>9?min:"0"+min)
                  +":"+(sec>9?sec:"0"+sec)  );