/* ============================================
   Sweet House – Chatbot Atención al Cliente
   ============================================ */
(function () {
    'use strict';

    /* ---- Datos del bot ---- */
    const BOT_NAME = 'Dulce Bot <i class="bi bi-cake2-fill"></i>';

    const RESPONSES = {
        welcome: {
            text: '¡Hola! <i class="bi bi-hand-wave-fill"></i> Soy <strong>Dulce Bot</strong>, tu asistente virtual de <strong>Sweet House</strong>. ¿En qué puedo ayudarte hoy?',
            options: ['horarios', 'delivery', 'pagos', 'productos', 'pedidos', 'contacto']
        },

        horarios: {
            text: '<i class="bi bi-clock-fill"></i> <strong>Nuestros horarios de atención son:</strong><br><br>' +
                '<i class="bi bi-calendar-week-fill"></i> <strong>Lunes a Domingo:</strong> 8:00 AM – 8:00 PM<br><br>' +
                '<i class="bi bi-truck"></i> <strong>Domicilios disponibles</strong> durante todo el horario de atención.',
            options: ['delivery', 'pagos', 'productos', 'volver']
        },

        delivery: {
            text: '<i class="bi bi-truck"></i> <strong>Información de delivery:</strong><br><br>' +
                '<i class="bi bi-check-circle-fill"></i> Realizamos entregas a domicilio en toda la ciudad.<br>' +
                '<i class="bi bi-stopwatch-fill"></i> <strong>Tiempo estimado:</strong> 30 – 60 minutos.<br>' +
                '<i class="bi bi-cash-coin"></i> <strong>Costo de envío:</strong> Varía según la zona.<br>' +
                '<i class="bi bi-box-seam-fill"></i> Los pedidos especiales requieren al menos <strong>24 horas de anticipación</strong>.<br><br>' +
                '<i class="bi bi-phone-fill"></i> Coordina tu delivery por WhatsApp para confirmación rápida.',
            options: ['horarios', 'pagos', 'pedidos', 'volver']
        },

        pagos: {
            text: '<i class="bi bi-credit-card-fill"></i> <strong>Métodos de pago aceptados:</strong><br><br>' +
                '<i class="bi bi-cash-stack"></i> Efectivo<br>' +
                '<i class="bi bi-phone-fill"></i> Transferencia bancaria / Pago móvil<br>' +
                '<i class="bi bi-credit-card-2-front-fill"></i> Tarjeta de débito y crédito<br>' +
                '<i class="bi bi-bank"></i> Zelle<br><br>' +
                '<i class="bi bi-shield-lock-fill"></i> Todos los pagos son seguros y confiables.',
            options: ['delivery', 'productos', 'pedidos', 'volver']
        },

        productos: {
            text: '<i class="bi bi-cake2-fill"></i> <strong>Nuestros productos:</strong><br><br>' +
                '<i class="bi bi-gift-fill"></i> Tortas y pasteles personalizados<br>' +
                '<i class="bi bi-cup-hot-fill"></i> Flanes artesanales<br>' +
                '<i class="bi bi-heart-fill"></i> Cupcakes decorados<br>' +
                '<i class="bi bi-grid-fill"></i> Brownies y galletas<br>' +
                '<i class="bi bi-snow2"></i> Pudines y postres fríos<br>' +
                '<i class="bi bi-star-fill"></i> Postres especiales para eventos<br><br>' +
                '<i class="bi bi-list-check"></i> Puedes ver todo nuestro catálogo en la sección <strong>Catálogo</strong> de la página.',
            options: ['horarios', 'pedidos', 'contacto', 'volver']
        },

        pedidos: {
            text: '<i class="bi bi-clipboard2-check-fill"></i> <strong>¿Cómo hacer un pedido?</strong><br><br>' +
                '1. Explora nuestro <strong>Catálogo</strong> y elige tus postres favoritos.<br>' +
                '2. Agrégalos al <strong>carrito de compras</strong>.<br>' +
                '3. Completa tu pedido con tus datos de entrega.<br>' +
                '4. ¡Recibe tu pedido en la puerta de tu casa! <i class="bi bi-house-door-fill"></i><br><br>' +
                '<i class="bi bi-gift-fill"></i> Para tortas personalizadas o pedidos especiales, contáctanos directamente.',
            options: ['delivery', 'pagos', 'contacto', 'volver']
        },

        contacto: {
            text: '<i class="bi bi-telephone-fill"></i> <strong>Contáctanos:</strong><br><br>' +
                '<i class="bi bi-whatsapp"></i> <strong>WhatsApp:</strong> +57 300 000 0000<br>' +
                '<i class="bi bi-envelope-fill"></i> <strong>Email:</strong> contacto@sweethouse.local<br>' +
                '<i class="bi bi-geo-alt-fill"></i> <strong>Ubicación:</strong> Cartagena, Colombia<br><br>' +
                '<i class="bi bi-chat-dots-fill"></i> ¡Responderemos lo antes posible!',
            options: ['horarios', 'productos', 'pedidos', 'volver']
        },

        volver: {
            text: '¿En qué más puedo ayudarte? <i class="bi bi-emoji-smile-fill"></i>',
            options: ['horarios', 'delivery', 'pagos', 'productos', 'pedidos', 'contacto']
        },

        desconocido: {
            text: '<i class="bi bi-question-circle-fill"></i> No estoy seguro de entender tu pregunta. Pero puedo ayudarte con estos temas:',
            options: ['horarios', 'delivery', 'pagos', 'productos', 'pedidos', 'contacto']
        }
    };

    const OPTION_LABELS = {
        horarios: '<i class="bi bi-clock-fill"></i> Horarios',
        delivery: '<i class="bi bi-truck"></i> Delivery',
        pagos: '<i class="bi bi-credit-card-fill"></i> Pagos',
        productos: '<i class="bi bi-cake2-fill"></i> Productos',
        pedidos: '<i class="bi bi-clipboard2-check-fill"></i> Pedidos',
        contacto: '<i class="bi bi-telephone-fill"></i> Contacto',
        volver: '<i class="bi bi-arrow-repeat"></i> Menú principal'
    };

    /* ---- Keyword matching ---- */
    const KEYWORDS = {
        horarios: ['horario', 'hora', 'abierto', 'abren', 'cierran', 'atienden', 'atención', 'atencion', 'abre', 'cierra', 'disponible'],
        delivery: ['delivery', 'envío', 'envio', 'entrega', 'domicilio', 'llevar', 'enviar', 'despacho'],
        pagos: ['pago', 'pagar', 'tarjeta', 'efectivo', 'transferencia', 'zelle', 'precio', 'costo', 'cobran'],
        productos: ['producto', 'postre', 'torta', 'pastel', 'flan', 'brownie', 'cupcake', 'galleta', 'cake', 'catalogo', 'catálogo', 'menu', 'menú'],
        pedidos: ['pedido', 'ordenar', 'orden', 'comprar', 'compra', 'encargar', 'encargo', 'pedir'],
        contacto: ['contacto', 'contactar', 'teléfono', 'telefono', 'whatsapp', 'email', 'correo', 'instagram', 'facebook', 'redes']
    };

    function matchKeyword(text) {
        const lower = text.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
        for (const [key, words] of Object.entries(KEYWORDS)) {
            for (const w of words) {
                const wNorm = w.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
                if (lower.includes(wNorm)) return key;
            }
        }
        return null;
    }

    /* ---- Helpers ---- */
    function el(tag, cls, html) {
        const e = document.createElement(tag);
        if (cls) e.className = cls;
        if (html) e.innerHTML = html;
        return e;
    }

    /* ---- Build DOM ---- */
    function buildChatbot() {
        // Toggle button
        const toggle = el('button', 'chatbot-toggle');
        toggle.id = 'chatbot-toggle';
        toggle.setAttribute('aria-label', 'Abrir chat de atención al cliente');
        toggle.innerHTML = `
      <span class="icon-chat"><i class="bi bi-chat-dots-fill"></i></span>
      <span class="icon-close"><i class="bi bi-x-lg"></i></span>
      <span class="chatbot-badge">1</span>
    `;

        // Window
        const win = el('div', 'chatbot-window');
        win.id = 'chatbot-window';
        win.innerHTML = `
      <div class="chatbot-header">
        <div class="chatbot-avatar"><i class="bi bi-robot"></i></div>
        <div class="chatbot-header-info">
          <h4>${BOT_NAME}</h4>
          <p><span class="chatbot-status-dot"></span>En línea</p>
        </div>
      </div>
      <div class="chatbot-body" id="chatbot-body"></div>
      <div class="chatbot-footer">
        <input type="text" id="chatbot-input" placeholder="Escribe tu mensaje…" autocomplete="off">
        <button id="chatbot-send" aria-label="Enviar mensaje"><i class="bi bi-send-fill"></i></button>
      </div>
    `;

        document.body.appendChild(toggle);
        document.body.appendChild(win);

        return { toggle, win };
    }

    /* ---- App ---- */
    document.addEventListener('DOMContentLoaded', function () {
        const { toggle, win } = buildChatbot();
        const body = document.getElementById('chatbot-body');
        const input = document.getElementById('chatbot-input');
        const sendBtn = document.getElementById('chatbot-send');
        let isOpen = false;
        let greeted = false;

        function toggleChat() {
            isOpen = !isOpen;
            toggle.classList.toggle('open', isOpen);
            win.classList.toggle('open', isOpen);
            if (isOpen) {
                if (!greeted) {
                    greeted = true;
                    showBotResponse('welcome');
                }
                setTimeout(() => input.focus(), 400);
            }
        }

        toggle.addEventListener('click', toggleChat);

        /* ---- Messages ---- */
        function addMsg(html, sender) {
            const msg = el('div', `chat-msg ${sender}`, html);
            body.appendChild(msg);
            scrollDown();
        }

        function scrollDown() {
            requestAnimationFrame(() => {
                body.scrollTop = body.scrollHeight;
            });
        }

        function showTyping() {
            const t = el('div', 'typing-indicator', '<span></span><span></span><span></span>');
            t.id = 'typing';
            body.appendChild(t);
            scrollDown();
        }

        function removeTyping() {
            const t = document.getElementById('typing');
            if (t) t.remove();
        }

        function showOptions(keys) {
            const wrap = el('div', 'chat-options');
            keys.forEach(key => {
                const btn = el('button', 'chat-option-btn', OPTION_LABELS[key] || key);
                btn.addEventListener('click', () => {
                    addMsg(OPTION_LABELS[key] || key, 'user');
                    removeAllOptions();
                    showBotResponse(key);
                });
                wrap.appendChild(btn);
            });
            body.appendChild(wrap);
            scrollDown();
        }

        function removeAllOptions() {
            body.querySelectorAll('.chat-options').forEach(o => o.remove());
        }

        function showBotResponse(key) {
            const data = RESPONSES[key] || RESPONSES.desconocido;
            showTyping();
            const delay = 600 + Math.random() * 400;
            setTimeout(() => {
                removeTyping();
                addMsg(data.text, 'bot');
                if (data.options) {
                    setTimeout(() => showOptions(data.options), 300);
                }
            }, delay);
        }

        /* ---- User input ---- */
        function handleUserInput() {
            const text = input.value.trim();
            if (!text) return;
            addMsg(text, 'user');
            input.value = '';
            removeAllOptions();

            const matched = matchKeyword(text);
            showBotResponse(matched || 'desconocido');
        }

        sendBtn.addEventListener('click', handleUserInput);
        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') handleUserInput();
        });
    });
})();
