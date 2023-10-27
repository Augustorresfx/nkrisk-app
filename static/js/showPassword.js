const showPasswordButton = document.querySelector('#showPassword');
const passwordInput = document.querySelector('#password');
showPasswordButton.addEventListener('click', () => {
  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    
  } else {
    passwordInput.type = 'password';
    
  }
});