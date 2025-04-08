// Define variables in global scope
window.video = document.getElementById('video');
window.canvas = document.getElementById('canvas');
window.context = canvas.getContext('2d');
window.stream = null;
window.cameraStatus = document.getElementById('cameraStatus');

// Access Webcam with detailed error handling
window.startCamera = function() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        cameraStatus.textContent = 'Camera not supported by your browser.';
        return;
    }

    cameraStatus.textContent = 'Requesting camera permission...';
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } }) // Force front camera
        .then(function(newStream) {
            stream = newStream;
            video.srcObject = stream;
            video.play();
            cameraStatus.textContent = 'Camera is active. Point to your face.';
            console.log('Camera stream started successfully.');
        })
        .catch(function(err) {
            console.error('Camera error:', err);
            cameraStatus.textContent = 'Camera access denied: ' + err.message;
            alert('Camera failed. Check browser settings (F12 console) or click "Retry Camera". Error: ' + err.message);
        });
};

// Retry Camera Function
window.retryCamera = function() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
    startCamera();
};

// Start camera on page load
window.addEventListener('load', startCamera);

// Capture Image Function
window.captureImage = function() {
    if (stream && video.readyState === video.HAVE_ENOUGH_DATA) {
        context.drawImage(video, 0, 0, 320, 240);
        let imageData = canvas.toDataURL('image/png');
        document.getElementById('face_image').value = imageData;
        cameraStatus.textContent = 'Face captured successfully!';
        alert('Face Captured Successfully!');
    } else {
        cameraStatus.textContent = 'Camera not ready. Click "Retry Camera" if needed.';
        alert('Camera not ready. Ensure permissions are granted.');
        retryCamera();
    }
};

// Ensure face is captured and passwords match (for register)
document.getElementById('register-form')?.onsubmit = function(event) {
    if (!document.getElementById('face_image').value) {
        alert('Please capture your face first!');
        event.preventDefault();
        return false;
    }

    const password = document.getElementById('id_password1')?.value;
    const passwordConfirm = document.getElementById('id_password2')?.value;

    if (password !== passwordConfirm) {
        alert('Passwords do not match!');
        event.preventDefault();
        return false;
    }

    const minLength = password?.length < 8;
    const isNumericOnly = /^\d+$/.test(password);
    const hasNoSpecialChar = !/[!@#$%^&*(),.?":{}|<>]/.test(password);

    if (minLength || isNumericOnly || hasNoSpecialChar) {
        let errorMessage = 'Your password must:\n';
        if (minLength) errorMessage += '- Be at least 8 characters long\n';
        if (isNumericOnly) errorMessage += '- Not be entirely numeric\n';
        if (hasNoSpecialChar) errorMessage += '- Include at least one special character (e.g., !@#$%^&*)\n';
        alert(errorMessage);
        event.preventDefault();
        return false;
    }

    return true;
};

// Ensure face is captured (for login)
document.getElementById('login-form')?.onsubmit = function(event) {
    if (!document.getElementById('face_image').value) {
        alert('Please capture your face first!');
        event.preventDefault();
        return false;
    }
    return true;
};

// Cleanup
window.onunload = function() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        cameraStatus.textContent = 'Camera stopped.';
    }
};