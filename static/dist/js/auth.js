function start() {
      gapi.load('auth2', function() {
        gapi.auth2.init();
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

