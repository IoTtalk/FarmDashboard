function validateNewPassword() {
  validationResult = validatePassword($('#newpwd').val(), $('#oldpwd').val());

  if ( !(validationResult.validity) ) {
    // Show the warning message if current new password does not conform the rules
    $('#newpwd-warning').text(validationResult.reason);

    return false;
  }

  // Clear the warning message if current new password conform the rules
  $('#newpwd-warning').text('');

  return true;
}

function validateOriginalPassword() {
  if ( !($('#oldpwd').val()) ) {
    // Show the warning message if old password is empty
    $('#oldpwd-warning').text('Please enter your old password');

    return false;
  }

  // Clear the warning message if old password is not empty
  $('#oldpwd-warning').text('');

  return true;
}

function validateRepeatedNewPassword() {
  if ( ($('#newpwd').val()) != ($('#repnewpwd').val()) ) {
    $('#repnewpwd-warning').text(
      'The password you entered does not match the original one');
    return false;
  }

  // Clear the warning message if two passwords match
  $('#repnewpwd-warning').text('');

  return true;
}

function handleNewPasswordBlurEvent() {
  if ( !($('#newpwd').val()) ) {
    $('#newpwd-warning').text('Please enter your new password');
    $('#repnewpwd-warning').text('');
  }
}

function handleRepeatedNewPasswordBlurEvent() {
  if ( !($('#repnewpwd').val()) ) {
    $('#repnewpwd-warning').text('Please enter your new password again');
  }
}

function mysubmit() {
  if ( !validateOriginalPassword() || !validateNewPassword() || !validateRepeatedNewPassword() ) {
    return;
  }

  axios.post('/api/user/pwd',
             {'old_password': $('#oldpwd').val(),
              'new_password': $('#newpwd').val()},
             {'headers': {'X-CSRFToken': $('#csrf-token').val(), }, })
       .then(() => {
         alert('Password has changed');
         location.reload();
       })
       .catch((error) => {
         alert(error.response.data);
         location.reload();
       });
}

$(()=>{
  $('#oldpwd').bind('input', validateOriginalPassword);
  $('#oldpwd').bind('blur', validateOriginalPassword);
  $('#newpwd').bind('input', validateNewPassword);
  $('#newpwd').bind('blur', handleNewPasswordBlurEvent);
  $('#repnewpwd').bind('input', validateRepeatedNewPassword);
  $('#repnewpwd').bind('blur', handleRepeatedNewPasswordBlurEvent);
});
