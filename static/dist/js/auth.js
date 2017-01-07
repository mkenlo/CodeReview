function start() {
      gapi.load('auth2', function() {
        gapi.auth2.init({
          client_id: '99393343552-3hmud19ig349jqjs2peq7biv918qi9m0.apps.googleusercontent.com'
        });
      });
}

function gSignIn(STATE){
  gapi.load('auth2', function() {
    gapi.auth2.init({
      client_id: '99393343552-3hmud19ig349jqjs2peq7biv918qi9m0.apps.googleusercontent.com'
    });

  var GoogleAuth  = gapi.auth2.getAuthInstance();
  GoogleAuth.signIn().then(function(response){//request to sign in

      GoogleAuth.grantOfflineAccess({'redirect_uri': 'postmessage'}).then(function(resp) {
        $.ajax({
          type:'POST',
          url:'/gconnect?state='+STATE,
          processData:false,
          contentType:'application/octet-stream;charset=utf-8',
          data: resp.code,
          error: function(result){ 
            var msg = '<div class="alert alert-danger alert-dismissible">'+
                  '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>'+
                  '<p><i class="icon fa fa-ban"></i>'+result.responseText+'</p>'
                  '</div>'; 
            $('.login-logo').after(msg);      
          },
          success: function(result){
            var msg = '<div class="alert alert-success">'+
                  '<h4><i class="icon fa fa-check"></i>'+result+'</h4>'+
                  '</div>';
            $('.login-logo').after(msg);
            setTimeout(function() {
              window.location.href = "/start";
            }, 2500);       
          }        

        });
      });
    });
  });
     
}

window.fbAsyncInit = function() {
    FB.init({
      appId      : '1136408746406465',
      status     : true, 
      xfbml      : true,
      version    : 'v2.8'
    });
    FB.AppEvents.logPageView();
};
(function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.8";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));


function fSignIn(STATE){
  console.log("Here Is fSignIn");  
  FB.login(function(response) {
    if (response.authResponse) {

      $.ajax({
        type:'POST',
        url:'/fconnect?state='+STATE,
        processData:false,
        contentType:'application/octet-stream;charset=utf-8',
        data: response.authResponse.accessToken,
        error: function(result){
          //console.log(result.responseText); 
          var msg = '<div class="alert alert-danger alert-dismissible">'+
                '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>'+
                '<p><i class="icon fa fa-ban"></i>'+result.responseText+'</p>'
                '</div>'; 
          $('.login-logo').after(msg);      
        },
        success: function(result){
          var msg = '<div class="alert alert-success">'+
                '<h4><i class="icon fa fa-check"></i>'+result+'</h4>'+
                '</div>';
          $('.login-logo').after(msg);
          setTimeout(function() {
            window.location.href = "/start";
          }, 2500);       
        }  
      });
     
    } else {
     console.log('User cancelled login or did not fully authorize.');
    }
  });
}

function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut();

    FB.getLoginStatus(function(response) {
      if (response.status === 'connected') {
          FB.logout(function(response) {
              
          });
      }
    });
    
  }

