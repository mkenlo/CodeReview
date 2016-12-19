///editor.js
'use strict';

//$(document).ready(function(){

   var editor = ace.edit("editor");
	editor.setTheme("ace/theme/monokai");
	editor.getSession().setMode("ace/mode/javascript");

	function setCodeValue(){
		$("#codefromEditor").val(editor.getValue());
	}
	$("#problemForm").submit(setCodeValue);

	function changeEditorLanguage(){
		language= $("#code_language").val();
		editor.getSession().setMode("ace/mode/"+language);
	}
	function setEditorMode(language){
		editor.getSession().setMode("ace/mode"+language);
	}

	function setEditorValue(codeToDisplay){
		editor.setValue(codeToDisplay);
	}

//});



