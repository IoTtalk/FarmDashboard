function validatePasswordLength(password) {
  return (password.length >= 6);
}

function validatePasswordCombination(password) {
  const regex_array = [
    /^[^!"#\$%&'\(\)\*\+,-\.\/:;<=>\?@\[\\\]\^_`{\|}~]*[!"#\$%&'\(\)\*\+,-\.\/:;<=>\?@\[\\\]\^_`{\|}~]/,
    /^(?=[^A-Z]*[A-Z])/,
    /^(?=[^a-z]*[a-z])/,
    /^(?=[^\d]*[\d])/,
  ];
  let counter = 0;

  for ( const re of regex_array ) {
    if ( !re.test(password) ) {
      continue;
    }
    ++counter;
  }

  if ( counter < 3 ) {
    return false;
  }

  return true;
}

function validatePassword(password, oldPassword) {
  if ( password == oldPassword ) {
    return {'validity': false, 'reason': 'New password can not be identical to the original one', };
  } else if ( !validatePasswordLength(password) ) {
    return {'validity': false, 'reason': 'Password length must be greater or equal to 6', };
  } else if ( !validatePasswordCombination(password) ) {
    return {
      'validity': false,
      'reason': 'Password must contain at least three of them: Uppercase letters, \
                 Lowercase letters, numbers and special symbols', };
  } else {
    return {'validity': true, };
  }
}
