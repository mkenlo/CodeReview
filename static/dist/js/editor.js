///editor.js
'use strict';

//$(document).ready(function(){
	if($('#editor')){
		
		var editor = ace.edit("editor");
		editor.setTheme("ace/theme/monokai");
		editor.getSession().setMode("ace/mode/javascript");
	}	
   

	function setCodeValue(){
		$("#codefromEditor").val(editor.getValue());
	}
	$("#problemForm").submit(setCodeValue);

	function changeEditorLanguage(){
		language= $("#code_language").val();
		editor.getSession().setMode("ace/mode/"+$("#code_language").val());
	}
	function setEditorMode(language){
		editor.getSession().setMode("ace/mode"+language);
	}

	function setEditorValue(codeToDisplay){
		editor.setValue(codeToDisplay);
	}

//});



