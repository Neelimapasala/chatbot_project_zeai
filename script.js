document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const loginForm = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const togglePassword = document.getElementById('togglePassword');
    const flashMessage = document.getElementById('flashMessage');
    const flashText = document.getElementById('flashText');

    const loginCard = document.getElementById('loginCard');
    const forgotCard = document.getElementById('forgotCard');
    const forgotPasswordLink = document.getElementById('forgotPasswordLink');
    const backToLoginLink = document.getElementById('backToLoginLink');

    const requestOtpForm = document.getElementById('requestOtpForm');
    const resetPasswordForm = document.getElementById('resetPasswordForm');

    // Helper: Show custom flash messages
    function showFlash(message, type = 'success') {
        flashText.textContent = message;
        
        // Handle icon changing
        const icon = flashMessage.querySelector('i');
        if (type === 'error') {
            icon.className = 'fa-solid fa-circle-xmark';
            flashMessage.style.backgroundColor = '#ef4444';
        } else {
            icon.className = 'fa-solid fa-circle-check';
            flashMessage.style.backgroundColor = '#10b981';
        }

        flashMessage.classList.add('show');
        setTimeout(() => {
            flashMessage.classList.remove('show');
        }, 3000);
    }

    // 1. Password Visibility Toggle
    if (togglePassword) {
        togglePassword.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            togglePassword.classList.toggle('fa-eye');
            togglePassword.classList.toggle('fa-eye-slash');
        });
    }

    // 2. Clear values on Login Submit
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();

        // Perform authentication check logic here...
        showFlash('Signed in successfully!', 'success');

        // Clear input values immediately
        emailInput.value = '';
        passwordInput.value = '';
    });

    // 3. Navigation: Switch views between Login and Forgot panels
    forgotPasswordLink.addEventListener('click', (e) => {
        e.preventDefault();
        loginCard.classList.add('hide');
        forgotCard.classList.remove('hide');
    });

    backToLoginLink.addEventListener('click', (e) => {
        e.preventDefault();
        forgotCard.classList.add('hide');
        loginCard.classList.remove('hide');
        
        // Reset recovery forms back to Step 1 setup
        requestOtpForm.classList.remove('hide');
        resetPasswordForm.classList.add('hide');
        requestOtpForm.reset();
        resetPasswordForm.reset();
    });

    // 4. Password Reset Step 1: Request OTP code
    requestOtpForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const identifier = document.getElementById('resetIdentifier').value;

        // Visual simulation of generating an OTP dispatch
        showFlash(`OTP code successfully sent to ${identifier}!`, 'success');
        
        // Advance view to step 2 configuration
        requestOtpForm.classList.add('hide');
        resetPasswordForm.classList.remove('hide');
    });

    // 5. Password Reset Step 2: Validate fields & push state live
    resetPasswordForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        // Verify key matching constraints match
        if (newPassword !== confirmPassword) {
            showFlash('Passwords do not match!', 'error');
            return;
        }

        showFlash('Password updated successfully!', 'success');

        // Return client safely home to login frame
        setTimeout(() => {
            resetPasswordForm.reset();
            requestOtpForm.reset();
            requestOtpForm.classList.remove('hide');
            resetPasswordForm.classList.add('hide');
            forgotCard.classList.add('hide');
            loginCard.classList.remove('hide');
        }, 1500);
    });
});