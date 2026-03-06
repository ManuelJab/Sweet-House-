document.addEventListener('DOMContentLoaded', function() {
    // Función para crear el botón de toggle
    function createPasswordToggle(passwordInput) {
        // Crear el contenedor
        const container = document.createElement('div');
        container.className = 'password-field-container';
        
        // Mover el input de contraseña dentro del contenedor
        passwordInput.parentNode.insertBefore(container, passwordInput);
        container.appendChild(passwordInput);
        
        // Crear el botón de toggle
        const toggleButton = document.createElement('button');
        toggleButton.type = 'button';
        toggleButton.className = 'password-toggle';
        // Use emoji icons (robust fallback) and set ARIA attributes
        toggleButton.textContent = '👁️';
        toggleButton.setAttribute('title', 'Mostrar contraseña');
        toggleButton.setAttribute('aria-label', 'Mostrar contraseña');
        
        // Agregar el botón después del input
        container.appendChild(toggleButton);
        
        // Agregar el evento click al botón
        toggleButton.addEventListener('click', function(e) {
            e.preventDefault();
            const type = passwordInput.getAttribute('type');
            if (type === 'password') {
                passwordInput.setAttribute('type', 'text');
                // show emoji for hiding
                toggleButton.textContent = '🙈';
                toggleButton.setAttribute('title', 'Ocultar contraseña');
                toggleButton.setAttribute('aria-label', 'Ocultar contraseña');
            } else {
                passwordInput.setAttribute('type', 'password');
                toggleButton.textContent = '👁️';
                toggleButton.setAttribute('title', 'Mostrar contraseña');
                toggleButton.setAttribute('aria-label', 'Mostrar contraseña');
            }
        });
    }

    // Aplicar a todos los campos de contraseña
    document.querySelectorAll('input[type="password"]').forEach(createPasswordToggle);
});