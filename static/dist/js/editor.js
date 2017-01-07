///editor.js
"use strict";

if($('#editor')){

var editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.getSession().setMode("ace/mode/javascript");
}	


function setCodeValue(){
	$("#codefromEditor").val(editor.getValue());
}

function changeEditorLanguage(){
	editor.getSession().setMode("ace/mode/"+$("#code_language").val());
}
function setEditorMode(language){
	editor.getSession().setMode("ace/mode/"+language);
}

function setEditorValue(codeToDisplay){
	editor.setValue(codeToDisplay);
}



$("#problemForm").submit(setCodeValue);
setEditorMode($("#code_language").val());




